# Locales and caching

> [!WARNING]
> **Deprecation Notice**: Passing the `locale` parameter directly to method calls is deprecated and will be removed in a future release. Always use `set_locale()` before calling library functions.

## Set a process-wide locale

Use `set_locale` before calling service functions to retrieve localized IMDb data:

```python
from imdbinfo import get_movie, search_title
from imdbinfo.locale import set_locale

set_locale("it")
movie = get_movie("tt0133093")

set_locale("es")
results = search_title("Money Heist")
```

`title` holds the original title, while `title_localized` holds the
locale-specific title when it is available. Supported values are `en`, `fr-ca`,
`fr`, `hi`, `de`, `it`, `es`, `pt`, and `es-es`. Invalid values fall back to
English.

## Clear cached data

HTTP responses and extended GraphQL queries are cached with an in-memory LRU cache
(with underlying HTTP responses cached up to 1024 entries). The cache automatically
keys entries by their complete URL (which embeds the requested locale), allowing
responses for different locales to coexist without cache thrashing.

To clear all in-memory LRU caches across services when a long-running process needs fresh data:

```python
from imdbinfo import clear_all_caches

clear_all_caches()
```

Setting a new global locale with `set_locale()` also clears dependent caches
automatically. Extended title and person data is cached internally to avoid
duplicate GraphQL requests within a process. `get_filmography` uses this
internal cache rather than exposing a `cache_clear()` method; its cache key
includes the person and selected roles. Default roles and an empty selection
share a cache entry, while an explicit list of the same roles uses a separate
entry.
