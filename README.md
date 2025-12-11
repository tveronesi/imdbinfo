[![PyPI Downloads](https://static.pepy.tech/badge/imdbinfo)](https://pepy.tech/projects/imdbinfo)
[![PyPI Version](https://img.shields.io/pypi/v/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
[![Build Status](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)

[//]: # (![PyPI - Daily Downloads]&#40;https://img.shields.io/pypi/dm/your-package-name?label=PyPI%20downloads&logo=pypi&#41;)

# imdbinfo

**Your personal gateway to IMDb data**. Search for movies, series and people and get structured information in seconds.

## Features

- 🔍 **Search movies, series, miniseries and people** by name or title
- 🎬 **Detailed movie info** including cast, crew, ratings and more
- 👥 **Detailed person info** with biography, filmography and images
- 📺 **TV series and miniseries** support with seasons and episodes
- 🌐 **Localized results** in multiple languages (set globally or per request)
- 📅 **Release dates** and **box office** information
- 🌍 **International titles** and **alternate titles (AKAs)** via `get_akas`
- 📸 **Poster images** and **backdrops**
- 📊 **Ratings** from IMDb and other sources
- 📝 **User reviews and ratings** via `get_reviews`
- 🎭 **Movie trivia and interesting facts** via `get_trivia`
- 🗂️ **Full filmography** for actors, directors and writers via `get_filmography`
- 📝 **Typed Pydantic models** for predictable responses
- ⚡ **Built-in caching** for faster repeated requests
- ✅ **No API keys required**

## Installation

```bash
pip install imdbinfo
```

## Quick Start

```python
from imdbinfo import search_title, get_movie, get_name, get_season_episodes, get_reviews, get_trivia

# Search for a title
results = search_title("The Matrix")
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - Rating: {movie.rating} - {movie.imdb_id}")

# Get movie details
movie = get_movie("0133093")  # or 'tt0133093'
print(movie.title, movie.year, movie.rating)

# Get movie kind:
print(movie.kind)  # movie, tvSeries, tvMiniSeries, tvMovie, tvEpisode, tvSpecial, tvShort, short, videoGame, video, musicVideo, podcastEpisode, podcastSeries
print(movie.is_series())  # False

# Get person details
person = get_name("nm0000206")  # or '0000206' 
print(person.name, person.birth_date)
```
#### Working with Series and Episodes

The `movie` object provides helpful methods to identify its type:

- `movie.is_series()` — Returns `True` if the movie is a series.
- `movie.is_episode()` — Returns `True` if the movie is an episode.

Depending on the type, you can access additional information:

- For series: use `movie.info_series` to get series details (creators, seasons, episodes, ...)
- For episodes: use `movie.info_episode` to get episode details 

#### Example: Working with Series and Episodes

```python
from imdbinfo import get_movie, get_season_episodes

# Fetch a TV series as a Movie object
walking_dead_serie = get_movie("tt1520211")  # Walking Dead

# Check if the object is a series
print(walking_dead_serie.is_series())  # True

# Access series-specific information
print(f"Series Info: {walking_dead_serie.info_series}")

# Retrieve episodes for the series season 1
walking_dead_episodes = get_season_episodes(walking_dead_serie.imdb_id, season=1)

# Print details for the first 3 episodes from the season 1
for episode_info in walking_dead_episodes[:3]:
    print(episode_info)

# Fetch a single episode as a Movie object and check its type
episode_detail = get_movie(episode_info.imdb_id)
print("Is Episode:", episode_detail.is_episode())  # True

# Access episode-specific information: series imdbid, season and episode number ...
print(f"Episode Info: {episode_detail.info_episode}")
```

#### All episodes in a series
You can now retrieve all episodes in a series with a single call:
```python
from imdbinfo import get_all_episodes
# Fetch all episodes for a series
all_episodes = get_all_episodes("tt1520211")  # Walking Dead
for episode in all_episodes:
    print(f"Title: {episode.title} - ({episode.imdbId})")
    print(f"Plot: {episode.plot[:100]}...")
    print(f"Release Date: {episode.release_date}")
    print(f"Rating: {episode.rating}")
    print(f"Duration: {episode.duration/60}min")
    print("" + "="*50)
```

#### Company Credits

* distribution companies, 
* production companies, 
* sales companies, 
* special effects companies, 
* miscellaneous companies

You can now extract information about the companies involved in a movie or series:

```python
from imdbinfo import get_movie

movie = get_movie("tt0133093")  # The Matrix

# Distribution companies
for company in movie.company_credits["distribution"]:
    print(f"Distribution: {company.name} ({company.country})")

# Sales companies
for company in movie.company_credits["sales"]:
    print(f"Sales: {company.name}")

# Production companies
for company in movie.company_credits["production"]:
    print(f"Production: {company.name}")

# Special effects companies
for company in movie.company_credits["specialEffects"]:
    print(f"Special Effects: {company.name}")

# Miscellaneous companies
for company in movie.company_credits["miscellaneous"]:
    print(f"Miscellaneous: {company.name}")
```

#### Alternate titles (AKAs)
Fetch international and alternate titles for any movie or series:
```python
from imdbinfo import get_akas
akas = get_akas("tt0133093")  # The Matrix
for aka in akas["akas"][:5]:
    print(f"{aka.title} ({aka.country_name})")
```

#### Reviews and User Ratings
Get user reviews and ratings for any movie or series:
```python
from imdbinfo import get_reviews
reviews = get_reviews("tt0133093")  # The Matrix
for review in reviews[:3]:
    print(f"Rating: {review['authorRating']}/10")
    print(f"Summary: {review['summary']}")
    print(f"Helpful votes: {review['upVotes']} up, {review['downVotes']} down")
    print(f"Spoiler: {review['spoiler']}")
    print("---")
```

#### Movie Trivia and Facts
Discover interesting trivia and behind-the-scenes facts:
```python
from imdbinfo import get_trivia
trivia = get_trivia("tt0133093")  # The Matrix
for fact in trivia[:3]:
    print(f"Interest Score: {fact['interestScore']}")
    print(f"Fact: {fact['body'][:200]}...")
    print("---")
```

### Localized results in multiple languages (set globally or per request)

Added support for locales in `search_movie`, `get_movie`, `get_episodes`, `get_all_episodes`, `get_name`
```python
from imdbinfo import get_movie, search_title
# Fetch movie details in Italian
movie_it = get_movie("tt0133093", locale="it")  # The Matrix

# Search for titles in Spanish (although IMDb search is mostly in all languages)
results_es = search_title("La Casa de Papel", locale="es")
```

Localized data can be set globally, dont need to pass `locale` every time in the functions:
```python
from imdbinfo import get_movie
from imdbinfo.locale import set_locale
set_locale("it")  # Set default locale to Italian
movie_it = get_movie("tt0133093")  # The Matrix in Italian
```

#### MovieInfoBrief.title_localized
The `MovieInfoBrief` object (e.g., items in `results.titles` from `search_title`) now includes the `title_localized` property. This property contains the title in the requested locale, if available, and falls back to the default `title` when a localized version is not present.

Example:
```python
from imdbinfo import search_title

# Search for a title with a specific locale
results = search_title("The Matrix", locale="it")
for item in results.titles:
    # Print the localized title if available, otherwise the default title
    print(item.title, "->", getattr(item, "title_localized", item.title))
```

### Filtering results based on type (e.g. Movies, Series, Episodes etc.) 🔽 
You can filter results from `search_title`, done server-side.
```python
from imdbinfo import search_title, TitleType

# Search for single type: movies
results = search_title("The Matrix", title_type=TitleType.Movies)
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")

# Search for multiple types: movies, shorts and videos.
results = search_title("The Matrix", title_type=(TitleType.Movies, TitleType.Shorts, TitleType.Video))
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")

```

### Get filmography with images 🎬🖼️
You can now get filmography for actors, directors and writers and all credits with images:
```python
from imdbinfo import get_filmography

filmography = get_filmography("nm0000206")  # Brad Pitt
if filmography:
    for role, films in filmography.items():
        print(f"\nRole: {role}")
        for film in films:
            print(f" - {film.title} ({film.year}) [{film.imdbId}]")

```

#### Get all interests for a title

_Fetch all interests for a title using the provided IMDb ID. Most time it returns the same as genres. 
    It requires a new request and parsing. Use it only if you really need it._

```python
from imdbinfo import get_all_interests

movies = ["tt1490017", "tt0133093"]

for imdb_id in movies:
    interests = get_all_interests(imdb_id)
    print(f"Interests for {imdb_id}: {interests}")
```


📝 For more examples see the [examples](examples/) folder.

> 💡 **Looking for a ready-to-use API based on this package? Check out [qdMovieAPI](https://github.com/tveronesi/qdMovieAPI) — a fast and simple way to access IMDb data via REST!**

## Why choose imdbinfo?

- Easy to use Python API
- Returns clean structured data
- Powered by niquests and lxml
- Uses Pydantic for type safety
- No external dependencies or API keys required
- Ideal for quick scripts and data analysis

## Disclaimer
This project and its authors are not affiliated in any way with IMDb Inc. or its affiliates. 
For more information, please refer to the [DISCLAIMER](DISCLAIMER.txt) file.

## Contributing

Contributions are welcome! Open an issue or pull request on GitHub.

If you find this project useful, please consider giving it a ⭐ on GitHub!

Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## License

imdbinfo is released under the MIT License.
See the [LICENSE](LICENSE) file for details.

#### Awards

The package groups award-related counts in the `MovieDetail.awards` object (an `AwardInfo` instance). The model currently exposes:

- `wins` — number of award wins
- `nominations` — number of nominations (excluding wins)
- `prestigious_award` — optional dict containing details of a prestigious award (may include `wins` and `nominations` keys)

Example showing how to safely read `MovieDetail.awards` using the current model shape:

```python
from imdbinfo import get_movie

movie = get_movie("tt0133093")  # The Matrix
aw = movie.awards
if not aw:
    print("No award information available for this title")
else:
    # basic counts
    print("wins:", aw.wins)
    print("nominations:", aw.nominations)

    # prestigious award (may be None or a dict)
    if aw.prestigious_award:
        pa = aw.prestigious_award
        print("prestigious wins:", pa.get("wins"))
        print("prestigious nominations:", pa.get("nominations"))
    else:
        print("No prestigious award summary available")
```

Notes:
- The JSON parser maps page data into `movie.awards` (a dict turned into an `AwardInfo` instance). Depending on the source data, `prestigious_award` can be None or a dict with `wins` and `nominations`.
- Use `if movie.awards:` to check presence before reading attributes.
