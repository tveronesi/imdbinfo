# People and filmography

## Retrieve a person

Use `get_name` with an IMDb name ID:

```python
from imdbinfo import get_name

person = get_name("nm0000206")
print(person.name)
print(person.birth_date)
print(person.primary_profession)
```

As with titles, both `"nm0000206"` and `"0000206"` are accepted.

## Retrieve a filmography

`get_filmography` groups a person's credits by category:

```python
from imdbinfo import get_filmography

filmography = get_filmography("nm0000206")
for category, titles in filmography.items():
    print(category)
    for title in titles[:3]:
        print("  ", title.title, title.year, title.imdbId)
```

The categories are derived from IMDb's credit data and can vary by person.
