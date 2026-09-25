# MIT License
# Copyright (c) 2025 tveronesi+imdbinfo@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import random
import re
from pathlib import Path
from typing import Optional, Dict, Union, List, Tuple, Any
from functools import lru_cache
from time import time
import logging
import niquests
import json
from lxml import html
from enum import Enum
from .locale import _retrieve_url_lang, _get_country_code_from_lang_locale
from .exceptions import HTTPError, WAFError, GraphQLError, ParseError

from .models import (
    SearchResult,
    MovieDetail,
    SeasonEpisodesList,
    PersonDetail,
    AkasData,
    MediaGallery,
    Quote,
    Award,
)
from .parsers import (
    parse_json_movie,
    parse_json_search,
    parse_json_person_detail,
    parse_json_season_episodes,
    parse_json_bulked_episodes,
    parse_json_akas,
    parse_json_trivia,
    parse_json_reviews,
    parse_json_filmography,
    parse_json_parental_guide,
    parse_json_media_gallery,
    parse_json_quotes,
    parse_json_awards,
)
from imdbinfo_aws.aws import AwsSolver

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://api.graphql.imdb.com/"

_WAF_COOKIE_FILE = Path.cwd() / ".cache" / "imdbinfo" / "waf_cookies.json"

# In-memory mirror of the on-disk cookie cache.
# _UNSET  → not yet loaded this process (triggers a one-time file read).
# None    → known to be absent (no file / invalidated).
# dict    → valid cookies ready to use.
_UNSET = object()
_waf_cookies: Any = _UNSET


def _load_waf_cookies() -> Optional[Dict]:
    """Return WAF cookies from the in-memory cache.
    On first call per process the cache is populated from disk (one file read only)."""
    global _waf_cookies
    if _waf_cookies is not _UNSET:
        return _waf_cookies  # fast path — already in memory
    try:
        if _WAF_COOKIE_FILE.exists():
            data = json.loads(_WAF_COOKIE_FILE.read_text(encoding="utf-8"))
            logger.debug("Loaded WAF cookies from %s", _WAF_COOKIE_FILE)
            _waf_cookies = data
            return _waf_cookies
    except Exception as exc:
        logger.debug("Could not load WAF cookies from cache file: %s", exc)
    _waf_cookies = None
    return None


def _save_waf_cookies(cookies: Dict) -> None:
    """Update the in-memory cache and persist to disk."""
    global _waf_cookies
    _waf_cookies = cookies
    try:
        _WAF_COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _WAF_COOKIE_FILE.write_text(json.dumps(cookies), encoding="utf-8")
        logger.debug("Saved WAF cookies to %s", _WAF_COOKIE_FILE)
    except Exception as exc:
        logger.debug("Could not save WAF cookies to cache file: %s", exc)


def _delete_waf_cookie_file() -> None:
    """Clear the in-memory cache and remove the on-disk file."""
    global _waf_cookies
    _waf_cookies = None
    try:
        if _WAF_COOKIE_FILE.exists():
            _WAF_COOKIE_FILE.unlink()
            logger.debug("Deleted WAF cookie cache file %s", _WAF_COOKIE_FILE)
    except Exception as exc:
        logger.debug("Could not delete WAF cookie cache file: %s", exc)


class TitleType(Enum):
    """Enum for filtering titles by type in search queries.

    This enum defines the valid title type filters for IMDb searches.
    Each member corresponds to a specific title category on IMDb.

    Attributes
    ----------
    Movies : str
        Movies (ft / MOVIE). Includes theatrical and made-for-TV movies.
    Series : str
        TV series (tv / TV). Includes serialized television programs.
    Episodes : str
        TV episodes (ep / TV_EPISODE). Individual episodes within a series.
    Shorts : str
        Short films (sh / MOVIE). Works under 40 minutes.
    TvMovie : str
        TV movies (tvm / TV). Films made for television.
    Video : str
        Video releases (v / ALL). Direct-to-video and streaming releases.

    Examples
    --------

    ```python
    >>> from imdbinfo import search_title, TitleType
    >>> # Search for movies only
    >>> results = search_title("The Matrix", title_type=TitleType.Movies)
    ```

    Search for multiple types:

    ```python
    >>> results = search_title(
    ...     "Game of Thrones",
    ...     title_type=(TitleType.Series, TitleType.Episodes)
    ... )
    ```
    """

    Movies = "ft"  # MOVIE
    Series = "tv"  # TV
    Episodes = "ep"  # TV_EPISODE
    Shorts = "sh"  # MOVIE
    TvMovie = "tvm"  # TV
    Video = "v"  # ALL


title_type_search_type = {
    TitleType.Movies: "MOVIE",
    TitleType.Series: "TV",
    TitleType.Episodes: "TV_EPISODE",
    TitleType.Shorts: "MOVIE",
    TitleType.TvMovie: "TV",
    TitleType.Video: "",
}


