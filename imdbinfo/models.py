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

"""Pydantic models for imdbinfo API responses.

This module contains all data models used to represent IMDb entities such as
movies, TV series, people, episodes, awards, and metadata. All models are built
with Pydantic for type safety, validation, and IDE autocompletion.

Model Hierarchy
---------------

**Title Models:**
- :class:`MovieDetail` — Main response for titles (movies, series, episodes)
- :class:`TvSeriesDetail` — Series-specific metadata
- :class:`TvEpisodeDetail` — Episode-specific metadata
- :class:`MovieBriefInfo` — Lightweight title metadata for search results

**Person Models:**
- :class:`Person` — Basic person info (directors, cast, crew)
- :class:`PersonDetail` — Comprehensive person biography and filmography

**Search & Results:**
- :class:`SearchResult` — Combined search results (titles + people)

**Metadata Models:**
- :class:`Award` — Award and nominations data
- :class:`Quote` — Character quotes and dialogue
- :class:`AkaInfo` / :class:`AkasData` — Alternative titles by region
- :class:`MediaGallery` — Images and media items
- :class:`ParentalGuideList` — Content warnings and ratings

**Episode Collections:**
- :class:`SeasonEpisodesList` — Episodes grouped by season
- :class:`BulkedEpisode` — Individual episode in bulk results
"""

from typing import Optional, List, Dict, Tuple, Union
from pydantic import BaseModel, Field, field_validator
import logging

from .transformers import _release_date

EPISODE_IDENTIFIERS = ("tvEpisode", "podcastEpisode")

SERIES_IDENTIFIERS = ("tvSeries", "tvMiniSeries", "podcastSeries")

logger = logging.getLogger(__name__)


class Person(BaseModel):
    """Basic information about a person (actor, director, writer, etc.).

    This model represents individuals in the IMDb database with their core
    identifying information. It's used for cast, crew, and search results.

    Attributes
    ----------
    id : str
        IMDb ID without prefix (e.g., ``"0000206"`` for Keanu Reeves).
    imdb_id : str
        IMDb ID without prefix. Same as ``id``.
    imdbId : str
        IMDb ID with ``nm`` prefix (e.g., ``"nm0000206"``).
    name : str
        Person's full name.
    url : str
        IMDb profile URL.
    job : str, optional
        Job title or role (e.g., ``"Director"``, ``"Actor"``, ``"Writer"``).
    """

    id: str
    imdb_id: str
    imdbId: str
    name: str
    url: str
    job: Optional[str] = None

    @classmethod
    def from_directors(cls, data: dict):
        if isinstance(data, dict) and "node" in data:
            data = data["node"]
        return cls(
            name=data["name"]["nameText"]["text"],
            imdb_id=data["name"]["id"].replace("nm", ""),
            id=data["name"]["id"].replace("nm", ""),
            imdbId=data["name"]["id"],
            url=f"https://www.imdb.com/name/{data['name']['id']}",
            job="Director",
        )

    @classmethod
    def from_creators(cls, data: dict):
        return cls(
            name=data["name"]["nameText"]["text"],
            imdb_id=data["name"]["id"].replace("nm", ""),
            id=data["name"]["id"].replace("nm", ""),
            imdbId=data["name"]["id"],
            url=f"https://www.imdb.com/name/{data['name']['id']}",
            job="Creator",
        )

    @classmethod
    def from_cast(cls, data: dict):
        return cls(
            name=data["name"]["nameText"]["text"],
            imdb_id=data["name"]["id"].replace("nm", ""),
            id=data["name"]["id"].replace("nm", ""),
            imdbId=data["name"]["id"],
            url=f"https://www.imdb.com/name/{data['name']['id']}",
            job="Cast",
        )

    @classmethod
    def from_search(cls, data: dict):
        professions = data.get("professions", [])
        prof = ",".join(
            [
                p.get("profession", {}).get("text", "")
                for p in professions
                if p.get("profession", {}).get("text")
            ]
        )

        return cls(
            name=data["nameText"]["text"],
            imdb_id=data["id"].replace("nm", ""),
            id=data["id"].replace("nm", ""),  # id without 'nm' prefix, e.g. '0000126'
            imdbId=data["id"],
            url=f"https://www.imdb.com/name/{data['id']}",
            job=prof,
        )

    @classmethod
    def from_category(cls, data: dict):
        return cls(
            name=data["rowTitle"],
            imdb_id=data["id"].replace("nm", ""),
            id=data["id"].replace("nm", ""),  # id without 'nm' prefix, e.g. '0000126'
            imdbId=data["id"],  # same as id without 'nm' prefix
            url=f"https://www.imdb.com/name/{data['id']}",
            job=str(data.get("jobTitle", "")),
        )

    def __str__(self):
        return f"{self.name} ({self.job})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name} - {self.job})"


