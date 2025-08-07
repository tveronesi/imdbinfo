[![Build Status](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml)
[![PyPI Version](https://img.shields.io/pypi/v/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
[![Python Versions](https://img.shields.io/pypi/pyversions/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
[![PyPI Downloads](https://static.pepy.tech/badge/imdbinfo/week)](https://pepy.tech/projects/imdbinfo)

[//]: # (![PyPI - Daily Downloads]&#40;https://img.shields.io/pypi/dm/your-package-name?label=PyPI%20downloads&logo=pypi&#41;)

# imdbinfo

**Your personal gateway to IMDb data**. Search for movies, series and people and get structured information in seconds.

## Features

- 🔍 **Search movies,series, miniseries and people** by name or title
- 🎬 **Detailed movie info** including cast, crew, ratings and more
- 👥 **Detailed person info** with biography, filmography and images
- 📺 **TV series and miniseries** support with seasons and episodes
- 📅 **Release dates** and **box office** information
- 🌍 **International titles** and **alternate titles**
- 📸 **Poster images** and **backdrops**
- 📊 **Ratings** from IMDb and other sources
- 🗂️ **Full filmography** for actors, directors and writers
- 📝 **Typed Pydantic models** for predictable responses
- ✅ **No API keys required**

## Installation

```bash
pip install imdbinfo
```

## Quick Start

```python
from imdbinfo.services import search_title, get_movie, get_name, get_episodes

# Search for a title
results = search_title("The Matrix")
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")

# Get movie details
movie = get_movie("0133093") # or 'tt0133093'
print(movie.title, movie.year, movie.rating)

# Get movie kind:
print(movie.kind) # movie, tvSeries, tvMiniSeries, tvEpisode, video
print(movie.is_series()) # False

# Get person details
person = get_name("nm0000206")# or '0000206' 
print(person.name, person.birth_date)
```
#### Working with Series and Episodes

The `movie` object provides helpful methods to identify its type:

- `movie.is_series()` — Returns `True` if the movie is a series.
- `movie.is_episode()` — Returns `True` if the movie is an episode.

Depending on the type, you can access additional information:

- For series: use `movie.info_series` to get series details.
- For episodes: use `movie.info_episode` to get episode details.

#### Example: Working with Series and Episodes

```python
from imdbinfo.services import get_movie, get_episodes

# Fetch a TV series as a Movie object
walking_dead_serie = get_movie("tt1520211")  # Walking Dead

# Check if the object is a series
print(walking_dead_serie.is_series())  # True

# Access series-specific information
print(f"Series Info: {walking_dead_serie.info_series}")

# Retrieve all episodes for the series
walking_dead_episodes = get_episodes(walking_dead_serie.imdb_id)

# Print details for the first 3 episodes
for episode_info in walking_dead_episodes[:3]:
    print(episode_info)

# Fetch a single episode as a Movie object and check its type
episode_detail = get_movie(episode_info.imdb_id)
print("Is Episode:", episode_detail.is_episode())  # True

# Access episode-specific information: series imdbid, season and episode number ...
print(f"Episode Info: {episode_detail.info_episode}")
```

For more examples see the [examples](examples/) folder.

> 💡 **Looking for a ready-to-use API based on this package? Check out [qdMovieAPI](https://github.com/tveronesi/qdMovieAPI) — a fast and simple way to access IMDb data via REST!**

## Why choose imdbinfo?

- Easy to use Python API
- Returns clean structured data
- Powered by requests and lxml
- Uses Pydantic for type safety
- No external dependencies or API keys required
- Ideal for quick scripts and data analysis

## Disclaimer
This project and its authors are not affiliated in any way with IMDb Inc. or its affiliates. 
For more information, please refer to the [DISCLAIMER](DISCLAIMER.txt) file.

## License

imdbinfo is released under the MIT License.
See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Open an issue or pull request on GitHub.

If you find this project useful, please consider giving it a ⭐ on GitHub!

Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.