TitleFilter = Union[TitleType, Tuple[TitleType, ...]]


def normalize_imdb_id(imdb_id: str, locale: Optional[str] = None):
    """Normalize IMDb IDs to a standard 7-digit numeric format.

    Accepts both prefixed (e.g., ``"tt0133093"``) and unprefixed (e.g., ``"0133093"``)
    IMDb IDs and returns a normalized numeric ID and language code.

    Parameters
    ----------
    imdb_id : str
        IMDb ID with or without prefix. E.g. ``"tt0133093"``, ``"0133093"``, ``"nm0000206"``.
        The function strips all non-digit characters and formats the result as a 7-digit ID.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    tuple
        A tuple of (imdb_id_numeric, language_code) where:
        - ``imdb_id_numeric`` is the 7-digit numeric ID (e.g., ``"0133093"``)
        - ``language_code`` is the URL language parameter (e.g., ``""``, ``"it"``, ``"fr"``).
          Empty string for English (default).

    Examples
    --------

    ```python
    >>> normalize_imdb_id("tt0133093")
    ('0133093', '')

    >>> normalize_imdb_id("0133093")
    ('0133093', '')

    >>> normalize_imdb_id("tt0133093", locale="it")
    ('0133093', 'it')
    ```
    """
    imdb_id = str(imdb_id)
    num = int(re.sub(r"\D", "", imdb_id))
    lang = _retrieve_url_lang(locale)
    imdb_id = f"{num:07d}"
    return imdb_id, lang


def get_cookies(text, user_agent, force=False):
    logger.debug("Starting WAF challenge solver...")
    try:
        solver = AwsSolver(user_agent=user_agent, domain="www.imdb.com")
        token = solver.solve(text)
        logger.debug("WAF token successfully obtained")
        return {
            "aws-waf-token": token,
        }
    except Exception as e:
        logger.error("WAF challenge resolution failed: %s", e, exc_info=True)
        raise


def request_json_url(url: str) -> Any:
    resp = request_handler(url)
    if resp.status_code != 200:
        logger.error("Error fetching %s: %s", url, resp.status_code)
        response_text = (resp.text or "")[:500]
        if resp.status_code == 202:
            raise WAFError(
                f"AWS WAF enforcement blocked the request to {url} (HTTP 202). "
                "Try again later, or use a different IP / proxy.",
                status_code=202,
                url=url,
                response_text=response_text,
            )
        raise HTTPError(
            f"Error fetching {url}: HTTP {resp.status_code}",
            status_code=resp.status_code,
            url=url,
            response_text=response_text,
        )

    tree = html.fromstring(resp.content or b"")
    script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script or type(script) is not list:
        logger.error("No script found with id '__NEXT_DATA__'")
        raise ParseError(
            f"No '__NEXT_DATA__' script tag found in the response from {url}",
            url=url,
        )
    raw_json = json.loads(str(script[0]))
    return raw_json


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
HEADERS = {
    "connection": "keep-alive",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "upgrade-insecure-requests": "1",
    "user-agent": f"{USER_AGENT}",
}


def request_handler(url: str) -> Any:
    waf_cookies = _load_waf_cookies()
    resp = niquests.get(url, headers=HEADERS, cookies=waf_cookies)
    if resp.status_code == 200:
        return resp
    # Non-200: invalidate cached cookies and request fresh ones
    logger.debug(
        "Non-200 response (%s) for %s — invalidating cached WAF cookies and refreshing",
        resp.status_code,
        url,
    )
    _delete_waf_cookie_file()
    try:
        waf_cookies = get_cookies(resp.text, USER_AGENT)
        _save_waf_cookies(waf_cookies)
        logger.debug("WAF cookies refreshed — retrying %s", url)
        resp = niquests.get(url, headers=HEADERS, cookies=waf_cookies)
        if resp.status_code != 200:
            logger.warning(
                "Request still non-200 (%s) after WAF cookie refresh for %s — "
                "discarding cookies, will retry fresh on next call",
                resp.status_code,
                url,
            )
            _delete_waf_cookie_file()
    except Exception as waf_exc:
        logger.debug(
            "WAF solver failed, response will be evaluated upstream: %s", waf_exc
        )
        _delete_waf_cookie_file()

    return resp


def request_graphql_url(headers, search_term, payload, url) -> Any:
    # IMDb's GraphQL endpoint returns HTTP 403 without a browser Referer.
    headers = {"Referer": "https://www.imdb.com/", **headers}
    resp = niquests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        logger.error("GraphQL request failed: %s", resp.status_code)
        raise GraphQLError(
            f"GraphQL request failed for {search_term!r}: HTTP {resp.status_code}",
            url=url,
            query_term=search_term,
            status_code=resp.status_code,
            response_text=(resp.text or "")[:500],
        )
    data = resp.json()
    if "errors" in data:
        logger.error("GraphQL error: %s", data["errors"])
        raise GraphQLError(
            f"GraphQL error for {search_term!r}: {data['errors']}",
            url=url,
            query_term=search_term,
            errors=data["errors"],
        )
    return data


