from typing import Optional, List, Dict, Tuple, Union, Any, Callable
from pydantic import BaseModel, field_validator
import logging

logger = logging.getLogger(__name__)

class Person(BaseModel):
    """ person model for directors, cast and search results.
    This model is used to represent a person in the IMDb database.
    It can be used for directors, cast members and search results.
    It contains the basic information about a person such as name, id, imdb_id, imdbId, url and job.
    """
    id: str  # id withouyt 'tt' prefix, e.g. '0133093', same as imdb_id
    imdb_id: str # id without 'nm' prefix, e.g. '0000126'
    imdbId: str # id with 'nm' prefix, e.g. 'nm0000126'
    name: str
    url: str
    job: Optional[str] = None

    @classmethod
    def from_directors(cls, data: dict):
        return cls(
            name=data['name']['nameText']['text'],
            imdb_id= data['name']['id'].replace('nm', ''),
            id= data['name']['id'].replace('nm', ''),
            imdbId=data['name']['id'],
            url=f"https://www.imdb.com/name/{data['name']['id']}",
            job='Director'
        )

    @classmethod
    def from_cast(cls, data: dict):
        return cls(
            name=data['node']['name']['nameText']['text'],
            imdb_id=data['node']['name']['id'].replace('nm', ''),
            id=data['node']['name']['id'].replace('nm', ''),
            imdbId=data['node']['name']['id'],
            url=f"https://www.imdb.com/name/{data['node']['name']['id']}",
            job='Cast'
        )
    @classmethod
    def from_search(cls, data: dict):
        return cls(
            name=data['displayNameText'],
            imdb_id=data['id'].replace('nm', ''),
            id=data['id'].replace('nm', ''),  # id without 'nm' prefix, e.g. '0000126'
            imdbId=data['id'],  # same as id without 'nm' prefix
            url=f"https://www.imdb.com/name/{data['id']}",
            job=str(data['knownForJobCategory'])
        )

    @classmethod
    def from_category(cls, data: dict):
        return cls(
            name=data['rowTitle'],
            imdb_id=data['id'].replace('nm', ''),
            id=data['id'].replace('nm', ''),  # id without 'nm' prefix, e.g. '0000126'
            imdbId=data['id'],  # same as id without 'nm' prefix
            url=f"https://www.imdb.com/name/{data['id']}",
            job=str(data.get('jobTitle', ''))
        )

    def __repr__(self):
        return f"{self.name} ({self.job})"

class CastMember(Person):
    """Cast member model for cast members in a movie.
    This model extends the Person model to include additional information specific to cast members.
    It includes the characters they played in the movie and their picture URL.
    """
    characters: List[str] = []
    picture_url: Optional[str] = None

    @classmethod
    def from_cast(cls, data: dict):
        return cls(
            name=data['rowTitle'],
            imdb_id=data['id'].replace('nm', ''),
            id=data['id'].replace('nm', ''),  # id without 'nm' prefix, e.g. '0000126'
            imdbId=data['id'],  #  with 'nm' prefix e.g. 'nm0000126'
            url=f"https://www.imdb.com/name/{data['id']}",
            job='Cast',
            characters=data.get('characters',[] ),
            picture_url=data.get('imageProps', {}).get('imageModel',{}).get('url', None)
        )

    def __repr__(self):
        return f"{self.name} ({', '.join(self.characters)})"