class SeriesMixin:
    """Mixin to provide type-checking methods for title entities.

    Methods
    -------
    is_series() -> bool
        Check if the title is a TV series (not a movie or episode).
    is_episode() -> bool
        Check if the title is a TV episode (part of a series).
    """

    def is_series(self) -> bool:
        """Check if this title is a TV series (main series reference).

        Returns
        -------
        bool
            True if the title is a TV series, False otherwise.
            If True, series details can be found in the ``info_series`` property.
        """
        return getattr(self, "kind", None) in SERIES_IDENTIFIERS

    def is_episode(self) -> bool:
        """Check if this title is a TV episode (part of a series).

        Returns
        -------
        bool
            True if the title is an episode, False otherwise.
            If True, episode details can be found in the ``info_episode`` property.
        """
        return getattr(self, "kind", None) in EPISODE_IDENTIFIERS


class InfoSeries(BaseModel):
    """Metadata about a TV series (years, seasons, creators).

    Attributes
    ----------
    display_years : List[str]
        Year range for the series (e.g., ``["2013", "2017"]`` for 2013-2017).
        Empty list if not available.
    display_seasons : List[str]
        List of season numbers as strings (e.g., ``["1", "2", "3"]``).
        Empty list if not available.
    creators : List[Person]
        List of series creators. Empty list if not available.
    """

    display_years: List[str] = Field(default_factory=list)
    display_seasons: List[str] = Field(default_factory=list)
    creators: List[Person] = Field(default_factory=list)

    @field_validator("display_years", mode="before")
    def filter_years(cls, value):
        if value is None:
            return []
        return [
            str(y) for y in value if isinstance(y, str) and len(y) == 4 and y.isdigit()
        ]

    def get_creators(self) -> List[Person]:
        """Get the list of series creators.

        Returns
        -------
        List[Person]
            Series creators, or empty list if none are available.
        """
        return self.creators or []

    def __str__(self):
        return f"Years: {self.display_years[-1] if self.display_years else ''}-{self.display_years[0] if self.display_years else ''}, Seasons: {len(self.display_seasons)}"


class InfoEpisode(BaseModel):
    """Metadata about a specific TV episode.

    Attributes
    ----------
    season_n : int, optional
        Season number (1-indexed).
    episode_n : int, optional
        Episode number within the season (1-indexed).
    series_imdbId : str, optional
        IMDb ID of the parent series (with ``tt`` prefix).
    series_title : str, optional
        Title of the parent series in original language.
    series_title_localized : str, optional
        Title of the parent series in the requested locale.
    """

    season_n: Optional[int] = None
    episode_n: Optional[int] = None
    series_imdbId: Optional[str] = None
    series_title: Optional[str] = None
    series_title_localized: Optional[str] = None

    def __str__(self):
        # print in S01E01 format
        season_str = f"S{self.season_n:02d}" if self.season_n is not None else "S??"
        episode_str = f"E{self.episode_n:02d}" if self.episode_n is not None else "E??"
        return f"{self.series_title} - {season_str}{episode_str} ({self.series_imdbId})"


class CastMember(Person):
    """Cast member model for cast members in a movie.
    This model extends the Person model to include additional information specific to cast members.
    It includes the characters they played in the movie and their picture URL.
    """

    characters: List[str] = Field(default_factory=list)
    picture_url: Optional[str] = None
    attributes: Optional[str] = None  # e.g. '(as John Doe)'

    @classmethod
    def from_cast(cls, data: dict):
        return cls(
            name=data["rowTitle"],
            imdb_id=data["id"].replace("nm", ""),
            id=data["id"].replace("nm", ""),  # id without 'nm' prefix, e.g. '0000126'
            imdbId=data["id"],  #  with 'nm' prefix e.g. 'nm0000126'
            url=f"https://www.imdb.com/name/{data['id']}",
            job="Cast",
            characters=data.get("characters", []),
            picture_url=data.get("imageProps", {})
            .get("imageModel", {})
            .get("url", None),
            attributes=data.get("attributes", ""),
        )

    def __str__(self):
        return f"{self.name} ({', '.join(self.characters)})"


