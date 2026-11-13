# imdbinfo

[![PyPI Downloads](https://static.pepy.tech/badge/imdbinfo)](https://pepy.tech/projects/imdbinfo)
[![PyPI Version](https://img.shields.io/pypi/v/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
[![Build Status](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://github.com/tveronesi/imdbinfo/blob/main/LICENSE)

**Your personal gateway to IMDb data**. Search for movies, TV series, episodes, and people, and fetch rich structured metadata in seconds — **with no API keys or credentials required**.

---

## Documentation

The published documentation is available at
[tveronesi.github.io/imdbinfo](https://tveronesi.github.io/imdbinfo/).

## ✨ Features

- 🔍 **Title & Person Search** — Search movies, series, miniseries, episodes, and people with exact-match, year, and type filters.
- 🎬 **Comprehensive Title Details** — Cast, crew, ratings, box office, release dates, runtime, plot summaries, and technical specs.
- 👤 **Detailed Person Information** — Biographies, personal details, jobs, and full filmographies with poster images.
- 📺 **TV Series & Episode Management** — Season-by-season breakdowns, episode info, and bulk episode retrieval.
- 🌐 **Multi-Language Localization** — Fetch localized titles and metadata (set globally or per request).
- 🗺️ **Alternate Titles (AKAs)** — Country-specific and international release titles via `get_akas`.
- 🏆 **Awards & Nominations** — Complete award event histories, nominees, and summary counts via `get_awards`.
- 💬 **Character Quotes** — Dialogue lines, character speaker attributions, and interest scores via `get_quotes`.
- 🖼️ **Media Gallery** — Posters and backdrops with captions, dimensions, and attribution sources via `get_media_gallery`.
- 🛡️ **Parental Guide** — Content advisories, severity classifications, and spoiler-flagged descriptions via `get_parental_guide`.
- 📝 **Reviews & Trivia** — User reviews with ratings and behind-the-scenes trivia via `get_reviews` and `get_trivia`.
- 🏢 **Company Credits** — Distribution, production, sales, VFX, and miscellaneous companies.
- 🧩 **Type Safety** — Clean [Pydantic](https://docs.pydantic.dev/) models with full IDE autocompletion.
- ⚡ **High Performance** — Built-in LRU caching and efficient data access.
- 🔓 **No API Keys Required** — Out-of-the-box operation with zero authentication setup.

---

## 📦 Installation

```bash
pip install imdbinfo
```

---

## 🚀 Quick Start

```python
from imdbinfo import search_title, get_movie, get_name

# 1. Search for a title
results = search_title("The Matrix")
for item in results.titles:
    print(f"{item.title} ({item.year}) - Rating: {item.rating} - {item.imdbId}")

# 2. Get detailed movie information
movie = get_movie("tt0133093")  # or numeric ID '0133093'
print(f"Title: {movie.title} ({movie.year})")
print(f"Rating: {movie.rating}/10 ({movie.votes:,} votes)")
print(f"Director: {', '.join(d.name for d in movie.directors)}")
print(f"Plot: {movie.plot}")

# 3. Get person details
person = get_name("nm0000206")  # Keanu Reeves (or '0000206')
print(f"Name: {person.name}")
print(f"Birth Date: {person.birth_date}")
print(f"Known For: {', '.join(person.knownfor)}")
```

---

## ⚙️ Configuration

Configure the default locale, proxies, and result limits through the shared
`config`, helper functions, or `IMDBINFO_` environment variables (including a
`.env` file):

```python
from imdbinfo import (
    config,
    configure,
    get_locale,
    get_max_items,
    get_proxy,
    set_locale,
    set_max_items,
    set_proxy,
)

set_locale("it")
set_proxy("[http://proxy.example:8080](http://proxy.example:8080)")
set_max_items(search=25, akas=300)

print(get_locale())             # "it"; English is returned as ""
print(get_proxy())              # mapping for HTTP and HTTPS
print(get_max_items("akas"))    # 300; get_max_items() returns all limits

# Alternative runtime access:
config.locale = "it"
config.proxies = {"https": "[http://proxy.example:8080](http://proxy.example:8080)"}
configure(max_items_search=25, max_items_akas=300)
print(config.max_items_akas)
```

The helpers can also be imported from `imdbinfo.helpers`. For **backward
compatibility**, `from imdbinfo.locale import set_locale, get_locale` still
works. Pass `locale=` to a supported function to override the global locale
for one call.

A proxy URL applies to both HTTP and HTTPS; use a mapping for individual
protocols or `set_proxy(None)` to clear it. Reassign `config.proxies` instead
of modifying its mapping in place so validation and cache invalidation run.
Changing global settings clears dependent caches.

Environment variables such as `IMDBINFO_LOCALE=it`,
`IMDBINFO_PROXIES=http://proxy.example:8080`, and
`IMDBINFO_MAX_ITEMS_AKAS=300` are read when the configuration is initialized.
`reset_config()` restores those initial values.

Each result type has an independent positive-integer limit. The functions below
also accept `max_items=` to override their own limit for one call without
changing the global configuration:

| Function | Setting | Default |
|---|---|---:|
| `search_title` | `max_items_search` | 50 |
| `get_media_gallery` | `max_items_images` | 50 |
| `get_all_interests` | `max_items_interests` | 20 |
| `get_akas` | `max_items_akas` | 200 |
| `get_trivia` | `max_items_trivia` | 50 |
| `get_reviews` | `max_items_reviews` | 50 |
| `get_parental_guide` | `max_items_guide_items` | 10 |
| `get_quotes` | `max_items_quotes` | 100 |
| `get_filmography` | `max_items_credits` | 250 |

```python
from imdbinfo import get_akas, search_title

results = search_title("The Matrix", max_items=10)
akas = get_akas("tt0133093", max_items=500)
```

See the [configuration guide](https://github.com/tveronesi/imdbinfo/blob/main/docs/guides/locales-and-caching.md) for supported
locales and more details.

---

## 📖 Usage Guide

### 🔍 Searching Titles & Filtering

Search titles and names across IMDb with support for type filtering, exact matching, and release year constraints:

```python
from imdbinfo import search_title, TitleType

# Basic search
results = search_title("The Matrix")

# Search with exact title matching
results = search_title("The Matrix", exact_match=True)

# Search filtered by release year
results = search_title("The Matrix", year=1999)

# Filter by a single type (e.g. Movies only)
results = search_title("The Matrix", title_type=TitleType.Movies)

# Filter by multiple types (Movies, Shorts, Video)
results = search_title(
    "The Matrix",
    title_type=(TitleType.Movies, TitleType.Shorts, TitleType.Video)
)

for title in results.titles:
    print(f"{title.title} ({title.year}) [{title.kind}] - {title.imdbId}")

for person in results.names:
    print(f"Person: {person.name} ({person.job}) - {person.imdbId}")
```

Available `TitleType` filters: `TitleType.Movies`, `TitleType.Series`, `TitleType.Episodes`, `TitleType.Shorts`, `TitleType.TvMovie`, `TitleType.Video`.

---

### 📺 TV Series & Episodes

`MovieDetail` provides helper methods to inspect title types and access specialized metadata:

- `movie.is_series()` — Returns `True` for TV series, miniseries, and podcast series (`movie.info_series`).
- `movie.is_episode()` — Returns `True` for TV episodes and podcast episodes (`movie.info_episode`).

```python
from imdbinfo import get_movie, get_season_episodes, get_all_episodes

# Fetch a TV series
series = get_movie("tt1520211")  # The Walking Dead
print(f"Is Series: {series.is_series()}")
if series.info_series:
    print(f"Seasons: {len(series.info_series.display_seasons)}")
    print(f"Creators: {', '.join(c.name for c in series.info_series.creators)}")

# Fetch all episodes for a specific season
season_1 = get_season_episodes(series.imdb_id, season=1)
print(f"Season 1 episode count: {season_1.count}")
for ep in season_1.episodes[:3]:
    print(f"S{ep.season:02d}E{ep.episode:02d}: {ep.title} (Rating: {ep.rating}) - {ep.imdbId}")

# Fetch a specific episode as a detailed Movie object
episode = get_movie(season_1.episodes[0].imdb_id)
print(f"Is Episode: {episode.is_episode()}")
if episode.info_episode:
    print(f"Episode Info: {episode.info_episode}")

# Retrieve ALL episodes across all seasons in a single call
all_episodes = get_all_episodes("tt1520211")
for ep in all_episodes[:5]:
    duration_min = f"{ep.duration / 60:.0f}m" if ep.duration else "N/A"
    print(f"{ep.title} (S{ep.season_number}E{ep.episode_number}) - {ep.rating}/10 ({duration_min})")
```

---

### 👤 People & Filmographies

Fetch comprehensive details and complete credit histories for actors, directors, writers, and crew:

```python
from imdbinfo import get_name, get_filmography

# Detailed person profile
person = get_name("nm0000206")  # Keanu Reeves
print(f"Name: {person.name}")
print(f"Birth: {person.birth_date} in {person.birth_place}")
print(f"Bio: {person.bio}")
print(f"Professions: {', '.join(person.primary_profession)}")

# Full filmography categorized by role
filmography = get_filmography("nm0000206")
for role, titles in filmography.items():
    print(f"\nRole: {role} ({len(titles)} titles)")
    for t in titles[:3]:
        print(f"  - {t.title} ({t.year}) [{t.kind}] - {t.imdbId}")
```

---

### 🌐 Multi-Language Localization

Localize search results and title metadata per request or globally across the library:

```python
from imdbinfo import get_movie, search_title, get_awards
from imdbinfo.locale import set_locale

# 1. Per-request locale
movie_it = get_movie("tt0133093", locale="it")  # Italian title & metadata
results_es = search_title("Money Heist", locale="es")  # Spanish search
awards_it = get_awards("tt0034583", locale="it")

# 2. Set default locale globally
set_locale("it")
movie = get_movie("tt0133093")  # Automatically fetched in Italian

# 3. Access localized title properties
results = search_title("The Matrix", locale="it")
for item in results.titles:
    print(f"Original: {item.title} -> Localized: {item.title_localized}")
```

---

### 🏆 Awards & Nominations

Fetch complete awards and nominations history via `get_awards`, or inspect summary statistics on movie details:

```python
from imdbinfo import get_awards, get_movie

# Detailed list of all awards and nominations
awards = get_awards("tt0034583")  # Casablanca
print(f"Total awards/nominations: {len(awards)}")
for award in awards[:5]:
    print(f"Event: {award.event}")
    print(f"Status: {award.status}")      # e.g. '1944 Winner'
    print(f"Award: {award.award}")        # e.g. 'Oscar'
    print(f"Category: {award.category}")  # e.g. 'Best Picture'
    print(f"Nominees: {award.nominees}")  # e.g. 'Michael Curtiz'
    print("---")

# Summary counts from movie detail
movie = get_movie("tt0133093")  # The Matrix
if movie.awards:
    print(f"Total Wins: {movie.awards.wins}")
    print(f"Total Nominations: {movie.awards.nominations}")
    if movie.awards.prestigious_award:
        print(f"Prestigious Award: {movie.awards.prestigious_award.get('name')}")
```

**Award Model Fields:**

| Field | Description | Example |
|---|---|---|
| `event` | Award event or organization name | `"Academy Awards, USA"` |
| `status` | Year and outcome status | `"1944 Winner"`, `"2017 Nominee"` |
| `award` | Name of the award | `"Oscar"`, `"BAFTA Film Award"` |
| `category` | Specific award category | `"Best Picture"`, `"Best Director"` |
| `nominees` | Nominees associated with the entry | `"Humphrey Bogart"`, `"Michael Curtiz"` |

---

### 💬 Character Quotes

Fetch iconic dialogue and character quotes with structured speaker attribution and community popularity scores:

```python
from imdbinfo import get_quotes

quotes = get_quotes("tt0133093")  # The Matrix
for quote in quotes[:3]:
    print(f"Quote ID: {quote.id}")
    print(f"Speakers: {', '.join(quote.speakers)}")
    print(f"Interest Score: {quote.interest_score.users_interested} / {quote.interest_score.users_voted} votes")
    
    # Iterate over dialogue lines
    for line in quote.lines:
        print(f"  {line}")  # e.g. "[Neo]: What truth?"
    print("---")
```

**Quote Model Overview:**

| Model | Description | Key Attributes / Properties |
|---|---|---|
| `Quote` | Complete dialogue exchange | `id`, `lines` (`List[QuoteLine]`), `interest_score` (`InterestScore`), `speakers` (list of names), `len()`, `str()` |
| `QuoteLine` | Single spoken dialogue line | `characters` (`List[QuoteCharacter]`), `text`, `stage_direction`, `speaker_names`, `str()` |
| `QuoteCharacter` | Character & actor attribution | `character` (character name), `id` (person numeric ID), `imdbId` (`nm...` ID) |
| `InterestScore` | Community voting metrics | `users_interested`, `users_voted` |

---

### 🖼️ Media Gallery

Fetch full poster collections, backdrops, and promotional stills with dimensions and source attribution:

```python
from imdbinfo import get_media_gallery

gallery = get_media_gallery("tt0133093")  # The Matrix
if gallery:
    print(f"Total images: {gallery.total}")
    for item in gallery.items[:5]:
        print(f"[{item.type}] {item.width}x{item.height}: {item.url}")
        if item.caption:
            print(f"  Caption: {item.caption}")
        if item.source_name:
            print(f"  Source: {item.source_name} ({item.source_url})")
```

---

### 🛡️ Parental Guide

Access content advisories, community severity ratings, and descriptive items:

```python
from imdbinfo import get_parental_guide

pg = get_parental_guide("tt0133093")  # The Matrix
if pg:
    # Summary of severity ratings across all categories
    print("Severity Summary:", pg.summary)

    for cat in pg.categories:
        print(f"\nCategory: {cat.id} - Severity: {cat.severity} ({len(cat.content_descriptions)} items)")
        
        # Access spoiler-free advisory texts
        for text in cat.category_texts_list(spoiler=False):
            print(f"  - {text}")
            
        # Or inspect detailed item objects with spoiler flags
        for item in cat.content_descriptions:
            if item.is_spoiler:
                print(f"  - [SPOILER] {item.text}")
```

---

### 🏢 Company Credits

Extract categorized details of all companies involved in a production:

```python
from imdbinfo import get_movie

movie = get_movie("tt0133093")  # The Matrix

for category, companies in movie.company_credits.items():
    print(f"\n{category.capitalize()} Companies:")
    for company in companies:
        countries = f" ({', '.join(company.countries)})" if company.countries else ""
        print(f"  - {company.name}{countries} [{company.imdbId}]")
```

Categories include: `distribution`, `production`, `sales`, `specialEffects`, and `miscellaneous`.

---

### 🗺️ Alternate Titles (AKAs)

Retrieve international release titles and country-specific translations:

```python
from imdbinfo import get_akas

akas = get_akas("tt0133093")  # The Matrix
for aka in akas.akas[:5]:
    lang = f" ({aka.language_name})" if aka.language_name else ""
    print(f"{aka.title} — {aka.country_name}{lang}")
```

---

### 📝 User Reviews & Movie Trivia

Access user reviews with ratings and vote counts, alongside behind-the-scenes trivia:

```python
from imdbinfo import get_reviews, get_trivia

# User reviews
reviews = get_reviews("tt0133093")
for review in reviews[:3]:
    print(f"Rating: {review['authorRating']}/10 | Summary: {review['summary']}")
    print(f"Votes: {review['upVotes']} up / {review['downVotes']} down | Spoiler: {review['spoiler']}")
    print("---")

# Trivia and facts
trivia = get_trivia("tt0133093")
for fact in trivia[:3]:
    score = fact.get("interestScore", {})
    print(f"Interested: {score.get('usersInterested', 0)} | Fact: {fact['body'][:160]}...")
    print("---")
```

---

### 🎯 Title Interests

Fetch descriptive topic tags, thematic interests, and sub-genre classifications:

```python
from imdbinfo import get_all_interests

interests = get_all_interests("tt0133093")
print("Interests / Themes:", interests)
```

---

## 🛠️ Error Handling

`imdbinfo` provides a base exception for handling library errors:

```python
from imdbinfo import ImdbinfoError, get_movie

try:
    movie = get_movie("tt0133093")
except ImdbinfoError as e:
    print(f"imdbinfo error: {e}")
```

---

## 💡 REST API (qdMovieAPI)

Looking for a production-ready HTTP REST API powered by `imdbinfo`? Check out [**qdMovieAPI**](https://github.com/tveronesi/qdMovieAPI) — a fast, lightweight REST microservice wrapper for IMDb data.

---

## ❓ Why Choose imdbinfo?

- ⚡ **Zero Setup & Keyless** — Works instantly without registering API accounts or managing API tokens.
- 🏎️ **Fast & Lightweight** — In-memory LRU caching keeps repeated lookups responsive.
- 🛡️ **Fully Typed** — Pydantic models guarantee consistent structures, field validation, and rich editor autocompletion.
- 🧪 **Thoroughly Tested** — Reliable test suite covering real-world IMDb structures and edge cases.

---

## ⚠️ Disclaimer & Terms of Use

`imdbinfo` is an independent, unofficial open-source tool developed strictly for **personal, educational, and non-commercial use**. This project and its authors are not affiliated with, endorsed by, or sponsored by Internet Movie Database Inc. (IMDb.com) or Amazon.com, Inc.

All data retrieved through this library is the property of IMDb or its content suppliers and is subject to [IMDb’s Conditions of Use](https://www.imdb.com/conditions/). **You may not use data fetched via this library for commercial applications or commercial data redistribution** without obtaining a proper license directly from [IMDb Developer](https://developer.imdb.com/). Please respect IMDb's infrastructure and avoid aggressive or bulk scraping.

For full legal details and limitation of liability, please read [DISCLAIMER.txt](https://github.com/tveronesi/imdbinfo/blob/main/DISCLAIMER.txt).

---

## 🤝 Contributing

Contributions are warmly welcomed! Feel free to report issues, submit feature requests, or open pull requests.

Please review our [Contributing Guidelines](https://github.com/tveronesi/imdbinfo/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/tveronesi/imdbinfo/blob/main/CODE_OF_CONDUCT.md) before submitting contributions.

If you find `imdbinfo` helpful, please consider giving the repository a ⭐ on GitHub!

---

## ⭐ Star History

<a href="https://www.star-history.com/?repos=tveronesi%2Fimdbinfo&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=tveronesi/imdbinfo&type=date&theme=dark&logscale&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=tveronesi/imdbinfo&type=date&logscale&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=tveronesi/imdbinfo&type=date&logscale&legend=top-left" />
 </picture>
</a>

---

## 📄 License

`imdbinfo` is distributed under the terms of the [MIT License](https://github.com/tveronesi/imdbinfo/blob/main/LICENSE).