@lru_cache(maxsize=128)
def get_movie(imdb_id: str, locale: Optional[str] = None) -> Optional[MovieDetail]:
    """Fetch detailed information for a movie, TV series, or episode.

    Retrieves comprehensive title details including cast, crew, ratings, plot,
    runtime, release dates, and other metadata from IMDb.

    Parameters
    ----------
    imdb_id : str
        IMDb title ID, with or without the ``tt`` prefix. E.g. ``"tt0133093"`` or ``"0133093"``.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    MovieDetail
        A structured response containing title, plot, cast, ratings, runtime, release dates,
        and all available metadata. Check :attr:`~imdbinfo.models.MovieDetail.is_series` or
        :attr:`~imdbinfo.models.MovieDetail.is_episode` to determine the title kind.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    ParseError
        If the HTML response lacks the ``__NEXT_DATA__`` JSON script tag.

    Notes
    -----
    Results are cached with :func:`functools.lru_cache` (maxsize=128).
    To clear the cache, call ``get_movie.cache_clear()``.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_movie
    >>> movie = get_movie("tt0133093")
    >>> print(movie.title)
    The Matrix
    >>> print(movie.rating)
    8.7
    ```

    Fetch a TV series and check its kind:

    ```python
    >>> series = get_movie("tt1520211")
    >>> if series.is_series():
    ...     print(f"Seasons: {series.info_series.display_seasons}")
    ```
    """
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    url = f"https://www.imdb.com/{lang}/title/tt{imdb_id}/reference"
    logger.info("Fetching movie %s", imdb_id)
    raw_json = request_json_url(url)
    movie = parse_json_movie(raw_json)
    logger.debug("Fetched url %s", url)
    return movie


@lru_cache(maxsize=128)
def get_awards(imdb_id: str, locale: Optional[str] = None) -> List[Award]:
    """Fetch awards and nominations for a title.

    Retrieves all award nominations and wins for a movie, TV series, or episode,
    including BAFTA, Golden Globe, Oscars, and other major award ceremonies.

    Parameters
    ----------
    imdb_id : str
        IMDb title ID, with or without the ``tt`` prefix. E.g. ``"tt0133093"`` or ``"0133093"``.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    List[Award]
        List of :class:`~imdbinfo.models.Award` objects, each containing award name,
        nominations, and winners. Empty list if no awards are available.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    ParseError
        If the HTML response lacks the ``__NEXT_DATA__`` JSON script tag.

    Notes
    -----
    Results are cached with :func:`functools.lru_cache` (maxsize=128).

    Examples
    --------

    ```python
    >>> from imdbinfo import get_awards
    >>> awards = get_awards("tt0111161")  # The Shawshank Redemption
    >>> for award in awards:
    ...     print(f"{award.name}: {len(award.nominations)} nominations")
    ```
    """
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    url = f"https://www.imdb.com/{lang}/title/tt{imdb_id}/awards/"
    logger.info("Fetching awards for movie %s", imdb_id)
    raw_json = request_json_url(url)
    awards = parse_json_awards(raw_json)
    logger.debug("Fetched awards for movie %s", imdb_id)
    return awards


