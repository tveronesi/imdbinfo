# Extended title data

These functions provide additional title information. Results are cached
during the process and refreshed when the relevant settings change.

## Awards and alternate titles

```python
from imdbinfo import get_akas, get_awards

for award in get_awards("tt0034583"):
    print(award.event, award.status, award.category)

akas = get_akas("tt0133093")
for aka in akas.akas:
    print(aka.country_name, aka.title)
```

## Quotes, reviews, and trivia

```python
from imdbinfo import get_quotes, get_reviews, get_trivia

for quote in get_quotes("tt0133093"):
    print(quote.speakers)
    for line in quote.lines:
        print(line)

reviews = get_reviews("tt0133093")
trivia = get_trivia("tt0133093")
```

Reviews and trivia are returned as dictionaries.

## Media, interests, and parental guidance

```python
from imdbinfo import (
    get_all_interests,
    get_media_gallery,
    get_parental_guide,
)

gallery = get_media_gallery("tt0133093")
if gallery:
    for image in gallery.items[:3]:
        print(image.type, image.url)

print(get_all_interests("tt0133093"))

guide = get_parental_guide("tt0133093")
if guide:
    print(guide.summary)
```

Use the [models reference](../api/models.md) to inspect the structured return
types for awards, quotes, gallery items, and parental-guide entries.

## Result limits

Each result type has its own setting and retains its current default:

| Setting | Results | Default |
|---|---|---:|
| `max_items_search` | Search results | 50 |
| `max_items_images` | Gallery images | 50 |
| `max_items_interests` | Interests | 20 |
| `max_items_akas` | Alternate titles | 200 |
| `max_items_trivia` | Trivia | 50 |
| `max_items_reviews` | Reviews | 50 |
| `max_items_guide_items` | Parental-guide entries | 10 |
| `max_items_quotes` | Quotes | 100 |
| `max_items_credits` | Filmography credits | 250 |

Set limits using one of these three methods:

```python
# 1. Environment before starting Python:
# IMDBINFO_MAX_ITEMS_AKAS=300

# 2. Shared configuration:
from imdbinfo import config
config.max_items_akas = 300

# 3. Named setters and getters:
from imdbinfo import get_max_items, set_max_items
set_max_items(akas=300, quotes=40)
aka_limit = get_max_items("akas")  # 300
all_limits = get_max_items()
```

The same three methods apply to locale and proxies: use `IMDBINFO_LOCALE` /
`IMDBINFO_PROXIES`, assign `config.locale` / `config.proxies`, or use
`set_locale()` / `get_locale()` and `set_proxy()` / `get_proxy()`. The
environment and optional `.env` file are read when the shared configuration is
created; changing them later does not update the running process.

Each relevant public function accepts `max_items` to override only its own
result limit for that call, for example `get_akas("tt0133093", max_items=500)`.
Other result types continue to use their configured limits.
All configured and per-call limits must be positive integers.

See the [locales and caching guide](locales-and-caching.md) for all setting
names, environment variables, proxy formats, and cache behavior.