class CompanyInfo(BaseModel):
    """
    CompanyInfo model for production companies and other companies involved in a movie.
    This model contains basic information about a company such as name, id, imdb_id, imdbId, url, attributes and countries.
    """

    id: str  # id without 'co' prefix, e.g. '0133093', same as imdb_id
    imdb_id: str  # id without 'co' prefix, e.g. '0133093'
    imdbId: str  # id with 'co' prefix, e.g. 'co0133093'
    name: str
    url: str
    attributes: Optional[List[str]] = None
    countries: Optional[List[str]] = None

    def __str__(self):
        return f"{self.name} ({self.imdbId})"


class AwardInfo(BaseModel):
    """Summary of award wins and nominations for a title.

    Attributes
    ----------
    wins : int, optional
        Total number of award wins.
    nominations : int, optional
        Total number of award nominations.
    prestigious_award : dict, optional
        Details of the most prestigious award, if any.
    """

    wins: Optional[int] = None
    nominations: Optional[int] = None
    prestigious_award: Optional[dict] = None


class Award(BaseModel):
    """A movie or TV series award, nomination, or win.

    Represents a single award entry as listed on IMDb's awards page for a title.
    Returned by :func:`~imdbinfo.services.get_awards`.

    Attributes
    ----------
    event : str
        Award ceremony name (e.g., ``"Academy Awards, USA"``, ``"Golden Globe Awards"``).
    status : str, optional
        Award status/year (e.g., ``"2000 Winner"``, ``"Nominee"``).
    award : str, optional
        Award name (e.g., ``"Oscar"``, ``"BAFTA Award"``).
    category : str, optional
        Award category (e.g., ``"Best Picture"``, ``"Best Director"``).
    nominees : str, optional
        Nominees or honorees associated with this award.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_awards
    >>> awards = get_awards("tt0111161")  # The Shawshank Redemption
    >>> for award in awards[:3]:
    ...     print(f"{award.event}: {award.award} ({award.category})")
    ...     print(f"  Status: {award.status}")
    ```
    """

    event: str = ""
    status: Optional[str] = None
    award: Optional[str] = None
    category: Optional[str] = None
    nominees: Optional[str] = None

    def __str__(self):
        parts = []
        if self.event:
            parts.append(self.event)
        if self.status:
            parts.append(self.status)
        if self.award:
            parts.append(self.award)
        if self.category:
            parts.append(self.category)
        if self.nominees:
            parts.append(f"({self.nominees})")
        return " - ".join(parts)

    def __repr__(self):
        return f"Award(event={self.event!r}, status={self.status!r}, award={self.award!r}, category={self.category!r})"


