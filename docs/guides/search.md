# Search

## Search titles and people

`search_title` searches IMDb titles and names in one request. Results expose
separate `titles` and `names` collections.

```python
from imdbinfo import search_title

results = search_title("Keanu Reeves")

for person in results.names:
    print(person.name, person.imdbId)

for title in results.titles:
    print(title.title, title.year, title.imdbId)
```

## Narrow a title search

Use `exact_match`, `year`, and `title_type` to reduce ambiguous results:

```python
from imdbinfo import TitleType, search_title

movies = search_title(
    "Dune",
    year=2021,
    exact_match=True,
    title_type=TitleType.Movies,
)
```

`title_type` accepts one `TitleType` member or a tuple of members:

```python
results = search_title(
    "The Office",
    title_type=(TitleType.Series, TitleType.Episodes),
)
```

Available filters are `Movies`, `Series`, `Episodes`, `Shorts`, `TvMovie`,
and `Video`. See [`TitleType`](../api/services.md) for their exact mapping.
