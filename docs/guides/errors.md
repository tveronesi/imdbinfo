# Errors and reliability

`imdbinfo` exposes a dedicated exception hierarchy. Catch the base
`ImdbinfoError` when one handling path is sufficient, or catch a more specific
type to distinguish network, WAF, GraphQL, and parsing failures.

```python
from imdbinfo import GraphQLError, HTTPError, ImdbinfoError, WAFError, get_movie

try:
    movie = get_movie("tt0133093")
except WAFError as error:
    print("IMDb WAF blocked the request:", error.status_code, error.url)
except HTTPError as error:
    print("IMDb HTML request failed:", error.status_code, error.url)
except GraphQLError as error:
    print("IMDb GraphQL request failed:", error.errors)
except ImdbinfoError as error:
    print("imdbinfo failed:", error)
```

`HTTPError` and `WAFError` include the HTTP status, requested URL, and a
truncated response body. `GraphQLError` also exposes the GraphQL error list
when IMDb returns one.

!!! tip
    Treat IMDb data as a remote dependency: set application-level timeouts
    where appropriate, retry conservatively, and handle absent optional
    fields in returned models.
