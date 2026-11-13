# Locales, proxies, limits, and caching

The same settings can be managed in three ways:

1. **Environment variables or `.env`** — loaded when the shared `config`
   object is created, normally when `imdbinfo` is imported. Environment
   variables use the `IMDBINFO_` prefix.
2. **The `config` object** — read or update fields directly at runtime.
3. **Dedicated helpers** — use `set_*` and `get_*` for a consistent public
   interface. `configure()` is a bulk runtime setter for the same shared
   configuration, not a separate source of values.

The environment is not re-read when a setting is changed at runtime. To apply
new environment values, start a new process or create a separate `Settings`
instance. Environment variables initialize settings; to read the effective
value in a running process, use `config` or the corresponding `get_*` helper.

## Locale

Pass `locale` to a service function to override the global locale for one
request:

```python
from imdbinfo import get_movie, search_title

movie = get_movie("tt0133093", locale="it")
results = search_title("Money Heist", locale="es")
```

For the process-wide locale, use any of the three configuration methods:

```python
# 1. Environment, set before starting Python:
# IMDBINFO_LOCALE=it

# 2. Direct runtime access:
from imdbinfo import config
config.locale = "it"
print(config.locale)  # "it"

# 3. Named helpers:
from imdbinfo import get_locale, set_locale
set_locale("it")
print(get_locale())  # "it"
```

`get_locale()` returns `""` when the configured locale is English (`"en"`).
Supported values are `en`, `fr-ca`, `fr`, `hi`, `de`, `it`, `es`, `pt`, and
`es-es`. Setting an unsupported global locale raises
`pydantic.ValidationError`. Invalid per-request locale values retain the
existing behavior of logging a warning and falling back to English.

`title` holds the original title, while `title_localized` holds the
locale-specific title when available.

## Proxies

Set and read the process-wide proxy using environment variables, `config`, or
the helpers:

```python
# 1. Environment, set before starting Python:
# IMDBINFO_PROXIES=http://proxy.example:8080

# 2. Direct runtime access (reassign the mapping; don't mutate it in place):
from imdbinfo import config
config.proxies = {
    "http": "http://proxy.example:8080",
    "https": "http://proxy.example:8080",
}
print(config.proxies)

# 3. Named helpers:
from imdbinfo import get_proxy, set_proxy
set_proxy("http://proxy.example:8080")
print(get_proxy())
```

A single proxy URL is expanded to both HTTP and HTTPS. A protocol-to-URL
mapping can instead set them independently. Pass `None` to `config.proxies` or
`set_proxy(None)` to clear the proxy. The settings validator checks proxy URL
scheme, host, and port. `set_proxy()` and `get_proxy()` are also re-exported
from `imdbinfo.proxy` for compatibility.

The configured proxy applies to the library's connections. Proxy settings are
global; the public service APIs do not accept a per-call proxy override.

## Result limits

Each result type has an independent positive-integer limit. Use an
environment variable before startup, assign directly to `config`, or use the
named helpers:

```python
# 1. Environment, set before starting Python:
# IMDBINFO_MAX_ITEMS_AKAS=300

# 2. Direct runtime access:
from imdbinfo import config
config.max_items_akas = 300
print(config.max_items_akas)  # 300

# 3. Named helpers:
from imdbinfo import get_max_items, set_max_items
set_max_items(search=25, akas=300)
print(get_max_items("akas"))  # 300
print(get_max_items())        # mapping of all limits
```

`set_max_items()` accepts any combination of `search`, `images`, `interests`,
`akas`, `trivia`, `reviews`, `guide_items`, `quotes`, and `credits`. It
validates all supplied values before applying any of them. `get_max_items()`
returns all values keyed by type; `get_max_items("akas")` and
`get_max_items("max_items_akas")` return the individual value. `configure()`
also accepts full setting names such as `max_items_akas=300`.

| Setting | Results | Default | Environment variable |
|---|---|---:|---|
| `max_items_search` | `search_title` results | 50 | `IMDBINFO_MAX_ITEMS_SEARCH` |
| `max_items_images` | Gallery images | 50 | `IMDBINFO_MAX_ITEMS_IMAGES` |
| `max_items_interests` | Interests | 20 | `IMDBINFO_MAX_ITEMS_INTERESTS` |
| `max_items_akas` | Alternate titles | 200 | `IMDBINFO_MAX_ITEMS_AKAS` |
| `max_items_trivia` | Trivia | 50 | `IMDBINFO_MAX_ITEMS_TRIVIA` |
| `max_items_reviews` | Reviews | 50 | `IMDBINFO_MAX_ITEMS_REVIEWS` |
| `max_items_guide_items` | Parental-guide entries | 10 | `IMDBINFO_MAX_ITEMS_GUIDE_ITEMS` |
| `max_items_quotes` | Quotes | 100 | `IMDBINFO_MAX_ITEMS_QUOTES` |
| `max_items_credits` | Filmography credits | 250 | `IMDBINFO_MAX_ITEMS_CREDITS` |

The corresponding public API accepts `max_items` to override only that
result type for one call, for example
`get_akas("tt0133093", max_items=500)`. Other result limits remain at their
configured values.

## Clear cached data

Many public title and person services use an LRU cache. Clear an individual
cached function when a long-running process needs fresh data:

```python
from imdbinfo import get_movie

get_movie.cache_clear()
```

Changing a setting on the global `config` object, or using a setter helper,
clears the dependent service caches. Cached results account for the locale and
effective result limits used to produce them.

Use `reset_config()` to restore the values loaded when the package was
initialized. It does not re-read environment variables.


`get_filmography` uses this internal cache rather than exposing a
`cache_clear()` method; its cache key includes the person, locale, and selected
roles. Equivalent role lists containing enum members or their string values
share a cache entry.
