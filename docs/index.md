# 🎬 imdbinfo – A Simple Python Tool to Fetch IMDb 
### Movie Series Episodes & Actor Data (No API Keys Needed)

[![PyPI Downloads](https://static.pepy.tech/badge/imdbinfo)](https://pepy.tech/projects/imdbinfo) 
[![Build Status](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)

Have you ever needed to grab movie or actor details from IMDb, but didn’t want to deal with complicated APIs or authentication keys?

That’s exactly why I built [`imdbinfo`](https://github.com/tveronesi/imdbinfo) — a lightweight, easy-to-use Python package to search and fetch structured IMDb data, **with no API keys required**.

---

## 🚀 What is imdbinfo?

**imdbinfo** is your personal gateway to IMDb data. It lets you:

- 🔍 **Search movies, series, miniseries and people** by name or title
- 🎬 **Detailed movie info** including cast, crew, ratings and more
- 👥 **Detailed person info** with biography, filmography and images
- 📺 **TV series and miniseries** support with seasons and episodes
- 🌐 **Localized results** in multiple languages (set globally or per request)
- 📅 **Release dates** and **box office** information
- 🌍 **International titles** and **alternate titles (AKAs)** via `get_akas`
- 📸 **Poster images** and **backdrops**
- 📊 **Ratings** from IMDb and other sources
- 🗂️ **Full filmography** for actors, directors and writers
- 📝 **Typed Pydantic models** for predictable responses
- ⚡ **Built-in caching** for faster repeated requests
- ✅ **No API keys required**

_No complicated scraping. No API credentials. Just clean, reliable data for your projects—ready to use in seconds._

---

## 📦 Installation

```bash
pip install imdbinfo
```

That’s all you need.

---

## ⚙️ Quick Start

Here's how you can use it in a Python script:

```python
from imdbinfo import search_title, get_movie, get_name, get_season_episodes

# Search for a title
results = search_title("The Matrix")
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")

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

---

## 📺 Working with Series and Episodes

The `movie` object provides helpful methods to identify its type:

- `movie.is_series()` — Returns `True` if the movie is a series.
- `movie.is_episode()` — Returns `True` if the movie is an episode.

Depending on the type, you can access additional information:

- For series: use `movie.info_series` to get series details.
- For episodes: use `movie.info_episode` to get episode details.

### Example: Series and Episodes

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

### 🆕 New: get filmography with images 🎬🖼️
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

More usage examples can be found in the [examples folder](https://github.com/tveronesi/imdbinfo/tree/main/examples).

---

## 🤔 Why Choose imdbinfo?

- ✅ No API keys or auth needed  
- ⚡ Blazing fast with `niquests` + `lxml`  
- 🎯 Cleanly typed with [Pydantic](https://docs.pydantic.dev)  
- 🧪 Great for automation, data science, or bots  
- 🪶 Lightweight and dependency-minimal  

Whether you're building a movie catalog, a Telegram bot, or just scraping your favorite actors' filmographies — `imdbinfo` is built to be intuitive and developer-friendly.

And if you want a REST API based on this package, check out [qdMovieAPI](https://github.com/tveronesi/qdMovieAPI) — a fast and simple way to access IMDb data via REST!

---

## 🛠 Under the Hood

- Built using `niquests` and `lxml` for fast scraping  
- Uses [Pydantic](https://docs.pydantic.dev) for typing and validation  
- No tracking, no telemetry, no nonsense  

---

## 💬 Feedback Welcome

I’m actively maintaining the project and open to improvements. Want to add support for series or images? Spot a bug? Just open a PR or issue.

⭐ If you like it, drop a star on [GitHub](https://github.com/tveronesi/imdbinfo) — it helps!

---

## 🔗 Resources

- GitHub: [tveronesi/imdbinfo](https://github.com/tveronesi/imdbinfo)  
- PyPI: [`imdbinfo`](https://pypi.org/project/imdbinfo/)  
- License: MIT  
- Contributions: Welcome!
