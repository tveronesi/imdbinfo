from typing import Optional, List, Dict, Tuple, Union
from pydantic import BaseModel, field_validator

class Person(BaseModel):
    name: str
    id: str
    url: str
    job: Optional[str] = None

    @classmethod
    def from_directors(cls, data: dict):
        return cls(
            name=data['name']['nameText']['text'],
            id=data['name']['id'],
            url=f"https://www.imdb.com/name/{data['name']['id']}",
            job='Director'
        )

    @classmethod
    def from_cast(cls, data: dict):
        return cls(
            name=data['node']['name']['nameText']['text'],
            id=data['node']['name']['id'],
            url=f"https://www.imdb.com/name/{data['node']['name']['id']}",
            job='Cast'
        )
    @classmethod
    def from_search(cls, data: dict):
        return cls(
            name=data['displayNameText'],
            id=data['id'],
            url=f"https://www.imdb.com/name/{data['id']}",
            job=str(data['knownForJobCategory'])
        )

    @classmethod
    def from_category(cls, data: dict):
        return cls(
            name=data['rowTitle'],
            id=data['id'],
            url=f"https://www.imdb.com/name/{data['id']}",
            job=str(data.get('jobTitle', ''))
        )

    def __repr__(self):
        return f"{self.name} ({self.job})"

class CastMember(Person):
    characters: List[str] = []
    picture_url: Optional[str] = None

    @classmethod
    def from_cast(cls, data: dict):
        return cls(
            name=data['rowTitle'],
            id=data['id'],
            url=f"https://www.imdb.com/name/{data['id']}",
            job='Cast',
            characters=data.get('characters',[] ),
            picture_url=data.get('imageProps', {}).get('imageModel',{}).get('url', None)
        )

    def __repr__(self):
        return f"{self.name} ({', '.join(self.characters)})"

class MovieDetail(BaseModel):
    imdbId: str
    imdb_id: str
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

    imdbId: str
    imdb_id: str
    title: str
    cover_url: Optional[str] = None
    url: Optional[str] = None
    year: Optional[int] = None # TODO series will have year as string 'from-to'. For now only movies are supported
    kind: Optional[str] = None


    @classmethod
    def from_movie_info(cls, data:dict):
        return cls(
            imdbId=data['id'],
            imdb_id=str(data['id'].replace('tt', '')),
            title=data['titleNameText'],
            cover_url=data.get('titlePosterImageModel', {}).get('url', None),
            url = f"https://www.imdb.com/title/{data['id']}/",
            year=data.get('titleReleaseText',None),
            kind=data.get('imageType',None),

        )

class SearchResult(BaseModel):
    titles: List[MovieInfo] = []
    names: List[Person] = []