class MovieDetail(SeriesMixin, BaseModel):
    """Comprehensive details for a movie, TV series, or episode.

    This is the main response model returned by :func:`~imdbinfo.services.get_movie`.
    It contains all available IMDb metadata for a title including basic info, cast, crew,
    ratings, release information, production details, and technical specifications.

    Use :meth:`is_series` and :meth:`is_episode` to determine the title type before
    accessing type-specific fields like ``info_series`` or ``info_episode``.

    Attributes
    ----------
    id : str
        IMDb title ID without ``tt`` prefix (e.g., ``"0133093"``).
    imdb_id : str
        IMDb title ID without ``tt`` prefix. Same as ``id``.
    imdbId : str
        IMDb title ID with ``tt`` prefix (e.g., ``"tt0133093"``).
    title : str
        Primary title in original language.
    title_localized : str, optional
        Title in the requested locale language.
    title_akas : List[str]
        Alternative titles by region and language.
    kind : str, optional
        Title type (``"movie"``, ``"tvSeries"``, ``"tvEpisode"``, etc.).
    url : str
        IMDb title URL.
    cover_url : str, optional
        URL of the primary poster/cover image.
    plot : str, optional
        Plot summary or synopsis.
    release_date : str, optional
        Release date in ISO format (``YYYY-MM-DD``).
    languages : List[str]
        List of language codes (e.g., ``["en", "fr"]``).
    certificates : Dict[str, Tuple[str, str]]
        Parental ratings by country (e.g., ``{"US": ("PG-13", "description")}``)
    directors : List[Person]
        List of film directors.
    stars : List[Person]
        List of main cast members.
    year : int, optional
        Release year.
    year_end : int, optional
        End year (for TV series).
    duration : int, optional
        Runtime in minutes.
    rating : float, optional
        IMDb rating (0-10).
    votes : int, optional
        Number of user votes.
    info_series : InfoSeries, optional
        Series-specific metadata. Present only if ``is_series()`` returns ``True``.
    info_episode : InfoEpisode, optional
        Episode-specific metadata. Present only if ``is_episode()`` returns ``True``.
    """

    id: str  # id without 'tt' prefix, e.g. '0133093', same as imdb_id
    imdb_id: str  # id without 'tt' prefix, e.g. '0133093'
    imdbId: str  # id with 'tt' prefix, e.g. 'tt0133093'
    title: str
    title_localized: Optional[str] = None
    title_akas: List[str] = Field(default_factory=list)
    kind: Optional[str] = None
    url: str = ""
    cover_url: Optional[str] = None
    plot: Optional[str] = None
    release_date: Optional[str] = None
    languages: List[str] = Field(default_factory=list)
    languages_text: List[str] = Field(default_factory=list)
    certificates: Dict[str, Tuple[str, str]] = Field(default_factory=dict)
    mpaa: Optional[str] = None
    directors: List[Person] = Field(default_factory=list)
    stars: List[Person] = Field(default_factory=list)
    year: Optional[int] = None
    year_end: Optional[int] = None
    duration: Optional[int] = None
    country_codes: List[str] = Field(default_factory=list)
    countries: List[str] = Field(default_factory=list)
    rating: Optional[float] = None
    metacritic_rating: Optional[int] = None
    votes: Optional[int] = None
    awards: Optional[AwardInfo] = None
    trailers: List[str] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    worldwide_gross: Optional[str] = None
    production_budget: Optional[str] = None
    storyline_keywords: List[str] = Field(default_factory=list)
    filming_locations: List[str] = Field(default_factory=list)
    sound_mixes: List[str] = Field(default_factory=list)
    processes: List[str] = Field(default_factory=list)
    printed_formats: List[str] = Field(default_factory=list)
    negative_formats: List[str] = Field(default_factory=list)
    laboratories: List[str] = Field(default_factory=list)
    colorations: List[str] = Field(default_factory=list)
    cameras: List[str] = Field(default_factory=list)
    aspect_ratios: List[Tuple[Optional[str], Optional[str]]] = Field(
        default_factory=list
    )
    summaries: List[str] = Field(default_factory=list)
    synopses: List[str] = Field(default_factory=list)
    production: List[str] = Field(default_factory=list)
    categories: Dict[str, List[Union[Person, CastMember]]] = Field(default_factory=dict)
    company_credits: Dict[str, List[CompanyInfo]] = Field(default_factory=dict)

    @field_validator(
        "languages",
        "country_codes",
        "genres",
        "languages_text",
        "countries",
        mode="before",
    )
    def none_is_list(cls, value):
        if value is None:
            return []
        return value

    def __str__(self):
        return f"{self.title} ({self.year}) - {self.imdbId} ({self.kind})"


class TvSeriesDetail(MovieDetail):
    """Details for a TV series (inherits from MovieDetail).

    Contains series-specific metadata such as creators, seasons, and year range.

    Attributes
    ----------
    info_series : InfoSeries, optional
        Series metadata including display years, seasons, and creators.
    """

    info_series: Optional[InfoSeries] = Field(
        None, description="Series metadata (years, seasons, creators)"
    )


class TvEpisodeDetail(MovieDetail):
    """Details for a TV episode (inherits from MovieDetail).

    Contains episode-specific metadata such as season number, episode number,
    and parent series information.

    Attributes
    ----------
    info_episode : InfoEpisode, optional
        Episode metadata including season, episode number, and series reference.
    """

    info_episode: Optional[InfoEpisode] = Field(
        None, description="Episode metadata (season, episode, series)"
    )