@lru_cache(maxsize=128)
def search_title(
    search_term: str,
    year: int | None = None,
    exact_match: bool = False,
    locale: Optional[str] = None,
    title_type: Optional[TitleFilter] = None,
) -> Optional[SearchResult]:
    """Search for movies, TV series, episodes, and people on IMDb.

    Queries IMDb's GraphQL API to find titles and people matching the search term.
    Supports filtering by year, exact match, and title type.

    Parameters
    ----------
    search_term : str
        The search query. E.g. ``"The Matrix"``, ``"Tom Cruise"``.
    year : int, optional
        Filter results to titles released in a specific year.
    exact_match : bool, default False
        If True, match titles exactly by name. If False, allow partial/fuzzy matches.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.
    title_type : TitleType or tuple of TitleType, optional
        Filter by title kind. E.g. ``TitleType.Movies``, ``TitleType.TVSeries``,
        or ``(TitleType.Movies, TitleType.TVSeries)`` for multiple types.
        See :class:`~imdbinfo.services.TitleType` for available filters.

    Returns
    -------
    SearchResult
        A :class:`~imdbinfo.models.SearchResult` containing two lists:
        ``titles`` (matching titles) and ``names`` (matching people).

    Raises
    ------
    GraphQLError
        If the GraphQL API returns an error or non-200 status.

    Notes
    -----
    Results are cached with :func:`functools.lru_cache` (maxsize=128).
    The API returns up to 50 results per query.

    Examples
    --------

    ```python
    >>> from imdbinfo import search_title, TitleType
    >>> results = search_title("The Matrix", year=1999)
    >>> for title in results.titles:
    ...     print(f"{title.imdbId}: {title.title} ({title.year})")
    ```

    Search for movies only with exact match:

    ```python
    >>> movies = search_title(
    ...     "The Matrix",
    ...     year=1999,
    ...     exact_match=True,
    ...     title_type=TitleType.Movies,
    ... )
    >>> print(f"Found {len(movies.titles)} result(s)")
    ```
    """
    lang = _retrieve_url_lang(locale)
    country_code = _get_country_code_from_lang_locale(lang)

    search_options_types = ""
    if title_type:
        tt_iter = title_type if isinstance(title_type, tuple) else (title_type,)
        types = [
            title_type_search_type.get(tt)
            for tt in tt_iter
            if tt is not TitleType.Video
        ]
        search_options_types = ",".join(filter(None, types))

    year_filter = (
        f"""
        releaseDateRange: {{
          start: "{year}-01-01"
          end: "{year}-12-31"
        }}
        """
        if year is not None
        else ""
    )

    query_template = """
query {
  mainSearch(
    first: 50
    options: {
      searchTerm: "__SEARCH_TERM__"
      isExactMatch: __EXACT_MATCH__
      type: [TITLE, NAME]
      titleSearchOptions: {
        type: [__TYPES__]
        __YEAR_FILTER__
      }
    }
  ) {
    edges {
      node {
        entity {
          ... on Title {
            __typename
            id
            titleText { text }
            canonicalUrl
            originalTitleText { text }
            releaseYear{ year }
            releaseDate { year month day }
            primaryImage { url }
            titleType { id text categories { id text value } }
            ratingsSummary { aggregateRating }
            runtime { seconds }
          }
          ... on Name {
            __typename
            id
            nameText { text }
            professions {
              profession { text }
              professionCategory {
                traits
                text { text id }
              }
            }
            knownForV2 {
              credits {
                title {
                  id
                  titleText { text }
                  releaseYear { year }
                }
              }
            }
            canonicalUrl
          }
        }
      }
    }
  }
}"""

    query = (
        query_template
        .replace("__SEARCH_TERM__", search_term)
        .replace("__EXACT_MATCH__", str(exact_match).lower())
        .replace("__TYPES__", search_options_types)
        .replace("__YEAR_FILTER__", year_filter)
    )
    payload = {"query": query}
    headers = {"Content-Type": "application/json", "x-imdb-user-country": country_code}

    logger.info("Searching for '%s' using GraphQL API", search_term)
    data = request_graphql_url(
        headers=headers,
        search_term=search_term,
        payload=payload,
        url=GRAPHQL_URL,
    )
    result = parse_json_search(data)

    return result


@lru_cache(maxsize=128)
def get_name(person_id: str, locale: Optional[str] = None) -> Optional[PersonDetail]:
    """Fetch detailed information for a person (actor, director, writer, etc.).

    Retrieves comprehensive person details including biography, filmography,
    awards, birth/death dates, and career information.

    Parameters
    ----------
    person_id : str
        IMDb person ID, with or without the ``nm`` prefix. E.g. ``"nm0000206"`` or ``"0000206"``.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    PersonDetail
        A structured response containing person name, birth/death dates, biography,
        primary profession, known for titles, and other biographical data.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    ParseError
        If the HTML response lacks the ``__NEXT_DATA__`` JSON script tag.

    Notes
    -----
    Results are cached with :func:`functools.lru_cache` (maxsize=128).
    For full filmography, use :func:`get_filmography` separately.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_name
    >>> person = get_name("nm0000206")  # Keanu Reeves
    >>> print(person.name)
    Keanu Reeves
    >>> print(person.primary_profession)
    actor
    ```
    """
    person_id, lang = normalize_imdb_id(person_id, locale)
    url = f"https://www.imdb.com/{lang}/name/nm{person_id}/"
    t0 = time()
    logger.info("Fetching person %s", person_id)
    raw_json = request_json_url(url)
    t1 = time()
    logger.debug("Fetched person %s in %.2f seconds", person_id, t1 - t0)
    t0 = time()
    person = parse_json_person_detail(raw_json)
    t1 = time()
    logger.debug("Parsed person %s in %.2f seconds", person_id, t1 - t0)
    return person


