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

## Documentation
For detailed documentation, please refer to the [imdbinfo documentation](https://imdbinfo.readthedocs.io/en/latest/).
## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
## Contributing
Contributions are welcome! Please read the [CONTRIBUTING](CONTRIBUTING.md) file for details on how to contribute to this project.
## Issues
