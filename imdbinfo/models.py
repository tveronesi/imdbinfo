from typing import Optional, List, Dict, Tuple
from pydantic import BaseModel, Field

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


class MovieDetail(BaseModel):
    imdbId: str
    imdb_id: str
    title: str
    kind: Optional[str] = None
    url: str = ""
    cover_url: str
    plot: Optional[str] = None
    release_date: Optional[str] = None
    languages: List[str] = Field(default_factory=list)
    certificates: Dict[str, Tuple[str, str]] = Field(default_factory=dict)
    directors: List[Person] = Field(default_factory=list)
    cast: List[Person] = Field(default_factory=list)
    stars: List[Person] = Field(default_factory=list)
    year: Optional[int] = None
    duration: Optional[int] = None
    country_codes: List[str] = Field(default_factory=list)
    rating: Optional[float] = None
    metacritic_rating: Optional[int] = None
    votes: Optional[int] = None
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
    aspect_ratios: List[Tuple[str, str]] = Field(default_factory=list)
    summaries: List[str] = Field(default_factory=list)
    synopses: List[str] = Field(default_factory=list)
    production: List[str] = Field(default_factory=list)
    categories: Dict[str, List[Person]] = Field(default_factory=dict)

class MovieInfo(BaseModel):

    imdbId: str
    imdb_id: str
    title: str
    cover_url: Optional[str] = None
    url: Optional[str] = None
    year: Optional[int] = None
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
    titles: List[MovieInfo] = Field(default_factory=list)
    names: List[Person] = Field(default_factory=list)