class MovieBriefInfo(SeriesMixin, BaseModel):
    """Lightweight title metadata for search results and filmography.

    Used in search results and as part of a person's filmography.
    Contains basic title info: name, year, rating, and IMDb ID.

    Attributes
    ----------
    id : str
        IMDb title ID without ``tt`` prefix (e.g., ``"0133093"``).
    imdb_id : str
        IMDb title ID without ``tt`` prefix. Same as ``id``.
    imdbId : str
        IMDb title ID with ``tt`` prefix (e.g., ``"tt0133093"``).
    title : str
        Title in original language.
    title_localized : str
        Title in the requested locale.
    cover_url : str, optional
        URL of the poster image.
    url : str, optional
        IMDb title URL.
    year : int, optional
        Release year.
    kind : str, optional
        Title type (``"movie"``, ``"tvSeries"``, ``"tvEpisode"``, etc.).
    rating : float, optional
        IMDb rating (0-10).
    """

    id: str
    imdb_id: str
    imdbId: str
    title: str
    title_localized: str
    cover_url: Optional[str] = None
    url: Optional[str] = None
    year: Optional[int] = None
    kind: Optional[str] = None
    rating: Optional[float] = None

    @classmethod
    def from_movie_search(cls, data: dict):
        # safely extract nested structures (preserve original behavior of returning None when missing)
        release = data.get("releaseYear")
        year = release.get("year") if isinstance(release, dict) else None

        primary = data.get("primaryImage")
        cover_url = primary.get("url") if isinstance(primary, dict) else None

        imdb_full = data["id"]
        imdb_num = str(imdb_full.replace("tt", ""))

        return cls(
            imdbId=imdb_full,
            imdb_id=imdb_num,
            id=imdb_num,
            title_localized=data["titleText"]["text"],
            title=data["originalTitleText"]["text"],
            cover_url=cover_url,
            url=f"https://www.imdb.com/title/{imdb_full}/",
            year=year,
            kind=data.get("titleType", {}).get("id"),
            rating=data.get("ratingsSummary", {}).get("aggregateRating"),
        )

    @classmethod
    def from_filmography(cls, data: dict):
        year = data.get("releaseYear", {})
        if isinstance(year, dict):
            year = year.get("year", None)
        _cover = data.get("primaryImage", {})
        if _cover:
            cover_url = _cover.get("url", None)
        else:
            cover_url = None

        return cls(
            id=str(data["id"].replace("tt", "")),
            imdb_id=str(data["id"].replace("tt", "")),
            imdbId=data["id"],
            title=data.get("titleText", {}).get("text", ""),
            title_localized=data.get("originalTitleText", {}).get("text", ""),
            cover_url=cover_url,
            url=f"https://www.imdb.com/title/{data['id']}/",
            year=year,
            kind=data.get("titleType", {}).get("id", None),
            rating=data.get("ratingsSummary", {}).get("aggregateRating", None),
        )

    def __str__(self):
        return f"{self.title} ({self.year}) - {self.imdbId} ({self.kind})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title} - {self.year} - {self.imdbId} - {self.kind})"


class SearchResult(BaseModel):
    """Results from a title/person search query.

    Returned by :func:`~imdbinfo.services.search_title`. Contains both title matches
    and people matches in separate lists.

    Attributes
    ----------
    titles : List[MovieBriefInfo]
        Matching movie, TV series, and episode titles.
    names : List[Person]
        Matching people (actors, directors, writers, etc.).

    Examples
    --------

    ```python
    >>> from imdbinfo import search_title
    >>> results = search_title("The Matrix", year=1999)
    >>> print(f"Found {len(results.titles)} titles and {len(results.names)} people")
    >>> for title in results.titles:
    ...     print(f"  {title.title} ({title.year})")
    ```
    """

    titles: List[MovieBriefInfo] = Field(default_factory=list)
    names: List[Person] = Field(default_factory=list)


class PersonDetail(BaseModel):
    """Comprehensive biography and filmography for a person.

    Returned by :func:`~imdbinfo.services.get_name`. Contains personal biography,
    career information, and complete filmography across all job categories.

    Attributes
    ----------
    id : str
        IMDb person ID without ``nm`` prefix (e.g., ``"0000206"``).
    imdb_id : str
        IMDb person ID without ``nm`` prefix. Same as ``id``.
    imdbId : str
        IMDb person ID with ``nm`` prefix (e.g., ``"nm0000206"``).
    name : str
        Person's full name.
    url : str
        IMDb profile URL.
    knownfor : List[str]
        List of titles the person is best known for (as titles).
    image_url : str, optional
        URL of the person's profile photo.
    bio : str, optional
        Biography or summary.
    height : str, optional
        Physical height.
    primary_profession : List[str]
        Primary job categories (e.g., ``["actor", "producer"]``).
    birth_date : str, optional
        Birth date (ISO format: ``YYYY-MM-DD``).
    birth_place : str, optional
        Birth location.
    death_date : str, optional
        Death date (ISO format: ``YYYY-MM-DD``).
    death_place : str, optional
        Death location.
    death_reason : str, optional
        Cause of death.
    jobs : List[str]
        Complete list of job titles/professions.
    credits : Dict[str, List[MovieBriefInfo]]
        Filmography by job category (e.g., ``{"actor": [...], "director": [...]}``)
    unreleased_credits : Dict[str, List[MovieBriefInfo]]
        Unreleased/upcoming projects by job category.

    Examples
    --------

    ```python
    >>> from imdbinfo import get_name
    >>> person = get_name("nm0000206")  # Keanu Reeves
    >>> print(person.name)
    Keanu Reeves
    >>> print(f"Known for: {', '.join(person.knownfor[:3])}")
    >>> for category, titles in person.credits.items():
    ...     print(f"{category.title()}: {len(titles)} titles")
    ```
    """

    id: str
    imdb_id: str
    imdbId: str
    name: str
    url: str
    knownfor: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    bio: Optional[str] = None
    height: Optional[str] = None
    primary_profession: List[str] = Field(default_factory=list)
    birth_date: Optional[str] = None
    birth_place: Optional[str] = None
    death_date: Optional[str] = None
    death_place: Optional[str] = None
    death_reason: Optional[str] = None
    jobs: List[str] = Field(default_factory=list)
    credits: Dict[str, List[MovieBriefInfo]] = Field(default_factory=dict)
    unreleased_credits: Dict[str, List[MovieBriefInfo]] = Field(default_factory=dict)

    def __str__(self):
        return f"{self.name} ({', '.join(self.knownfor)})"