class MovieDetail(BaseModel):
    """MovieDetail model for detailed information about a movie.
    This model contains all the information about a movie such as title, id, imdb_id, imdbId, url, cover_url, plot, release_date, languages, certificates, directors, stars,
    year, duration, country_codes, rating, metacritic_rating, votes, trailers, genres, interests, worldwide_gross, production_budget, storyline_keywords,
    filming_locations, sound_mixes, processes, printed_formats, negative_formats, laboratories, colorations, cameras, aspect_ratios, summaries, synopses,
    production and categories.
    It also includes a field_validator to ensure that certain fields are lists and not None.
    """

    id: str # id without 'tt' prefix, e.g. '0133093', same as imdb_id
    imdb_id: str # id without 'tt' prefix, e.g. '0133093'
    imdbId: str # id with 'tt' prefix, e.g. 'tt0133093'
    title: str
    kind: Optional[str] = None
    url: str = ""
    cover_url: Optional[str] = None
    plot: Optional[str] = None
    release_date: Optional[str] = None
    languages: List[str] = []
    certificates: Dict[str, Tuple[str, str]] = {}
    directors: List[Person] = []
    stars: List[Person] = []
    year: Optional[int] = None
    duration: Optional[int] = None
    country_codes: List[str] = []
    rating: Optional[float] = None
    metacritic_rating: Optional[int] = None
    votes: Optional[int] = None
    trailers: List[str] = []
    genres:List[str] = []
    interests: List[str] = []
    worldwide_gross: Optional[str] = None
    production_budget: Optional[str] = None
    storyline_keywords: List[str] = []
    filming_locations: List[str] = []
    sound_mixes: List[str] = []
    processes: List[str] = []
    printed_formats: List[str] = []
    negative_formats: List[str] = []
    laboratories: List[str] = []
    colorations: List[str] = []
    cameras: List[str] = []
    aspect_ratios: List[Tuple[Optional[str], Optional[str]]] = []
    summaries: List[str] = []
    synopses: List[str] = []
    production: List[str] = []
    categories: Dict[str, List[Union[Person, CastMember]]] = {}

    @field_validator('languages', 'country_codes','genres', mode='before')
    def none_is_list(cls, value):
        if value is None:
            return []
        return value


class MovieInfo(BaseModel):
    """
    MovieInfo model for search results and cast members.
    This model is used to represent a movie in search results and cast members.
    It contains basic information about a movie such as title, id, imdb_id, imdbId, url, cover_url, year and kind.
    It can be used to represent a movie in search results or as part of a cast member's credits.
    It includes class methods to create an instance from search results and cast data.
    """
    id : str # id withouyt 'tt' prefix, e.g. '0133093', same as imdb_id
    imdb_id: str
    imdbId: str
    title: str
    cover_url: Optional[str] = None
    url: Optional[str] = None
    year: Optional[int] = None # TODO series will have year as string 'from-to'. For now only movies are supported
    kind: Optional[str] = None


    @classmethod
    def from_movie_search(cls, data:dict):
        return cls(
            imdbId=data['id'],
            imdb_id=str(data['id'].replace('tt', '')),
            id=str(data['id'].replace('tt', '')),
            title=data['titleNameText'],
            cover_url=data.get('titlePosterImageModel', {}).get('url', None),
            url = f"https://www.imdb.com/title/{data['id']}/",
            year=data.get('titleReleaseText',None),
            kind=data.get('imageType',None),

        )

    @classmethod
    def from_cast(self, data: dict):
        return self(
            id=str(data['id'].replace('tt', '')),
            imdb_id=str(data['id'].replace('tt', '')),
            imdbId=data['id'],
            title=data['titleNameText'],
            cover_url=data.get('titlePosterImageModel', {}).get('url', None),
            url = f"https://www.imdb.com/title/{data['id']}/",
            year=data.get('titleReleaseText',None),
            kind=data.get('imageType',None),
        )

class SearchResult(BaseModel):
    """
    SearchResult model for search results.
    This model contains the results of a search query, including a list of titles and names.
    It is used to represent the results of a search query for movies and people.
    It includes a list of MovieInfo objects for titles and a list of Person objects for names.
    """
    titles: List[MovieInfo] = []
    names: List[Person] = []


class PersonDetail(BaseModel):
    """
    PersonDetail model for detailed information about a person.
    This model contains all the information about a person such as id, imdb_id, imdbId, name, url, knownfor, image_url, bio, height, primary_profession,
    birth_date, birth_place, death_date, death_place, jobs, credits and unreleased_credits.

    """
    id: str # id without 'nm' prefix, e.g. '0000126', same as imdb_id
    imdb_id: str # id without 'nm' prefix, e.g. '0000126' same as id
    imdbId: str # id with 'nm' prefix
    name: str
    url: str
    knownfor: List[str] = []
    image_url: Optional[str] = None
    bio: Optional[str] = None
    height: Optional[str] = None
    primary_profession: List[str] = []
    birth_date: Optional[str] = None
    birth_place: Optional[str] = None
    death_date: Optional[str] = None
    death_place: Optional[str] = None
    jobs: List[str] = []
    credits: Dict[str, List[MovieInfo]] = {}
    unreleased_credits: Dict[str, List[MovieInfo]] = {}


    def __repr__(self):
        return f"{self.name} ({', '.join(self.knownfor)})"

