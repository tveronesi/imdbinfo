# Getting started

## Install imdbinfo

Install the published package from PyPI:

```bash
pip install imdbinfo
```

No IMDb key, account, or client configuration is required.

## Find a title

`search_title` returns both title and person matches. Supply a year, an exact
match flag, or a `TitleType` filter when the query is ambiguous.

```python
from imdbinfo import TitleType, search_title

results = search_title(
    "The Matrix",
    year=1999,
    exact_match=True,
    title_type=TitleType.Movies,
)

for title in results.titles:
    print(title.imdbId, title.title, title.year)
```

## Retrieve details

Use the IMDb ID returned by search to fetch a complete title record:

```python
from imdbinfo import get_movie

movie = get_movie("tt0133093")
print(movie.title)
print(movie.plot)
print(movie.rating)
```

Title and name IDs accept both prefixed and numeric forms. For example,
`"tt0133093"` and `"0133093"` identify the same title.

## Understand title kinds

`get_movie` returns a `MovieDetail` subtype. Check its kind before accessing
series- or episode-specific fields:

```python
series = get_movie("tt1520211")

if series.is_series():
    print(series.info_series.display_seasons)
elif series.is_episode():
    print(series.info_episode)
```

Continue with the [search guide](guides/search.md), or consult the
[services reference](api/services.md) for every available operation.
