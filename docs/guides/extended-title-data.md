# Extended title data

Several title services retrieve additional IMDb data through the GraphQL
transport. Results for a title share an internal cache during the process.

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

Reviews and trivia are returned as dictionaries because their shape reflects
the corresponding IMDb GraphQL response.

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
