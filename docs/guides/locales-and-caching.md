# Locales and caching

## Choose a locale per request

Pass `locale` to supported service functions to request localized IMDb data:

```python
from imdbinfo import get_movie, search_title

movie = get_movie("tt0133093", locale="it")
results = search_title("Money Heist", locale="es")
```

`title` holds the original title, while `title_localized` holds the
locale-specific title when it is available.

## Set a process-wide locale

Use `set_locale` when an application should use one default locale:

```python
from imdbinfo import get_movie
from imdbinfo.locale import set_locale

set_locale("it")
movie = get_movie("tt0133093")
```

Supported values are `en`, `fr-ca`, `fr`, `hi`, `de`, `it`, `es`, `pt`, and
`es-es`. Invalid values fall back to English.

## Clear cached data

Many public title and person services use an LRU cache. Clear an individual
cached function when a long-running process needs fresh data:

```python
from imdbinfo import get_movie

get_movie.cache_clear()
```

The cache key includes the requested locale. Extended title and person data is
also cached internally to avoid duplicate GraphQL requests within a process.
`get_filmography` uses this internal cache rather than exposing a
`cache_clear()` method; its cache key includes the person, locale, and selected
roles. Default roles and an empty selection share a cache entry, while an
explicit list of the same roles uses a separate entry.
