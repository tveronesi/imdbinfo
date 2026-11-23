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

## Caching & multi-locale retention

HTTP responses (HTML scraping) and GraphQL API requests are cached in memory using `@lru_cache(maxsize=1024)` at the transport layer:
- **HTML scraping** (`request_json_url`): Keyed by URL, which embeds the requested locale path segment (e.g. `/it/` vs `/`).
- **GraphQL queries** (`request_graphql_url`): Keyed by the serialized query payload and request headers (including the `x-imdb-user-country` header).

Because both caches naturally incorporate the locale, responses for different locales coexist in memory simultaneously without cache collisions or thrashing. Setting a new global locale with `set_locale()` does not clear the cache by default, allowing efficient multi-language workflows in long-running processes.

To clear all in-memory LRU caches across services when a long-running process needs fresh data:

```python
from imdbinfo import clear_all_caches

clear_all_caches()
```

You can also pass `clear_cache=True` to `set_locale()` to explicitly invalidate caches upon changing locale:

```python
from imdbinfo.locale import set_locale

set_locale("it", clear_cache=True)
```
