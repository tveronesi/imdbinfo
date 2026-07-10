# 🎬 imdbinfo – A Simple Python Tool to Fetch IMDb 
### Movie Series Episodes & Actor Data (No API Keys Needed)

[![PyPI Downloads](https://static.pepy.tech/badge/imdbinfo)](https://pepy.tech/projects/imdbinfo) 
[![Build Status](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/imdbinfo)](https://pypi.org/project/imdbinfo/)

Have you ever needed to grab movie or actor details from IMDb, but didn't want to deal with complicated APIs or authentication keys?

That's exactly why I built [`imdbinfo`](https://github.com/tveronesi/imdbinfo) — a lightweight, easy-to-use Python package to search and fetch structured IMDb data, **with no API keys required**.

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
- 📝 **User reviews and ratings** via `get_reviews`
- 🎭 **Movie trivia and interesting facts** via `get_trivia`
- 🗂️ **Full filmography** for actors, directors and writers via `get_filmography`
- 🛡️ **Parental guide** including content advisories via `get_parental_guide`
- 🖼️ **Media gallery** with poster images and backdrops via `get_media_gallery`
- 📝 **Typed Pydantic models** for predictable responses
- ⚡ **Built-in caching** for faster repeated requests
- 🛡️ **AWS WAF** solver in CPython for better performance
- ✅ **No API keys required**

_No complicated scraping. No API credentials. Just clean, reliable data for your projects—ready to use in seconds._

---

## 📦 Installation

```bash
pip install imdbinfo
```

That's all you need.

---

## ⚙️ Quick Start

Here's how you can use it in a Python script:

```python
from imdbinfo import search_title, get_movie, get_name, get_season_episodes, get_reviews, get_trivia

# Search for a title
results = search_title("The Matrix")
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - Rating: {movie.rating} - {movie.imdb_id}")

# Search for an exact title match
results = search_title("The Matrix", exact_match=True)
for movie in results.titles:
    print(f"{movie.title} ({movie.year})")

# Search by title and year
results = search_title("The Matrix", year=1999)
for movie in results.titles:
    print(f"{movie.title} ({movie.year})")

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

- For series: use `movie.info_series` to get series details (creators, seasons, episodes, ...)
- For episodes: use `movie.info_episode` to get episode details 

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

### All episodes in a series

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

---

## 🏢 Company Credits

Extract information about the companies involved in a movie or series:

- Distribution companies
- Production companies
- Sales companies
- Special effects companies
- Miscellaneous companies

```python
from imdbinfo import get_movie

movie = get_movie("tt0133093")  # The Matrix

# Distribution companies
for company in movie.company_credits["distribution"]:
    print(f"Distribution: {company.name} ({company.country})")

# Production companies
for company in movie.company_credits["production"]:
    print(f"Production: {company.name}")

# Sales companies
for company in movie.company_credits["sales"]:
    print(f"Sales: {company.name}")

# Special effects companies
for company in movie.company_credits["specialEffects"]:
    print(f"Special Effects: {company.name}")

# Miscellaneous companies
for company in movie.company_credits["miscellaneous"]:
    print(f"Miscellaneous: {company.name}")
```

---

## 🌍 Alternate Titles (AKAs)

Fetch international and alternate titles for any movie or series:

```python
from imdbinfo import get_akas

akas = get_akas("tt0133093")  # The Matrix
for aka in akas["akas"][:5]:
    print(f"{aka.title} ({aka.country_name})")
```

---

## 📝 Reviews and User Ratings

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

---

## 🎭 Movie Trivia and Facts

Discover interesting trivia and behind-the-scenes facts:

```python
from imdbinfo import get_trivia

trivia = get_trivia("tt0133093")  # The Matrix
for fact in trivia[:3]:
    print(f"Interest Score: {fact['interestScore']}")
    print(f"Fact: {fact['body'][:200]}...")
    print("---")
```

---

## 🛡️ Parental Guide

Get parental guide information including content advisories, severity level, spoiler flags, and content descriptions:

```python
from imdbinfo import get_parental_guide

pg = get_parental_guide("tt0133093")  # The Matrix
for cat in pg.categories:
    print(cat)  # e.g. NUDITY - MILD (6 descriptions)
    for txt in cat.category_texts_list(spolier=True):
        print(f" - {txt.text} (SPOILER: {txt.is_spoiler})")
```

---

## 🏆 Awards

The package groups award-related counts in the `MovieDetail.awards` object (an `AwardInfo` instance):

- `wins` — number of award wins
- `nominations` — number of nominations (excluding wins)
- `prestigious_award` — optional dict containing details of a prestigious award

```python
from imdbinfo import get_movie

movie = get_movie("tt0133093")  # The Matrix
aw = movie.awards
if not aw:
    print("No award information available for this title")
else:
    print("wins:", aw.wins)
    print("nominations:", aw.nominations)
    if aw.prestigious_award:
        pa = aw.prestigious_award
        print("prestigious wins:", pa.get("wins"))
        print("prestigious nominations:", pa.get("nominations"))
    else:
        print("No prestigious award summary available")
```

---

## 🌐 Localized Results

Fetch movie details and search results in multiple languages. Locale can be set globally or per request:

```python
from imdbinfo import get_movie, search_title
from imdbinfo.locale import set_locale

# Per-request locale
movie_it = get_movie("tt0133093", locale="it")  # The Matrix in Italian

# Search in Spanish
results_es = search_title("La Casa de Papel", locale="es")

# Set locale globally
set_locale("it")
movie_it = get_movie("tt0133093")  # The Matrix in Italian
```

The `MovieBriefInfo` object includes `title_localized` — the title in the requested locale:

```python
from imdbinfo import search_title

results = search_title("The Matrix", locale="it")
for item in results.titles:
    print(item.title, "->", item.title_localized)
```

---

## 🔽 Filtering Results by Type

Filter search results server-side by title type (Movies, Series, Episodes, etc.):

```python
from imdbinfo import search_title, TitleType

# Search for movies only
results = search_title("The Matrix", title_type=TitleType.Movies)
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")

# Search for multiple types
results = search_title("The Matrix", title_type=(TitleType.Movies, TitleType.Shorts, TitleType.Video))
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")

# Exact match and year filtering
results = search_title("The Matrix", exact_match=True, year=1999)
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")
```

---

## 🗂️ Get Filmography with Images

Get filmography for actors, directors and writers with all credits and images:

```python
from imdbinfo import get_filmography

filmography = get_filmography("nm0000206")  # Brad Pitt
if filmography:
    for role, films in filmography.items():
        print(f"\nRole: {role}")
        for film in films:
            print(f" - {film.title} ({film.year}) [{film.imdbId}]")
```

---

## 🎯 Get All Interests

Fetch all interests for a title using the provided IMDb ID:

```python
from imdbinfo import get_all_interests

movies = ["tt1490017", "tt0133093"]

for imdb_id in movies:
    interests = get_all_interests(imdb_id)
    print(f"Interests for {imdb_id}: {interests}")
```

---

## 🖼️ Media Gallery

Fetch poster images and backdrops for any movie or series:

```python
from imdbinfo import get_media_gallery

gallery = get_media_gallery("tt0133093")  # The Matrix
print(f"Total images: {gallery.total}")

for item in gallery[:5]:
    print(f"[{item.type}] {item.url}")
    if item.caption:
        print(f"  Caption: {item.caption}")
    if item.source_name:
        print(f"  Source: {item.source_name}")
```

---

More usage examples can be found in the [examples folder](https://github.com/tveronesi/imdbinfo/tree/main/examples).

---

## 🤔 Why Choose imdbinfo?

- ✅ No API keys or auth needed  
- ⚡ Blazing fast with `niquests` + `lxml`  
- 🎯 Cleanly typed with [Pydantic](https://docs.pydantic.dev)  
- 🧪 Great for automation, data science, or bots  
- 🪶 Lightweight and dependency-minimal  
- 🛡️ Built-in AWS WAF bypass for reliability  

Whether you're building a movie catalog, a Telegram bot, or just scraping your favorite actors' filmographies — `imdbinfo` is built to be intuitive and developer-friendly.

And if you want a REST API based on this package, check out [qdMovieAPI](https://github.com/tveronesi/qdMovieAPI) — a fast and simple way to access IMDb data via REST!

---

## 🛠 Under the Hood

- Built using `niquests` and `lxml` for fast scraping  
- Uses [Pydantic](https://docs.pydantic.dev) for typing and validation  
- GraphQL API for rich data (search, reviews, trivia, filmography)  
- No tracking, no telemetry, no nonsense  

---

## 💬 Feedback Welcome

I'm actively maintaining the project and open to improvements. Want to add support for series or images? Spot a bug? Just open a PR or issue.

⭐ If you like it, drop a star on [GitHub](https://github.com/tveronesi/imdbinfo) — it helps!

---

## 🔗 Resources

- GitHub: [tveronesi/imdbinfo](https://github.com/tveronesi/imdbinfo)  
- PyPI: [`imdbinfo`](https://pypi.org/project/imdbinfo/)  
- License: MIT  
- Contributions: Welcome!
