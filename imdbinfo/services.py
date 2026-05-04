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
)
from .aws import AwsSolver

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
        return _waf_cookies          # fast path — already in memory
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
    """
    Defines the valid 'ttype' filters for title searches on IMDb.
    The values correspond to the URL parameter used in search queries.
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
    imdb_id = str(imdb_id)
    num = int(re.sub(r"\D", "", imdb_id))
    lang = _retrieve_url_lang(locale)
    imdb_id = f"{num:07d}"
    return imdb_id, lang


def get_cookies(text , user_agent, force = False):
    solver = AwsSolver(user_agent=user_agent , domain = "www.imdb.com")
    token = solver.solve(text)
    return {
        'aws-waf-token': token,
    }


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
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': f'{USER_AGENT}',
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
    """Fetch movie details from IMDb using the provided IMDb ID as string,
    preserve the 'tt' prefix or not, it will be stripped in the function.
    """
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    url = f"https://www.imdb.com/{lang}/title/tt{imdb_id}/reference"
    logger.info("Fetching movie %s", imdb_id)
    raw_json = request_json_url(url)
    movie = parse_json_movie(raw_json)
    logger.debug("Fetched url %s", url)
    return movie

@lru_cache(maxsize=128)
def search_title(
    search_term: str,
    locale: Optional[str] = None,
    title_type: Optional[TitleFilter] = None,
) -> Optional[SearchResult]:
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

    url = GRAPHQL_URL

    query_template = """query {
  mainSearch(
    first: 50
    options: {
      searchTerm: "__SEARCH_TERM__"
      isExactMatch: false
      type: [TITLE, NAME]
      titleSearchOptions: { type: [__TYPES__] }
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

    query = (query_template.replace("__SEARCH_TERM__", search_term)
            .replace( "__TYPES__", search_options_types))
    payload = {"query": query}
    headers = {"Content-Type": "application/json", "x-imdb-user-country": country_code}

    logger.info("Searching for '%s' using GraphQL API", search_term)
    data = request_graphql_url(
        headers=headers, search_term=search_term, payload=payload, url=url
    )
    result = parse_json_search(data)

    return result


@lru_cache(maxsize=128)
def get_name(person_id: str, locale: Optional[str] = None) -> Optional[PersonDetail]:
    """Fetch person details from IMDb using the provided IMDb ID.
    Preserve the 'nm' prefix or not, it will be stripped in the function.
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
    """Fetch episodes for a movie or series using the provided IMDb ID."""
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    url = f"https://www.imdb.com/{lang}/title/tt{imdb_id}/episodes/?season={season}"
    logger.info("Fetching episodes for movie %s", imdb_id)
    raw_json = request_json_url(url)
    episodes = parse_json_season_episodes(raw_json)
    logger.debug("Fetched %d episodes for movie %s", len(episodes.episodes), imdb_id)
    return episodes


@lru_cache(maxsize=128)
def get_all_episodes(imdb_id: str, locale: Optional[str] = None):
    series_id, lang = normalize_imdb_id(imdb_id, locale)
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
    """wrap until deprecation : use get_season_episodes instead for seasons
    or get_all_episodes for all episodes
    """
    logger.warning(
        "get_episodes is deprecating, use get_season_episodes or get_all_episodes instead."
    )
    return get_season_episodes(imdb_id, season, locale)


def get_akas(imdb_id: str, locale: Optional[str] = None) -> Union[AkasData, list]:
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    raw_json = _get_extended_title_info(imdb_id, lang)
    if not raw_json:
        logger.warning("No AKAs found for title %s", imdb_id)
        return []
    akas = parse_json_akas(raw_json)
    logger.debug("Fetched %d AKAs for title %s", len(akas), imdb_id)
    return akas


def get_all_interests(imdb_id: str, locale: Optional[str] = None):
    """
        Fetch all 'interests' for a title using the provided IMDb ID.

    In the context of IMDb data, 'interests' are thematic tags, topics, or metadata associated with a title,
    such as genres, themes, or other descriptors that go beyond the standard genre classification.
    These interests are extracted from the extended title information returned by IMDb's GraphQL API.

    Note: This function makes an additional request to IMDb's GraphQL endpoint, which may be slower and
    more resource-intensive than standard API calls. Use this function only if you require interests
    beyond what is available in movie.genres, as it can impact performance.
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
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    raw_json = _get_extended_title_info(imdb_id, lang)
    if not raw_json:
        logger.warning("No trivia found for title %s", imdb_id)
        return []
    trivia_list = parse_json_trivia(raw_json)
    logger.debug("Fetched %d trivia items for title %s", len(trivia_list), imdb_id)
    return trivia_list


def get_reviews(imdb_id: str, locale: Optional[str] = None) -> List[Dict]:
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    raw_json = _get_extended_title_info(imdb_id, lang)
    if not raw_json:
        logger.warning("No reviews found for title %s", imdb_id)
        return []
    reviews_list = parse_json_reviews(raw_json)
    logger.debug("Fetched %d reviews for title %s", len(reviews_list), imdb_id)
    return reviews_list


def get_parental_guide(imdb_id: str, locale: Optional[str] = None) -> Dict:
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    raw_json = _get_extended_title_info(imdb_id, lang)
    if not raw_json:
        logger.warning("No parental guide found for title %s", imdb_id)
        return {}
    parental_guide = parse_json_parental_guide(raw_json)
    logger.debug("Fetched parental guide for title %s", imdb_id)
    return parental_guide


def get_filmography(imdb_id,locale: Optional[str] = None) -> dict:
    """
    Fetch full filmography for a person using the provided IMDb ID.
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


def _get_extended_name_info(person_id,  locale=None) -> dict:
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
