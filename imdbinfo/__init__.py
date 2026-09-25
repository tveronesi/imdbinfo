# MIT License
# Copyright (c) 2025 tveronesi+imdbinfo@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""imdbinfo — A Python library for retrieving structured IMDb data without API keys.

This library provides functions to search for and fetch comprehensive information
about movies, TV series, episodes, and people from IMDb. No API keys or credentials
are required.

Quick Start
-----------

```python
>>> from imdbinfo import search_title, get_movie, get_name
>>> results = search_title("The Matrix", year=1999)
>>> movie = get_movie("tt0133093")
>>> person = get_name("nm0000206")
```

Main Functions
--------------
- :func:`.search_title` — Search for titles and people
- :func:`.get_movie` — Fetch title details (movie, TV series, episode)
- :func:`.get_name` — Fetch person biography and filmography
- :func:`.get_awards` — Fetch awards and nominations
- :func:`.get_season_episodes` — Fetch episodes for a specific season
- :func:`.get_all_episodes` — Fetch all episodes in a series

Configuration
--------------
- :func:`.set_locale` — Set global language locale for requests
- :class:`.TitleType` — Enum for filtering titles by type

Data Models
-----------
- :class:`.MovieDetail` — Comprehensive title information
- :class:`.PersonDetail` — Person biography and filmography
- :class:`.SearchResult` — Search result (titles + people)

Exceptions
----------
- :class:`.ImdbinfoError` — Base exception
- :class:`.HTTPError` — HTTP transport errors
- :class:`.WAFError` — AWS WAF blocking (HTTP 202)
- :class:`.GraphQLError` — GraphQL API errors
- :class:`.ParseError` — JSON parsing errors

See Also
--------
- Documentation: https://tveronesi.github.io/imdbinfo/
- GitHub: https://github.com/tveronesi/imdbinfo
"""

import logging

from .services import (
    get_movie,
    get_awards,
    search_title,
    get_name,
    get_episodes,
    get_all_episodes,
    get_season_episodes,
    get_akas,
    get_reviews,
    get_trivia,
    get_parental_guide,
    get_filmography,
    get_all_interests,
    get_media_gallery,
    get_quotes,
    TitleType,
)
from .models import (
    Award,
    AwardInfo,
    Quote,
    QuoteLine,
    QuoteCharacter,
    InterestScore,
)
from .exceptions import (
    ImdbinfoError,
    HTTPError,
    WAFError,
    GraphQLError,
    ParseError,
)

__all__ = [
    "get_movie",
    "get_awards",
    "search_title",
    "get_name",
    "get_episodes",
    "get_all_episodes",
    "get_season_episodes",
    "get_akas",
    "get_reviews",
    "get_trivia",
    "get_parental_guide",
    "get_filmography",
    "get_all_interests",
    "get_media_gallery",
    "get_quotes",
    "TitleType",
    # award models
    "Award",
    "AwardInfo",
    # quote models
    "Quote",
    "QuoteLine",
    "QuoteCharacter",
    "InterestScore",
    # exceptions
    "ImdbinfoError",
    "HTTPError",
    "WAFError",
    "GraphQLError",
    "ParseError",
]

# setup library logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