@lru_cache(maxsize=128)
def get_season_episodes(
    imdb_id: str, season=1, locale: Optional[str] = None
) -> SeasonEpisodesList:
    """Fetch all episodes for a specific season of a TV series.

    Parameters
    ----------
    imdb_id : str
        IMDb title ID, with or without the ``tt`` prefix. E.g. ``"tt1520211"`` or ``"1520211"``.
    season : int, default 1
        Season number to retrieve. E.g. 1 for season 1, 2 for season 2, etc.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    SeasonEpisodesList
        A :class:`~imdbinfo.models.SeasonEpisodesList` containing list of
        :class:`~imdbinfo.models.SeasonEpisode` objects with episode details.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    ParseError
        If the HTML response lacks the ``__NEXT_DATA__`` JSON script tag.

    Notes
    -----
    Results are cached with :func:`functools.lru_cache` (maxsize=128).
    To get all episodes at once, use :func:`get_all_episodes`.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_season_episodes
    >>> episodes = get_season_episodes("tt1520211", season=1)
    >>> for ep in episodes.episodes:
    ...     print(f"S01E{ep.episode:02d}: {ep.title}")
    ```
    """
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    url = f"https://www.imdb.com/{lang}/title/tt{imdb_id}/episodes/?season={season}"
    logger.info("Fetching episodes for movie %s", imdb_id)
    raw_json = request_json_url(url)
    episodes = parse_json_season_episodes(raw_json)
    logger.debug("Fetched %d episodes for movie %s", len(episodes.episodes), imdb_id)
    return episodes


@lru_cache(maxsize=128)
def get_all_episodes(imdb_id: str, locale: Optional[str] = None):
    """Fetch all episodes for a TV series (across all seasons).

    Retrieves the complete episode list for a series in chronological order.

    Parameters
    ----------
    imdb_id : str
        IMDb title ID, with or without the ``tt`` prefix. E.g. ``"tt1520211"`` or ``"1520211"``.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    list
        List of :class:`~imdbinfo.models.BulkedEpisode` objects, each containing
        episode title, number, rating, and other metadata.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    ParseError
        If the HTML response lacks the ``__NEXT_DATA__`` JSON script tag.

    Notes
    -----
    Results are cached with :func:`functools.lru_cache` (maxsize=128).
    For a single season, use :func:`get_season_episodes` instead.
    This function may be slower for long-running series.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_all_episodes
    >>> all_eps = get_all_episodes("tt0944947")  # Game of Thrones
    >>> print(f"Total episodes: {len(all_eps)}")
    ```
    """
    url = f"https://www.imdb.com/{lang}/search/title/?count=250&series=tt{series_id}&sort=release_date,asc"
    logger.info("Fetching bulk episodes for series %s", imdb_id)
    raw_json = request_json_url(url)
    episodes = parse_json_bulked_episodes(raw_json)
    logger.debug("Fetched %d episodes for series %s", len(episodes), imdb_id)
    return episodes


@lru_cache(maxsize=128)
def get_episodes(
    imdb_id: str, season=1, locale: Optional[str] = None
) -> SeasonEpisodesList:
    """Deprecated: Use :func:`get_season_episodes` or :func:`get_all_episodes` instead.

    This function is kept for backward compatibility and forwards calls to
    :func:`get_season_episodes`.

    Parameters
    ----------
    imdb_id : str
        IMDb title ID, with or without the ``tt`` prefix.
    season : int, default 1
        Season number to retrieve.
    locale : str, optional
        Language locale code. Defaults to global locale setting.

    Returns
    -------
    SeasonEpisodesList
        List of episodes for the specified season.

    Warnings
    --------
    This function is deprecated. Use :func:`get_season_episodes` for a single
    season or :func:`get_all_episodes` for all episodes instead.
    """
    logger.warning(
        "get_episodes is deprecating, use get_season_episodes or get_all_episodes instead."
    )
    return get_season_episodes(imdb_id, season, locale)


def get_akas(imdb_id: str, locale: Optional[str] = None) -> Union[AkasData, list]:
    """Fetch alternative titles (AKAs) for a title in different regions and languages.

    Retrieves all known alternative titles and regional releases for a title,
    along with country and language codes.

    Parameters
    ----------
    imdb_id : str
        IMDb title ID, with or without the ``tt`` prefix. E.g. ``"tt0133093"`` or ``"0133093"``.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    AkasData or list
        A :class:`~imdbinfo.models.AkasData` object or empty list if no AKAs are found.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    ParseError
        If the HTML response lacks the ``__NEXT_DATA__`` JSON script tag.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_akas
    >>> akas = get_akas("tt0133093")  # The Matrix
    >>> for aka in akas:
    ...     print(f"{aka.title} ({aka.country_code})")
    ```
    """
    raw_json = _get_extended_title_info(imdb_id, lang)
    if not raw_json:
        logger.warning("No AKAs found for title %s", imdb_id)
        return []
    akas = parse_json_akas(raw_json)
    logger.debug("Fetched %d AKAs for title %s", len(akas), imdb_id)
    return akas


