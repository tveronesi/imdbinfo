
[![Build and Publish to PyPI](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml)
# imdbinfo

A Python package to fetch and manage IMDb movie information easily.

## Requirements

Python (3.7 or higher)

## Installation

`pip install imdbinfo`

## Usage

``` python
from imdbinfo.services import search_title, get_movie

# Search for a movie by title
results = search_title("The Matrix")
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")
``` 
Will output:
``` 
Matrix (1999) - 0133093
Matrix Reloaded (2003) - 0234215
Matrix Resurrections (2021) - 10838180
Matrix Revolutions (2003) - 0242653
The Matrix Recalibrated (2004) - 0410519
``` 

Dump the search results in JSON format, to see the full details of the search results:

``` python
print(results.model_dump_json())
```

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

## NEW FEATURES

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

## Deprecation Notice

`MovieDetail.directors` and `MovieDetail.cast` have been deprecated in favor of the new categories structure: `MovieDetail.categories['director']` and `MovieDetail.categories['cast']` respectively.

Adding `MovieDetail.stars` as a new attribute to `MovieDetail` to replace the old `MovieDetail.cast` attribute.

The old attribute `MovieDetail.directors` will be removed in a future release and the attribute `MovieDetail.cast` will be renamed into `MovieDetail.stars` .



## License
This project is licensed under GPL  v2.0 - see the [LICENSE](LICENSE) file for details.
## Contributing
Contributions are welcome! Please read the [CONTRIBUTING](CONTRIBUTING.md) file for details on how to contribute to this project.
## Issues
