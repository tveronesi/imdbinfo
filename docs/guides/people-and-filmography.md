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

By default, the request selects actor, actress, cinematographer, director,
writer, and composer credits. The returned categories are derived from IMDb's
credit data and can vary by person.

## Filter credits by role

Use the `roles` parameter to select one or more categories. `CreditRole` is
available from the top-level package and defines the supported role names:

```python
from imdbinfo import CreditRole, get_filmography

filmography = get_filmography(
    "nm0000206",
    locale="es",
    roles=[CreditRole.ACTOR, CreditRole.DIRECTOR],
)
for title in filmography.get("actor", []):
    print(title.title, title.year)
```

Only `CreditRole` members are accepted; see the
[`CreditRole` API reference](../api/models.md#imdbinfo.models.CreditRole) for
the available categories. Passing `None` or an empty list uses the default
roles. Invalid entries, including strings, are ignored with a warning. If no
valid entries remain, the function returns an empty dictionary without making
a request.