class SeasonEpisode(BaseModel):
    id: str  # id without 'tt' prefix, e.g. '1234567'
    imdbId: str
    imdb_id: str
    title: str
    season: int
    episode: int
    plot: str
    image_url: Optional[str] = None
    rating: Optional[float] = None
    votes: Optional[int] = None
    year: Optional[int] = None
    release_date: Optional[str] = None
    kind: Optional[str] = None

    @classmethod
    def from_episode_data(cls, data: dict) -> "SeasonEpisode":
        """
        Create a SeasonEpisode instance from episode data dictionary.
        """
        return cls(
            id=data["id"].replace("tt", ""),
            imdbId=data["id"],
            imdb_id=data["id"].replace("tt", ""),
            title=data["titleText"],
            season=data["season"],
            episode=data["episode"],
            plot=data.get("plot", ""),
            image_url=data.get("image", {}).get("url", None),
            rating=data.get("aggregateRating", None),
            votes=data.get("voteCount", None),
            year=data.get("releaseYear", None),
            release_date=_release_date(data["releaseDate"]),
            kind=data.get("type"),
        )

    def __str__(self):
        return f"{self.title} (S{self.season:02d}E{self.episode:02d}) - {self.imdbId} ({self.year or 'N/A'}) - {self.kind or 'N/A'}"


class BulkedEpisode(BaseModel):
    id: str  # id without 'tt' prefix, e.g. '1234567'
    imdbId: str
    imdb_id: str
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    title: str
    plot: str
    image_url: Optional[str] = None
    rating: Optional[float] = None
    votes: Optional[int] = None
    year: Optional[int] = None
    release_date: Optional[str] = None
    kind: Optional[str] = None
    genres: Optional[List[str]] = None
    duration: Optional[int] = None  # Duration in seconds

    @classmethod
    def from_bulked_episode_data(cls, data: dict) -> "BulkedEpisode":
        """
        Create an EpisodeData instance from bulked episode data dictionary.
        This is used when fetching episodes in bulk from a series.
        """
        return cls(
            id=data["titleId"].replace("tt", ""),
            imdbId=data["titleId"],
            imdb_id=data["titleId"].replace("tt", ""),
            season_number=data.get("series", {}).get("seasonNumber", None),
            episode_number=data.get("series", {}).get("episodeNumber", None),
            title=data["titleText"],
            genres=data.get("genres") or [],
            plot=data.get("plot", ""),
            image_url=data.get("primaryImage", {}).get("url", None),
            rating=data.get("ratingSummary", {}).get("aggregateRating", None),
            votes=data.get("ratingSummary", {}).get("voteCount", None),
            year=data.get("releaseYear", None),
            release_date=_release_date(data["releaseDate"]),
            kind=data.get("titleType", {}).get("id", None),
            duration=data.get("runtime"),
        )

    def __str__(self):
        return f"{self.title} S{str(self.season_number).zfill(2)}-E{str(self.episode_number).zfill(2)}({self.release_date or 'N/A'}) - {self.imdbId} ({self.kind or 'N/A'})"


