# imdbinfo

[![PyPI version](https://img.shields.io/pypi/v/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
[![Python versions](https://img.shields.io/pypi/pyversions/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg?style=flat-square)](https://github.com/tveronesi/imdbinfo/blob/main/LICENSE)

`imdbinfo` is a Python library for retrieving structured IMDb data without an
API key. Search for titles and people, retrieve title and person details, and
work with episodes, awards, quotes, reviews, trivia, media, and more.

## Install

```bash
pip install imdbinfo
```

The package supports Python 3.10 through 3.13.

## Quick start

```python
from imdbinfo import get_movie, get_name, search_title

results = search_title("The Matrix", year=1999)
for title in results.titles:
    print(title.imdbId, title.title)

movie = get_movie("tt0133093")
print(movie.title, movie.rating, movie.duration)

person = get_name("nm0000206")
print(person.name, person.primary_profession)
```

IMDb title and name IDs may be supplied with or without their `tt` or `nm`
prefix. The library normalizes them before making a request.

## Explore the documentation

- Start with [Getting started](getting-started.md) for a fuller introduction.
- Read the [guides](guides/search.md) for focused usage examples.
- Use the generated [API reference](api/index.md) for function signatures and
  model fields.

!!! note
    imdbinfo retrieves data from IMDb at runtime. Returned data can vary as
    IMDb changes its public pages and GraphQL responses.