def get_all_interests(imdb_id: str, locale: Optional[str] = None):
    """Fetch all interest tags and thematic topics for a title.

    In the context of IMDb data, 'interests' are thematic tags, topics, or metadata
    associated with a title, such as genres, themes, or other descriptors beyond
    the standard genre classification. These are extracted from IMDb's GraphQL API.

    Parameters
    ----------
    imdb_id : str
        IMDb title ID, with or without the ``tt`` prefix. E.g. ``"tt0133093"`` or ``"0133093"``.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    list
        List of interest tag strings. Empty list if no interests are found.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    GraphQLError
        If the GraphQL endpoint returns an error.

    Notes
    -----
    This function makes an additional request to IMDb's GraphQL endpoint, which
    may be slower and more resource-intensive than standard API calls. Use this
    function only if you require interests beyond what is available in
    :attr:`~imdbinfo.models.MovieDetail.genres`.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_all_interests
    >>> interests = get_all_interests("tt0133093")  # The Matrix
    >>> print(interests[:5])
    ['cyberpunk', 'hacker', 'action', ...]
    ```
    """
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    raw_json = _get_extended_title_info(imdb_id, lang)
    if not raw_json:
        logger.warning("No interests found for title %s", imdb_id)
        return []
    interests = []
    interests_edges = raw_json.get("interests", {}).get("edges", [])
    for edge in interests_edges:
        node = edge.get("node", {})
        primary_text = node.get("primaryText", {}).get("text", "")
        if primary_text:
            interests.append(primary_text)
    logger.debug("Fetched %d interests for title %s", len(interests), imdb_id)
    return interests


def get_trivia(imdb_id: str, locale: Optional[str] = None) -> List[Dict]:
    """Fetch trivia facts for a title.

    Retrieves interesting behind-the-scenes facts, production trivia, and
    user-contributed trivia about a movie or TV series.

    Parameters
    ----------
    imdb_id : str
        IMDb title ID, with or without the ``tt`` prefix. E.g. ``"tt0133093"`` or ``"0133093"``.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    List[Dict]
        List of trivia dictionaries containing trivia text and interest scores.
        Empty list if no trivia is found.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    GraphQLError
        If the GraphQL endpoint returns an error.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_trivia
    >>> trivia = get_trivia("tt0111161")  # The Shawshank Redemption
    >>> print(f"Found {len(trivia)} trivia facts")
    ```
    """
    raw_json = _get_extended_title_info(imdb_id, lang)
    if not raw_json:
        logger.warning("No trivia found for title %s", imdb_id)
        return []
    trivia_list = parse_json_trivia(raw_json)
    logger.debug("Fetched %d trivia items for title %s", len(trivia_list), imdb_id)
    return trivia_list


def get_reviews(imdb_id: str, locale: Optional[str] = None) -> List[Dict]:
    """Fetch user reviews for a title.

    Retrieves top user reviews and comments about a movie or TV series,
    including reviewer names, ratings, and spoiler flags.

    Parameters
    ----------
    imdb_id : str
        IMDb title ID, with or without the ``tt`` prefix. E.g. ``"tt0133093"`` or ``"0133093"``.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    List[Dict]
        List of review dictionaries containing reviewer name, rating, text, and
        spoiler flag. Empty list if no reviews are found.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    GraphQLError
        If the GraphQL endpoint returns an error.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_reviews
    >>> reviews = get_reviews("tt0111161")
    >>> for review in reviews:
    ...     print(f"By {review['author']}: {review['summary']}")
    ```
    """
    raw_json = _get_extended_title_info(imdb_id, lang)
    if not raw_json:
        logger.warning("No reviews found for title %s", imdb_id)
        return []
    reviews_list = parse_json_reviews(raw_json)
    logger.debug("Fetched %d reviews for title %s", len(reviews_list), imdb_id)
    return reviews_list


def get_parental_guide(imdb_id: str, locale: Optional[str] = None) -> Dict:
    """Fetch parental guide information for a title.

    Retrieves content warnings for violence, profanity, sex, drugs, and other
    categories to help parents assess title suitability.

    Parameters
    ----------
    imdb_id : str
        IMDb title ID, with or without the ``tt`` prefix. E.g. ``"tt0133093"`` or ``"0133093"``.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    Dict
        A :class:`~imdbinfo.models.ParentalGuideList` object or dict with categories
        and content warnings. Empty dict if no parental guide is found.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    GraphQLError
        If the GraphQL endpoint returns an error.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_parental_guide
    >>> guide = get_parental_guide("tt0137523")  # Fight Club
    >>> for category in guide.get('categories', []):
    ...     print(f"{category['name']}: {category['severity']}")
    ```
    """
    raw_json = _get_extended_title_info(imdb_id, lang)
    if not raw_json:
        logger.warning("No parental guide found for title %s", imdb_id)
        return {}
    parental_guide = parse_json_parental_guide(raw_json)
    logger.debug("Fetched parental guide for title %s", imdb_id)
    return parental_guide