class SeasonEpisodesList(BaseModel):
    """
    EpisodesList model for a list of episodes.
    This model contains a list of EpisodeInfo objects representing the episodes of a series.
    It can be used to represent the episodes of a series in a specific season.
    """

    series_imdbId: str  # The IMDb ID of the series, e.g. 'tt1234567'
    season_number: int  # The season number, e.g. 1, 2, 3
    top_rating_episode: Optional[float] = None
    total_series_episodes: Optional[int] = (
        None  # Total number of episodes in the series
    )
    total_series_seasons: Optional[int] = None  # Total number of seasons in the series
    top_ten_episodes: Optional[List[dict]] = (
        None  # List of top ten episodes based on rating
    )
    episodes: List[SeasonEpisode] = Field(default_factory=list)

    @property
    def count(self) -> int:
        """
        Count the number of episodes in the list.
        Returns:
            int: The number of episodes in the list.
        """
        return len(self.episodes)

    def __len__(self):
        return len(self.episodes)

    def __getitem__(self, idx):
        return self.episodes[idx]

    def __str__(self):
        return f"Season {self.season_number} of series {self.series_imdbId} has {len(self.episodes)} episodes"


class AkaInfo(BaseModel):
    title: str
    country_code: str
    country_name: str
    language_code: Optional[str] = None
    language_name: Optional[str] = None

    @classmethod
    def from_data(
        self, title, country_code, country_name, language_code=None, language_name=None
    ):
        # if country_code is None, set it to US
        # if country_name is None, set it to United States
        if country_code is None:
            country_code = "US"
        if country_name is None:
            country_name = "United States"
        return AkaInfo(
            title=title,
            country_code=country_code,
            country_name=country_name,
            language_code=language_code,
            language_name=language_name,
        )

    def __str__(self):
        return f"{self.title} ({self.country_name or 'N/A'} - {self.language_name or 'N/A'})"

    def __repr__(self):
        return self.__str__()


class AkasData(BaseModel):
    imdbId: str
    akas: List[AkaInfo]

    def __len__(self):
        return len(self.akas)

    # create a method that when called self['akas'] returns the list of akas, and self[imdbId] returns the imdbId
    def __getitem__(self, item):
        if item == "akas":
            return self.akas
        elif item == "imdbId":
            return self.imdbId
        else:
            raise KeyError(f"Key {item} not found in AkasDataModel")


class ParentalGuideContentDescription(BaseModel):
    is_spoiler: bool = False
    text: str = ""

    @classmethod
    def from_node(cls, node: dict) -> "ParentalGuideContentDescription":
        return cls(
            is_spoiler=node.get("isSpoiler", False),
            text=node.get("text", {}).get("plaidHtml", ""),
        )


class ParentalGuideCategory(BaseModel):
    id: str = ""
    text: str = ""
    content_descriptions: List[ParentalGuideContentDescription] = Field(
        default_factory=list
    )
    severity: str = "NONE"

    @classmethod
    def from_edge(cls, edge: dict) -> "ParentalGuideCategory":
        cat = edge.get("category", {}) or {}
        cat_contents = [
            ParentalGuideContentDescription.from_node(item.get("node", {}) or {})
            for item in edge.get("guideItems", {}).get("edges", []) or []
        ]
        votesfor = 0
        severity = "NONE"
        for tm in edge.get("severityBreakdown", []):
            if tm.get("votedFor", 0) > votesfor:
                votesfor = tm.get("votedFor", 0)
                severity = tm.get("voteType", "NONE")

        return cls(
            id=cat.get("id", ""),
            text=cat.get("text", ""),
            content_descriptions=cat_contents,
            severity=severity,
        )

    def has_category_texts(self) -> bool:
        """Return True if there are any guide items in this category."""
        return len(self.content_descriptions) > 0

    def category_texts_list(self, spoiler=False) -> List[str]:
        """Return a list of texts from the guide items."""
        return [
            item.text
            for item in self.content_descriptions
            if item.is_spoiler == spoiler
        ]

    def __repr__(self):
        return f"{self.id} - {self.severity} ({len(self.content_descriptions)} descriptions)"

    def __str__(self):
        return self.__repr__()


class ParentalGuideList(BaseModel):
    categories: List[ParentalGuideCategory] = Field(default_factory=list)

    @classmethod
    def from_raw(cls, parental_guide: dict) -> Optional["ParentalGuideList"]:
        if not parental_guide:
            return None
        categories = [
            ParentalGuideCategory.from_edge(edge)
            for edge in parental_guide.get("categories", []) or []
        ]
        return cls(categories=categories)

    @property
    def summary(self) -> dict[str, str]:
        """Return the list of parental guide categories."""
        return {category.id: category.severity for category in self.categories}

    def __str__(self):
        return f"{self.summary}"

    def __repr__(self):
        return self.__str__()


