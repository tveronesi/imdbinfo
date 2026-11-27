# imdbinfo

[![PyPI Downloads](https://static.pepy.tech/badge/imdbinfo)](https://pepy.tech/projects/imdbinfo)
[![PyPI Version](https://img.shields.io/pypi/v/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
[![Build Status](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://github.com/tveronesi/imdbinfo/blob/main/LICENSE)

**A modern, fully-typed Python library for IMDb data.** Search movies, TV series, episodes, and people, and fetch rich Pydantic-validated metadata in seconds — **with no API keys or credentials required**.

[Documentation](https://tveronesi.github.io/imdbinfo/) · [PyPI](https://pypi.org/project/imdbinfo/) · [REST API (qdMovieAPI)](#-rest-api-qdmovieapi) · [Release Notes & Deprecations](#-release-notes--deprecations)

---

## 📦 Installation

```bash
pip install imdbinfo
```

## 🚀 Quick Start

```python
from imdbinfo import search_title, get_movie, get_name

# 1. Search for a title
results = search_title("The Matrix")
for item in results.titles[:2]:
    print(f"{item.title} ({item.year}) - {item.imdbId}")

# 2. Get detailed movie metadata (Pydantic model)
movie = get_movie("tt0133093")  # or numeric ID '0133093'
print(f"{movie.title} ({movie.year}) — {movie.rating}/10 ({movie.votes:,} votes)")
print(f"Director: {', '.join(d.name for d in movie.directors)}")
print(f"Plot: {movie.plot}")

# 3. Get person details
person = get_name("nm0000206")  # Keanu Reeves (or '0000206')
print(f"{person.name} (Born: {person.birth_date})")
print(f"Known For: {', '.join(person.knownfor)}")
```

**Output:**

```text
The Matrix (1999) - tt0133093
The Matrix Reloaded (2003) - tt0234215
The Matrix (1999) — 8.7/10 (2,100,000+ votes)
Director: Lana Wachowski, Lilly Wachowski
Plot: When a beautiful stranger leads computer hacker Neo to a forbidding underworld...
Keanu Reeves (Born: 1964-09-02)
Known For: The Matrix, John Wick, Speed, Constantine
```

---

## ❓ Why imdbinfo?

- 🔓 **Zero Setup & Keyless** — Works out of the box with no API accounts, tokens, or authentication hurdles.
- 🧩 **Pydantic-Native & Fully Typed** — Responses are validated into clean [Pydantic](https://docs.pydantic.dev/) models with full IDE autocompletion.
- ⚡ **Fast by Default** — Built-in LRU caching keeps repeated lookups instant.
- 🎯 **Built for Real-World IMDb Quirks** — Smart `CreditRole` filtering prevents minor credits from crowding out main works under IMDb's 250-item GraphQL limit.
- 🌐 **Multi-Language Ready** — Global localization via `set_locale()` for titles, awards, and metadata.

---

## ✨ What You Can Fetch

| Category | Functions | Highlights |
| :--- | :--- | :--- |
| **Search** | `search_title` | Movies, series, episodes, and people with exact-match, year, and `TitleType` filters |
| **Titles** | `get_movie`, `get_akas`, `get_all_interests` | Cast, crew, ratings, box office, plot, company credits, international AKAs, themes |
| **TV & Episodes** | `get_season_episodes`, `get_all_episodes` | Season breakdowns, episode metadata, and single-call bulk episode retrieval |
| **People** | `get_name`, `get_filmography` | Biographies, personal details, and role-filtered filmographies (`CreditRole`) |
| **Extras** | `get_awards`, `get_quotes`, `get_media_gallery` | Award histories, character dialogue with speaker attribution, posters & backdrops |
| **Community** | `get_parental_guide`, `get_reviews`, `get_trivia` | Spoiler-flagged advisories, user reviews with ratings, behind-the-scenes trivia |

> 📖 **Full API Reference:** Check out the [published documentation](https://tveronesi.github.io/imdbinfo/) for complete model schemas and advanced usage.

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

# Filter by a single type (e.g., Movies only)
results = search_title("The Matrix", title_type=TitleType.Movies)

# Filter by multiple types (Movies, Shorts, Video)
results = search_title(
    "The Matrix",
    title_type=(TitleType.Movies, TitleType.Shorts, TitleType.Video),
)

for title in results.titles:
    print(f"{title.title} ({title.year}) [{title.kind}] - {title.imdbId}")

for person in results.names:
    print(f"Person: {person.name} ({person.job}) - {person.imdbId}")
```

Available `TitleType` filters: `TitleType.Movies`, `TitleType.Series`, `TitleType.Episodes`, `TitleType.Shorts`, `TitleType.TvMovie`, `TitleType.Video`.

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

### 👤 People & Filmographies

Fetch comprehensive details and credit histories for actors, directors, writers, and crew:

```python
from imdbinfo import get_name, get_filmography, CreditRole

# Detailed person profile
person = get_name("nm0000206")  # Keanu Reeves
print(f"Name: {person.name}")
print(f"Birth: {person.birth_date} in {person.birth_place}")
print(f"Bio: {person.bio}")
print(f"Professions: {', '.join(person.primary_profession)}")

# 1. Main filmography by default (actor, actress, director, writer, cinematographer, composer)
filmography = get_filmography("nm0000206")
for role, titles in filmography.items():
    print(f"\nRole: {role} ({len(titles)} titles)")
    for t in titles[:3]:
        print(f" - {t.title} ({t.year}) [{t.kind}] - {t.imdbId}")

# 2. Filter specific roles using the CreditRole enum
credits = get_filmography(
    "nm0000206",
    roles=[CreditRole.ACTOR, CreditRole.DIRECTOR],
)
```

### 🌐 Multi-Language Localization

Localize search results and title metadata globally across the library by calling `set_locale()` before making requests:

```python
from imdbinfo import get_movie, search_title, get_awards
from imdbinfo.locale import set_locale

# 1. Set locale before calling methods
set_locale("it")
movie_it = get_movie("tt0133093")    # Italian title & metadata
awards_it = get_awards("tt0034583")  # Italian awards

# 2. Switch locale for other requests
set_locale("es")
results_es = search_title("Money Heist")  # Spanish search

# 3. Access localized title properties
set_locale("it")
results = search_title("The Matrix")
for item in results.titles:
    print(f"Original: {item.title} -> Localized: {item.title_localized}")
```

---

### 🧩 More Data & Specialized Endpoints

Click any section below to expand code examples and model details:

<details>
<summary><strong>🏆 Awards &amp; Nominations (<code>get_awards</code>)</strong></summary>

Fetch complete awards and nominations history via `get_awards`, or inspect summary statistics on movie details:

```python
from imdbinfo import get_awards, get_movie

# Detailed list of all awards and nominations
awards = get_awards("tt0034583")  # Casablanca
print(f"Total awards/nominations: {len(awards)}")
for award in awards[:5]:
    print(f"Event: {award.event}")
    print(f"Status: {award.status}")        # e.g. '1944 Winner'
    print(f"Award: {award.award}")          # e.g. 'Oscar'
    print(f"Category: {award.category}")    # e.g. 'Best Picture'
    print(f"Nominees: {award.nominees}")    # e.g. 'Michael Curtiz'
    print("---")

# Summary counts from movie detail
movie = get_movie("tt0133093")  # The Matrix
if movie.awards:
    print(f"Total Wins: {movie.awards.wins}")
    print(f"Total Nominations: {movie.awards.nominations}")
    if movie.awards.prestigious_award:
        print(f"Prestigious Award: {movie.awards.prestigious_award.get('name')}")
```

**`Award` Model Fields:**

| Field | Description | Example |
| :--- | :--- | :--- |
| `event` | Award event or organization name | `"Academy Awards, USA"` |
| `status` | Year and outcome status | `"1944 Winner"`, `"2017 Nominee"` |
| `award` | Name of the award | `"Oscar"`, `"BAFTA Film Award"` |
| `category` | Specific award category | `"Best Picture"`, `"Best Director"` |
| `nominees` | Nominees associated with the entry | `"Humphrey Bogart"`, `"Michael Curtiz"` |

</details>

<details>
<summary><strong>💬 Character Quotes (<code>get_quotes</code>)</strong></summary>

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

**`Quote` Model Overview:**

| Model | Description | Key Attributes / Properties |
| :--- | :--- | :--- |
| `Quote` | Complete dialogue exchange | `id`, `lines` (`List[QuoteLine]`), `interest_score` (`InterestScore`), `speakers`, `len()`, `str()` |
| `QuoteLine` | Single spoken dialogue line | `characters` (`List[QuoteCharacter]`), `text`, `stage_direction`, `speaker_names`, `str()` |
| `QuoteCharacter` | Character & actor attribution | `character` (character name), `id` (person numeric ID), `imdbId` (`nm...` ID) |
| `InterestScore` | Community voting metrics | `users_interested`, `users_voted` |

</details>

<details>
<summary><strong>🖼️ Media Gallery (<code>get_media_gallery</code>)</strong></summary>

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

</details>

<details>
<summary><strong>🛡️ Parental Guide (<code>get_parental_guide</code>)</strong></summary>

Access content advisories, community severity ratings, and spoiler-flagged descriptive items:

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
            print(f" - {text}")

        # Or inspect detailed item objects with spoiler flags
        for item in cat.content_descriptions:
            if item.is_spoiler:
                print(f" - [SPOILER] {item.text}")
```

</details>

<details>
<summary><strong>🏢 Company Credits (<code>movie.company_credits</code>)</strong></summary>

Extract categorized details of all companies involved in a production (`distribution`, `production`, `sales`, `specialEffects`, and `miscellaneous`):

```python
from imdbinfo import get_movie

movie = get_movie("tt0133093")  # The Matrix
for category, companies in movie.company_credits.items():
    print(f"\n{category.capitalize()} Companies:")
    for company in companies:
        countries = f" ({', '.join(company.countries)})" if company.countries else ""
        print(f" - {company.name}{countries} [{company.imdbId}]")
```

</details>

<details>
<summary><strong>🗺️ Alternate Titles / AKAs (<code>get_akas</code>)</strong></summary>

Retrieve international release titles and country-specific translations:

```python
from imdbinfo import get_akas

akas = get_akas("tt0133093")  # The Matrix
for aka in akas.akas[:5]:
    lang = f" ({aka.language_name})" if aka.language_name else ""
    print(f"{aka.title} — {aka.country_name}{lang}")
```

</details>

<details>
<summary><strong>📝 User Reviews &amp; Movie Trivia (<code>get_reviews</code>, <code>get_trivia</code>)</strong></summary>

Access user reviews with ratings and vote counts, alongside behind-the-scenes trivia *(note: these endpoints currently return structured dictionaries)*:

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
    print(f"Interested: {score.get('usersInterested', 0)} / {score.get('usersVoted', 0)}")
    print(f"Fact: {fact['body'][:200]}...")
    print("---")
```

</details>

<details>
<summary><strong>🏷️ Interests &amp; Themes (<code>get_all_interests</code>)</strong></summary>

Fetch all interests and thematic tags associated with a title:

```python
from imdbinfo import get_all_interests

interests = get_all_interests("tt0133093")  # The Matrix
print(interests)
```

</details>

---

## 🌐 REST API (qdMovieAPI)

Need to access IMDb data over HTTP from another language or service?

Check out **[qdMovieAPI](https://github.com/tveronesi/qdMovieAPI)** — a fast, lightweight FastAPI microservice wrapper built on top of `imdbinfo`, supporting localized queries out of the box.

---

## 📢 Release Notes & Deprecations

> [!IMPORTANT]
> **Smart Filmography Role Filtering (`CreditRole`)**
> `get_filmography` now extracts main credits by default (`actor`, `actress`, `cinematographer`, `director`, `writer`, `composer`) instead of fetching all miscellaneous categories.
>
> **Why this matters:** IMDb enforces a hard limit of 250 items per GraphQL response. Querying all categories indiscriminately causes minor roles (e.g., *Self*, *Thanks*, *Soundtrack*, *Archive footage*) to exhaust the quota and drop career-defining works — for example, *Citizen Kane* was previously crowded out of Orson Welles' filmography! You can still selectively request any roles via `roles=[CreditRole.ACTOR, CreditRole.DIRECTOR]`.

> [!WARNING]
> **Deprecated Notice**
> - **`locale` Method Parameter:** Passing `locale` as a parameter directly to method calls (e.g. `get_movie("tt0133093", locale="it")`) is deprecated and will be removed in a future release. Always call `set_locale()` before calling library functions.
> - **`get_episodes()` Function:** The legacy `get_episodes()` function is deprecated. Use `get_season_episodes()` for a specific season or `get_all_episodes()` to retrieve all episodes across seasons.

For the full version history, see the [GitHub Releases](https://github.com/tveronesi/imdbinfo/releases) page.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an [issue](https://github.com/tveronesi/imdbinfo/issues) or submit a [pull request](https://github.com/tveronesi/imdbinfo/pulls) on GitHub.

If you find `imdbinfo` useful, consider giving the repository a ⭐!

---

## 📄 License & Disclaimer

This project is licensed under the **MIT License** — see the [LICENSE](https://github.com/tveronesi/imdbinfo/blob/main/LICENSE) file for details.

> [!NOTE]
> **Disclaimer & Terms of Use:** `imdbinfo` is an independent, unofficial open-source project and is not affiliated with, endorsed by, or connected to IMDb or Amazon. Please use this library responsibly and respect IMDb's Terms of Service. For more information, refer to the [DISCLAIMER](https://github.com/tveronesi/imdbinfo/blob/main/DISCLAIMER) file.