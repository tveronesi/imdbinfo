# imdbinfo

[![PyPI Downloads](https://static.pepy.tech/badge/imdbinfo)](https://pepy.tech/projects/imdbinfo)
[![PyPI Version](https://img.shields.io/pypi/v/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
[![Build Status](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

**Your personal gateway to IMDb data**. Search for movies, TV series, episodes, and people, and fetch rich structured metadata in seconds — **with no API keys or credentials required**.

---

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
- ⚡ **High Performance** — Native CPython AWS WAF solver, built-in LRU caching, and HTTP/2 transport.
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

`imdbinfo` provides a structured exception hierarchy for resilient integration:

```python
from imdbinfo import get_movie
from imdbinfo.exceptions import (
    ImdbinfoError,
    HTTPError,
    WAFError,
    GraphQLError,
    ParseError,
)

try:
    movie = get_movie("tt0133093")
except WAFError as e:
    print(f"AWS WAF challenge blocked request ({e.status_code}): {e.url}")
except HTTPError as e:
    print(f"HTTP request error ({e.status_code}) for URL: {e.url}")
except GraphQLError as e:
    print(f"IMDb GraphQL query error for {e.query_term}: {e.errors}")
except ParseError as e:
    print(f"Failed to parse page content: {e}")
except ImdbinfoError as e:
    print(f"Generic imdbinfo error: {e}")
```

---

## 💡 REST API (qdMovieAPI)

Looking for a production-ready HTTP REST API powered by `imdbinfo`? Check out [**qdMovieAPI**](https://github.com/tveronesi/qdMovieAPI) — a fast, lightweight REST microservice wrapper for IMDb data.

---

## ❓ Why Choose imdbinfo?

- ⚡ **Zero Setup & Keyless** — Works instantly without registering API accounts or managing API tokens.
- 🚀 **CPython WAF Solver** — Built-in AWS WAF token solving via `imdbinfo-aws` ensures high reliability.
- 🏎️ **Fast & Lightweight** — Utilizes HTTP/2-enabled requests via `niquests`, fast parsing with `lxml`, and in-memory LRU caching.
- 🛡️ **Fully Typed** — Pydantic models guarantee consistent structures, field validation, and rich editor autocompletion.
- 🧪 **Thoroughly Tested** — Reliable test suite covering real-world IMDb structures and edge cases.

---

## ⚠️ Disclaimer

This project and its authors are not affiliated with, endorsed by, or sponsored by IMDb.com, Inc. or Amazon.com. All product and company names are trademarks or registered trademarks of their respective holders. For more details, see [DISCLAIMER.txt](DISCLAIMER.txt).

---

## 🤝 Contributing

Contributions are warmly welcomed! Feel free to report issues, submit feature requests, or open pull requests.

Please review our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting contributions.

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

`imdbinfo` is distributed under the terms of the [MIT License](LICENSE).
