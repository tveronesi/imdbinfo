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

from typing import Optional, List, Dict, Tuple, Union
from pydantic import BaseModel, Field, field_validator
import logging

from .transformers import _release_date

EPISODE_IDENTIFIERS = ("tvEpisode", "podcastEpisode")

SERIES_IDENTIFIERS = ("tvSeries", "tvMiniSeries", "podcastSeries")

logger = logging.getLogger(__name__)


class Person(BaseModel):
    """person model for directors, cast and search results.
    This model is used to represent a person in the IMDb database.
    It can be used for directors, cast members and search results.
    It contains the basic information about a person such as name, id, imdb_id, imdbId, url and job.
    """

    id: str  # id withouyt 'tt' prefix, e.g. '0133093', same as imdb_id
    imdb_id: str  # id without 'nm' prefix, e.g. '0000126'
    imdbId: str  # id with 'nm' prefix, e.g. 'nm0000126'
    name: str
    url: str
    job: Optional[str] = None

    @classmethod
    def from_directors(cls, data: dict):
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
            name=data["node"]["name"]["nameText"]["text"],
            imdb_id=data["node"]["name"]["id"].replace("nm", ""),
            id=data["node"]["name"]["id"].replace("nm", ""),
            imdbId=data["node"]["name"]["id"],
            url=f"https://www.imdb.com/name/{data['node']['name']['id']}",
            job="Cast",
        )

    @classmethod
    def from_search(cls, data: dict):
        return cls(
            name=data["nameText"],
            imdb_id=data["nameId"].replace("nm", ""),
            id=data["nameId"].replace(
                "nm", ""
            ),  # id without 'nm' prefix, e.g. '0000126'
            imdbId=data["nameId"],
            url=f"https://www.imdb.com/name/{data['nameId']}",
            job=str((data.get("professions") or [""])[0]),
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
    def is_series(self) -> bool:
        """
        Check if this movie title is a series, the main title of a series.
        If True, it means that this is a series, not a movie, not an episode, but the main reference for the series itself, and series details can be found in the self.info_series property.
        """
        return getattr(self, "kind", None) in SERIES_IDENTIFIERS

    def is_episode(self) -> bool:
        """
        Check if this movie title is an episode of a series.
        If True, means that this is the episode of a series and episode details can be found in the self.info_episode property
        """
        return getattr(self, "kind", None) in EPISODE_IDENTIFIERS


class InfoSeries(BaseModel):
    display_years: List[str] = Field(
        default_factory=list
    )  # e.g. ['2013', '2014', '2015']
    display_seasons: List[str] = Field(default_factory=list)  # e.g. ['1', '2', '3']
    creators: List[Person] = Field(
        default_factory=list
    )  # eg. [Person(...), Person(...)]

    @field_validator("display_years", mode="before")
    def filter_years(cls, value):
        if value is None:
            return []
        return [
            str(y) for y in value if isinstance(y, str) and len(y) == 4 and y.isdigit()
        ]

    def get_creators(self) -> List[Person]:
        return self.creators or []

    def __str__(self):
        return f"Years: {self.display_years[-1] if self.display_years else ''}-{self.display_years[0] if self.display_years else ''}, Seasons: {len(self.display_seasons)}"


class InfoEpisode(BaseModel):
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
    """Model to group award-related counts for a title.

    Fields:
        wins (Optional[int]): Number of wins.
        nominations (Optional[int]): Number of nominations.
        prestigious_award (Optional[dict]): Details of a prestigious award, if any.
    """

    wins: Optional[int] = None
    nominations: Optional[int] = None
    prestigious_award: Optional[dict] = None

    def __str__(self):
        parts = []
        if self.wins is not None:
            parts.append(f"Wins: {self.wins}")
        if self.nominations is not None:
            parts.append(f"Nominations: {self.nominations}")
        if self.prestigious_award is not None:
            parts.append(
                f"{self.prestigious_award.get('name', 'ND')}: Wins: {self.prestigious_award.get('wins', 0)}, Nominations: {self.prestigious_award.get('nominations', 0)}"
            )
        return ", ".join(parts) if parts else "No awards information"


class MovieDetail(SeriesMixin, BaseModel):
    """MovieDetail model for detailed information about a movie.
    This model contains all the information about a movie such as title, id, imdb_id, imdbId, url, cover_url, plot, release_date, languages, certificates, directors, stars,
    year, duration, country_codes, rating, metacritic_rating, votes, trailers, genres, interests, worldwide_gross, production_budget, storyline_keywords,
    filming_locations, sound_mixes, processes, printed_formats, negative_formats, laboratories, colorations, cameras, aspect_ratios, summaries, synopses,
    production and categories.
    It also includes a field_validator to ensure that certain fields are lists and not None.
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
    info_series: Optional[InfoSeries] = (
        None  # e.g. SeriesInfo(display_years=['2013', '2014', '2015'], display_seasons=['1', '2', '3'])
    )


class TvEpisodeDetail(MovieDetail):
    info_episode: Optional[InfoEpisode] = None  # e.g. SeriesInfo(display_year


class MovieBriefInfo(SeriesMixin, BaseModel):
    """
    MovieBriefInfo model for search results and cast members.
    This model is used to represent a movie in search results and cast members.
    It contains basic information about a movie such as title, id, imdb_id, imdbId, url, cover_url, year, rating and kind.
    It can be used to represent a movie in search results or as part of a cast member's credits.
    It includes class methods to create an instance from search results and cast data.
    """

    id: str  # id withouyt 'tt' prefix, e.g. '0133093', same as imdb_id
    imdb_id: str
    imdbId: str
    title: str
    title_localized: str
    cover_url: Optional[str] = None
    url: Optional[str] = None
    year: Optional[int] = None
    kind: Optional[str] = None  # e.g. 'movie', 'tvSeries', 'tvSeriesEpisode' ...
    rating: Optional[float] = None  # e.g. 8.7

    @classmethod
    def from_movie_search(cls, data: dict):
        return cls(
            imdbId=data["titleId"],
            imdb_id=str(data["titleId"].replace("tt", "")),
            id=str(data["titleId"].replace("tt", "")),
            title_localized=data["titleText"],
            title=data["originalTitleText"],
            cover_url=data.get("primaryImage", {}).get("url", None),
            url=f"https://www.imdb.com/title/{data['titleId']}/",
            year=data.get("releaseYear", None),
            kind=data.get("titleType", {}).get("id", None),
            rating=data.get("ratingSummary", {}).get("aggregateRating", None),
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
    """
    SearchResult model for search results.
    This model contains the results of a search query, including a list of titles and names.
    It is used to represent the results of a search query for movies and people.
    It includes a list of MovieBriefInfo objects for titles and a list of Person objects for names.
    """

    titles: List[MovieBriefInfo] = Field(default_factory=list)
    names: List[Person] = Field(default_factory=list)


class PersonDetail(BaseModel):
    """
    PersonDetail model for detailed information about a person.
    This model contains all the information about a person such as id, imdb_id, imdbId, name, url, knownfor, image_url, bio, height, primary_profession,
    birth_date, birth_place, death_date, death_place, jobs, credits and unreleased_credits.

    """

    id: str  # id without 'nm' prefix, e.g. '0000126', same as imdb_id
    imdb_id: str  # id without 'nm' prefix, e.g. '0000126' same as id
    imdbId: str  # id with 'nm' prefix
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
        return f"{self.title} ({self.release_date or 'N/A'}) - {self.imdbId} ({self.kind or 'N/A'})"


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
        return "Season"


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