def get_quotes(imdb_id: str, locale: Optional[str] = None) -> List[Quote]:
    """Fetch character quotes and dialogue from a title.

    Returns a list of memorable movie or TV quotes, including speaker attribution,
    dialogue lines, and community interest scores.

    Parameters
    ----------
    imdb_id : str
        IMDb title ID, with or without the ``tt`` prefix. E.g. ``"tt0133093"`` or ``"0133093"``.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    List[Quote]
        List of :class:`~imdbinfo.models.Quote` objects, each containing dialogue lines,
        speaker attribution, and interest scores. Empty list if no quotes are found.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    GraphQLError
        If the GraphQL endpoint returns an error.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_quotes
    >>> quotes = get_quotes("tt0133093")  # The Matrix
    >>> for quote in quotes:
    ...     print(f"{quote.characters[0].character}: {quote.lines[0].text}")
    ```
    """
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    raw_json = _get_extended_title_info(imdb_id, lang)
    if not raw_json:
        logger.warning("No quotes found for title %s", imdb_id)
        return []
    parsed_quotes = parse_json_quotes(raw_json)
    logger.debug("Fetched %d quotes for title %s", len(parsed_quotes), imdb_id)
    return parsed_quotes


def get_filmography(imdb_id, locale: Optional[str] = None) -> dict:
    """Fetch complete filmography for a person.

    Retrieves all known credits for an actor, director, writer, composer, or other
    professional, organized by job category.

    Parameters
    ----------
    imdb_id : str
        IMDb person ID, with or without the ``nm`` prefix. E.g. ``"nm0000206"`` or ``"0000206"``.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    dict
        Dictionary with filmography organized by category (actor, director, writer, etc.),
        containing all known credits. Empty dict if no filmography is found.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    GraphQLError
        If the GraphQL endpoint returns an error.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_filmography
    >>> filmography = get_filmography("nm0000206")  # Keanu Reeves
    >>> print(f"Acting credits: {len(filmography.get('actor', []))}")
    ```
    """
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    raw_json = _get_extended_name_info(imdb_id, lang)
    if not raw_json:
        logger.warning("No full_credit found for name %s", imdb_id)
        return {}
    full_credits_list = parse_json_filmography(raw_json)
    logger.debug("Fetched full_credits for name %s", imdb_id)
    return full_credits_list


@lru_cache(maxsize=128)
def _get_extended_title_info(imdb_id, locale=None) -> dict:
    """
    Fetch extended info using IMDb's GraphQL API:
    including akas, trivia, reviews, interests, and parental guide.
    """
    imdbId = "tt" + imdb_id
    country = _get_country_code_from_lang_locale(locale)
    url = GRAPHQL_URL
    headers = {
        "Content-Type": "application/json",
        "x-imdb-user-country": country,
    }
    query = (
        """
        query {
          title(id: "%s") {
            id
            titleText {
              text
            }
            originalTitle: originalTitleText {
              text
            }
            images(first: 50) {
              total
              pageInfo {
                endCursor
                hasNextPage
                hasPreviousPage
                startCursor
              }
              edges {
                position
                cursor
                node {
                  id
                  url
                  height
                  width
                  caption {
                    plainText
                  }
                  type
                  copyright
                  createdBy
                  source {
                    id
                    text
                    attributionUrl
                  }
                  names {
                    id
                    nameText {
                      text
                    }
                  }
                  titles {
                    id
                    titleText {
                      text
                    }
                  }
                }
              }
            }
            interests(first: 20) {
              edges {
                node {
                  primaryText {
                    text
                  }
                }
              }
            }
            akas(first: 200) {
              edges {
                node {
                  country {
                    name: text
                    code: id
                  }
                  language {
                    name: text
                    code: id
                  }
                  title: text
                }
              }
            }
            trivia(first: 50) {
              edges {
                node {
                  id
                  displayableArticle {
                    body {
                      plaidHtml
                    }
                  }
                  interestScore {
                    usersVoted
                    usersInterested
                  }
                }
              }
            }
            reviews(first: 50) {
              edges {
                node {
                  id
                  spoiler
                  author {
                    nickName
                  }
                  summary {
                    originalText
                  }
                  text {
                    originalText {
                      plaidHtml
                    }
                  }
                  authorRating
                  submissionDate
                  helpfulness {
                    upVotes
                    downVotes
                  }
                  __typename
                }
              }
            }
             parentsGuide {
                  categories {
                    category {
                      id
                      text
                    }
                    guideItems(first: 10) {
                      edges {
                        node {
                          isSpoiler
                          text {
                            plaidHtml
                          }
                        }
                      }
                    }
                    severity{id,votedFor}
                    severityBreakdown {
                      votedFor
                      voteType
                    }
                  }
                }
                    quotes(first: 100) {
              edges {
                node {
                  id
                  lines {
                    characters {
                      character
                    name { id }
                    }
                    text
                    stageDirection
                  }
                  interestScore {
                    usersInterested
                    usersVoted
                  }
                }
              }
            }
          }
        }
        """
        % imdbId
    )
    payload = {"query": query}
    logger.info("Fetching title %s from GraphQL API", imdb_id)
    data = request_graphql_url(headers, imdbId, payload, url)
    raw_json = data.get("data", {}).get("title", {})
    return raw_json


