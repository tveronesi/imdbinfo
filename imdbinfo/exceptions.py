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

"""
imdbinfo exception hierarchy
============================

ImdbinfoError
├── HTTPError        — any non-200 HTTP response (status_code, url, response_text)
│   └── WAFError     — HTTP 202 from AWS WAF enforcement
├── GraphQLError     — non-200 or {"errors": …} from the GraphQL endpoint
└── ParseError       — __NEXT_DATA__ script not found in HTML response
"""

from typing import Optional, List, Dict, Any


class ImdbinfoError(Exception):
    """Base class for all imdbinfo exceptions."""


class HTTPError(ImdbinfoError):
    """Raised when the IMDb HTML endpoint returns a non-200 status code.

    Attributes
    ----------
    status_code : int
        The HTTP status code returned by the server.
    url : str
        The full URL that was requested.
    response_text : str
        The first 500 characters of the response body (may be empty).
    """

    def __init__(
        self, message: str, status_code: int, url: str, response_text: str = ""
    ):
        super().__init__(message)
        self.status_code: int = status_code
        self.url: str = url
        self.response_text: str = response_text

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"status_code={self.status_code!r}, "
            f"url={self.url!r}, "
            f"message={str(self)!r})"
        )


class WAFError(HTTPError):
    """Raised when AWS WAF returns HTTP 202, blocking the request.

    This is a subclass of :class:`HTTPError` so callers that catch
    ``HTTPError`` will also catch ``WAFError``.  Callers that want to handle
    WAF enforcement specifically (e.g. to rotate proxies or back off) can
    catch ``WAFError`` directly.

    Attributes
    ----------
    status_code : int
        Always ``202`` for WAF-blocked responses.
    url : str
        The full URL that was blocked.
    response_text : str
        The first 500 characters of the WAF challenge response body.
    """


class GraphQLError(ImdbinfoError):
    """Raised when the IMDb GraphQL API returns a non-200 status or
    an ``{"errors": […]}`` payload.

    Attributes
    ----------
    url : str
        The GraphQL endpoint URL.
    query_term : str
        The search term / entity ID used in the query.
    status_code : Optional[int]
        HTTP status code when the failure is transport-level; ``None`` when
        the response was 200 but contained GraphQL ``errors``.
    errors : List[Dict[str, Any]]
        Parsed GraphQL error objects from the response body (empty list for
        transport-level failures).
    response_text : str
        First 500 characters of the raw response body.
    """

    def __init__(
        self,
        message: str,
        url: str,
        query_term: str,
        status_code: Optional[int] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        response_text: str = "",
    ):
        super().__init__(message)
        self.url: str = url
        self.query_term: str = query_term
        self.status_code: Optional[int] = status_code
        self.errors: List[Dict[str, Any]] = errors or []
        self.response_text: str = response_text

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"status_code={self.status_code!r}, "
            f"url={self.url!r}, "
            f"query_term={self.query_term!r}, "
            f"message={str(self)!r})"
        )


class ParseError(ImdbinfoError):
    """Raised when the expected ``__NEXT_DATA__`` JSON script tag is absent
    from the IMDb HTML response.

    Attributes
    ----------
    url : str
        The URL whose response could not be parsed.
    """

    def __init__(self, message: str, url: str = ""):
        super().__init__(message)
        self.url: str = url

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(url={self.url!r}, message={str(self)!r})"