class MediaItem(BaseModel):
    id: str
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    caption: Optional[str] = None
    type: Optional[str] = None
    copyright: Optional[str] = None
    created_by: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    names: List[Dict[str, str]] = Field(default_factory=list)
    titles: List[Dict[str, str]] = Field(default_factory=list)

    def __str__(self):
        return f"MediaItem({self.id}, {self.type}, {self.caption or ''}, {self.url or ''})"

    def __repr__(self):
        return self.__str__()


class MediaGallery(BaseModel):
    imdb_id: str
    total: int = 0
    items: List[MediaItem] = Field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.items)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        return self.items[idx]

    def __str__(self):
        return f"MediaGallery({len(self.items)}/{self.total} images)"

    def __repr__(self):
        return self.__str__()


class InterestScore(BaseModel):
    """Community interest and voting counts for a quote or trivia item.

    Fields:
        users_interested (int): Number of users who marked this item as interesting.
        users_voted (int): Total number of users who voted on this item.
    """

    users_interested: int = 0
    users_voted: int = 0

    @classmethod
    def from_node(cls, node: dict) -> "InterestScore":
        if not node:
            return cls()
        return cls(
            users_interested=node.get("usersInterested", 0) or 0,
            users_voted=node.get("usersVoted", 0) or 0,
        )

    def __str__(self):
        return f"InterestScore(interested={self.users_interested}, voted={self.users_voted})"

    def __repr__(self):
        return self.__str__()


class QuoteCharacter(BaseModel):
    """A character speaker attributed to a line in a quote.

    Represents the actor/character speaking a line in a movie quote.
    May be linked to an IMDb person page or be unattributed.

    Attributes
    ----------
    character : str, optional
        Character name as shown on IMDb (e.g., ``"Neo"``).
    id : str, optional
        IMDb person ID without ``nm`` prefix (e.g., ``"0000206"``).
        ``None`` if speaker has no linked IMDb person page.
    imdb_id : str, optional
        Alias of ``id``.
    imdbId : str, optional
        IMDb person ID with ``nm`` prefix (e.g., ``"nm0000206"``).
    """

    character: Optional[str] = None
    imdbId: Optional[str] = None
    id: Optional[str] = None
    imdb_id: Optional[str] = None


class QuoteLine(BaseModel):
    """A single line of dialogue within a quote exchange.

    Represents one speaker's contribution to a multi-line quote.

    Attributes
    ----------
    characters : List[QuoteCharacter]
        Speaker(s) attributed to this line.
    text : str, optional
        The spoken dialogue text.
    stage_direction : str, optional
        Stage direction or action note (e.g., ``"[enters stage]"``).
    """

    characters: List[QuoteCharacter] = Field(default_factory=list)
    text: Optional[str] = None
    stage_direction: Optional[str] = None

    @property
    def speaker_names(self) -> List[str]:
        """Get list of character names speaking this line.

        Returns
        -------
        List[str]
            Character names from all speakers in this line.
        """
        return [c.character for c in self.characters if c.character]


class Quote(BaseModel):
    """A memorable quote or dialogue exchange from a movie or TV series.

    Returned by :func:`~imdbinfo.services.get_quotes`. Each quote contains one or more
    dialogue lines exchanged between characters, plus community voting data.

    Attributes
    ----------
    id : str
        IMDb quote ID (e.g., ``"qt0324252"``).
    lines : List[QuoteLine]
        Ordered list of dialogue lines in the exchange.
    interest_score : InterestScore
        Community engagement metrics (votes, interest count).

    Examples
    --------

    ```python
    >>> from imdbinfo import get_quotes
    >>> quotes = get_quotes("tt0133093")  # The Matrix
    >>> for quote in quotes[:3]:
    ...     print(f"Quote {quote.id}:")
    ...     print(f"  Speakers: {', '.join(quote.speakers)}")
    ...     for line in quote.lines:
    ...         print(f"    {line}")
    ```
    """

    id: str
    lines: List[QuoteLine] = Field(default_factory=list)
    interest_score: InterestScore = Field(default_factory=InterestScore)

    @property
    def speakers(self) -> List[str]:
        """Get deduplicated list of all character names in this quote.

        Returns
        -------
        List[str]
            Unique character names who speak in this quote.
        """
        seen: set = set()
        result = []
        for line in self.lines:
            for name in line.speaker_names:
                if name not in seen:
                    seen.add(name)
                    result.append(name)
        return result

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, idx):
        return self.lines[idx]

    def __str__(self):
        parts = [str(line) for line in self.lines if line.text]
        return "\n".join(parts)

    def __repr__(self):
        return f"Quote(id={self.id!r}, lines={len(self.lines)}, speakers={self.speakers})"
