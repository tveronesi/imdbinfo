
[![Build and Publish to PyPI](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml)
# imdbinfo

A Python package to fetch and manage IMDb movie information easily.

## Requirements

Python (3.7 or higher)

## Installation

`pip install imdbinfo`

---
## NEW FEATURES

- **Search for titles and people**: You can now search for movies and people by name or title using the `search_title` function.
- **Get detailed person information**: Fetch detailed information about a person using their IMDb ID with the `get_name` function.
- **New Structured data models**:
  - `PersonDetail`: Contains detailed person information including name, biography, image, birth/death info, jobs, and credits. It's returned by the `get_name` function.

---
## Usage

#### Search titles/names
``` python
from imdbinfo.services import search_title, get_movie

# Search for a movie by title
results = search_title("The Matrix")
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")

for person in results.names:
    print(f"{person.name} ({person.job}) - {person.id}")
    
``` 
Will output:
``` 
# titles
Matrix (1999) - 0133093
Matrix Reloaded (2003) - 0234215
Matrix Resurrections (2021) - 10838180
Matrix Revolutions (2003) - 0242653
The Matrix Recalibrated (2004) - 0410519

# names
Vasyl Lomachenko (Actor) - 5263899
Rooney Mara (Actress) - 1913734
Martina McBride (Soundtrack) - 0005198
``` 

Dump the search results in JSON format, to see the full details of the search results:

``` python
print(results.model_dump_json())
```

#### Search movie by IMDb ID

``` python
Get detailed information about a movie by IMDb ID

``` python
# Get detailed information about a movie by IMDb ID
movie = get_movie("0133093") 
print(f"Title: {movie.title}") # Title: The Matrix
print(f"Year: {movie.year}") # Year: 1999
print(f"Rating: {movie.rating}") # Rating: 8.7
print(f"Genres: {', '.join(movie.genres)}") # Genres: Action, Sci-Fi
print(f"Plot: {movie.plot}") # Plot: A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.
``` 

Dump the movie details in JSON format:

``` python
print(movie.model_dump_json())
```

#### Search person by IMDb ID

``` python

Get detailed information about a person by IMDb ID

``` python
from imdbinfo.services import get_name
person = get_name("nm0000206")  # Keanu Reeves
print(f"Known For: {', '.join(person.knownfor)}")
print(f"Image URL: {person.image_url}")
print(f"IMDb URL: {person.url}")
print(f"Name: {person.name}")
print(f"Known For: {', '.join(person.knownfor)}")
print(f"Birth Date: {person.birth_date}")
print(f"Birth Place: {person.birth_place}")
print(f"Death Date: {person.death_date}")
print(f"Death Place: {person.death_place}")
print(f"Bio: {person.bio}")
print(f"Height: {person.height}")
print(f"Primary Profession: {', '.join(person.primary_profession)}")

``` 

The list of credits of the person can be accessed via the `person.credits` attribute, which is a dictionary containing various categories of work, such as:

``` python
print(person.credits['actor'])  # List of movies (MovieInfo) where the person acted
print(person.credits['director'])  # List of movies  (MovieInfo) where the person directed
print(person.credits['producer'])  # List of movies  (MovieInfo) where the person produced
print(person.credits['writer'])  # List of movies  (MovieInfo) where the person writed
print(person.credits['composer'])  # List of movies  (MovieInfo)  where the person composed music
print(person.credits['cinematographer'])  # List of movies (MovieInfo)  where the person was cinemat

```

A PersonDetail object contains 3 `credits` dictionary with the most relevant categories of work for the person.

So for instace, for Steven Spielberg, you can access his movies as director, producer, 
and writer but for Kevin Costner, you can access his movies as actor, writer, and producer.


# IMDb Info Service

This project provides Python services for interacting with IMDb data, focusing on movies and people. The main logic is in `services.py`, and the data models are defined in `models.py`.

## Services (`services.py`)

- **get_movie(imdb_id: str) -> MovieDetail**  
  Fetches detailed information about a movie using its IMDb ID (without the `tt` prefix). Returns a `MovieDetail` object.

- **search_title(title: str) -> Optional[SearchResult]**  
  Searches IMDb for a given movie title. Returns a `SearchResult` object with lists of matching movies and people.

- **get_name(person_id: str) -> Optional[PersonDetail]**  
  Fetches detailed information about a person using their IMDb ID (without the `nm` prefix). Returns a `PersonDetail` object.

## Output Models (`models.py`)

- **MovieDetail**  
  Contains detailed movie data: title, year, genres, directors, cast, plot, ratings, technical details, and more.

- **MovieInfo**
    Contains basic movie information: title, year, IMDb ID, and URL.

- **SearchResult**  
  Contains search results:  
  - `titles`: List of `MovieInfo` objects (basic movie info)  
  - `names`: List of `Person` objects (basic person info)

- **CastMember**  
  Represents a cast member with their name, IMDb ID, URL, and job title.
- **Person**  
  Represents a person with their name, IMDb ID, URL, and job title. Used in search results.

- **PersonDetail**  
  Contains detailed person data: name, biography, image, birth/death info, jobs, credits, and more.

All models use Pydantic for type safety and structured data.

Under `MovieDetail.categories` dictionary, you can find various categories of people involved in the movie production. The categories include:

* director
* writer
* cast
* producer
* composer
* cinematographer
* editor
* casting_director
* production_designer
* art_director
* set_decorator
* costume_designer
* make_up_department
* production_manager
* assistant_director
* art_department
* sound_department
* special_effects
* visual_effects
* stunts
* camera_department
* animation_department
* casting_department
* costume_department
* editorial_department
* location_management
* music_department
* script_department
* transportation_department
* miscellaneous

Each category contains a list of people involved in that role, in the format Model 

    Person(name='Keanu Reeves', id='nm0000206', url='https://www.imdb.com/name/nm0000206', job='Cast')


## License
This project is licensed under GPL  v2.0 - see the [LICENSE](LICENSE) file for details.
## Contributing
Contributions are welcome! Please read the [CONTRIBUTING](CONTRIBUTING.md) file for details on how to contribute to this project.
## Issues