def _get_extended_name_info(person_id, locale=None) -> dict:
    """
    Fetch extended person info using IMDb's GraphQL API.
    """
    person_id = "nm" + person_id
    country = _get_country_code_from_lang_locale(locale)

    query = (
        """
            query {
              name(id: "%s") {
                nameText {
                  text
                }

                credits(first: 250
                filter: {
            categories: [
              "production_designer"
              "casting_department"
              "director"
              "composer"
              "casting_director"
              "executive"
              "art_director"
              "actress"
              "costume_designer"
              "writer"
              "camera_department"
              "art_department"
              "publicist"
              "cinematographer"
              "location_management"
              "soundtrack"
              "sound_department"
              "talent_agent"
              "set_decorator"
              "animation_department"
              "make_up_department"
              "costume_department"
              "script_department"
              "producer"
              "stunts"
              "editor"
              "stunt_coordinator"
              "special_effects"
              "assistant_director"
              "editorial_department"
              "music_department"
              "transportation_department"
              "actor"
              "visual_effects"
              "production_manager"
              "production_designer"
              "casting_department"
              "director"
              "composer"
              "archive_sound"
              "casting_director"
              "art_director"
            ]
          }
                )

                {
                  edges {
                    node {
                      category {
                        id
                      }

                      title {
                        id
                        ratingsSummary{aggregateRating}
                        primaryImage {
                          url
                        }
                        #certificate {rating}
                        originalTitleText {
                          text
                        }
                        titleText {
                          text
                        }
                        titleType {
                          #text
                          id
                        }
                        releaseYear {
                          year
                        }
                      }
                    }
                  }

                  pageInfo {
                    endCursor
                    hasNextPage
                  }
                }
              }
            }

        """
        % person_id
    )
    url = GRAPHQL_URL
    headers = {
        "Content-Type": "application/json",
        "x-imdb-user-country": country,
    }
    payload = {"query": query}
    logger.info("Fetching person %s from GraphQL API", person_id)
    data = request_graphql_url(headers, person_id, payload, url)
    raw_json = data.get("data", {}).get("name", {})
    return raw_json


@lru_cache(maxsize=128)
def get_media_gallery(
    imdb_id: str,
    locale: Optional[str] = None,
) -> Optional[MediaGallery]:
    """Fetch media gallery (images and videos) for a title.

    Retrieves all available images, promotional photos, and behind-the-scenes
    media for a movie or TV series.

    Parameters
    ----------
    imdb_id : str
        IMDb title ID, with or without the ``tt`` prefix. E.g. ``"tt0133093"`` or ``"0133093"``.
    locale : str, optional
        Language locale code. Defaults to global locale setting (see :func:`set_locale`).
        Supported: ``"en"``, ``"it"``, ``"fr"``, ``"es"``, ``"de"``, ``"pt"``, ``"hi"``, ``"fr-ca"``, ``"es-es"``.

    Returns
    -------
    MediaGallery or list
        A :class:`~imdbinfo.models.MediaGallery` object containing images with URLs,
        captions, and metadata. Empty list if no media is found.

    Raises
    ------
    HTTPError
        If IMDb returns a non-200 HTTP status.
    WAFError
        If AWS WAF blocks the request (HTTP 202). Retry later or use a different IP/proxy.
    GraphQLError
        If the GraphQL endpoint returns an error.

    Notes
    -----
    Results are cached with :func:`functools.lru_cache` (maxsize=128).

    Examples
    --------

    ```python
    >>> from imdbinfo import get_media_gallery
    >>> media = get_media_gallery("tt0111161")  # The Shawshank Redemption
    >>> print(f"Found {len(media or [])} media items")
    ```
    """
    raw_json = _get_extended_title_info(imdb_id, lang)
    if not raw_json:
        logger.warning("No media_gallery found for title %s", imdb_id)
        return []
    media_gallery = parse_json_media_gallery(raw_json)
    logger.debug(
        "Fetched %d media_gallery for title %s", len(media_gallery or []), imdb_id
    )
    return media_gallery
