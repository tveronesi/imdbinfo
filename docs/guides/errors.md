# Errors and reliability

`imdbinfo` exposes a dedicated exception hierarchy. Catch the base
`ImdbinfoError` to handle errors raised by the library:

```python
from imdbinfo import ImdbinfoError, get_movie

try:
    movie = get_movie("tt0133093")
except ImdbinfoError as error:
    print("imdbinfo failed:", error)
```

!!! tip
    Handle errors at the appropriate level in your application, and account
    for optional fields in returned models.
