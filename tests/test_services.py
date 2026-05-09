import os
import json
from types import SimpleNamespace

from imdbinfo import services

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_json_source")


def load_sample_text(filename: str) -> str:
    with open(os.path.join(SAMPLE_DIR, filename), encoding="utf-8") as f:
        return f.read()


def mock_get_factory(filename: str):
    json_text = load_sample_text(filename)
    html = f'<html><script id="__NEXT_DATA__">{json_text}</script></html>'.encode(
        "utf-8"
    )

    def mock_get(*args, **kwargs):
        return SimpleNamespace(status_code=200, content=html)

    return mock_get


def mock_post_factory(filename: str):
    json_text = load_sample_text(filename)

    def mock_post(*args, **kwargs):
        # Provide a .json() method so callers can get parsed JSON (as real requests.Response.json would)
        return SimpleNamespace(
            status_code=200, content=json_text, json=lambda: json.loads(json_text)
        )

    return mock_post


def test_get_movie(monkeypatch):
    monkeypatch.setattr(
        services.niquests, "get", mock_get_factory("sample_resource.json")
    )
    movie = services.get_movie("tt0133093")
    assert movie.title == "The Matrix"
    assert movie.duration == 136


def test_search_title(monkeypatch):
    # Use POST mock for GraphQL-style search responses
    # allow setting 'post' even if the niquests stub doesn't define it by default
    monkeypatch.setattr(
        services.niquests,
        "post",
        mock_post_factory("sample_search.json"),
        raising=False,
    )
    result = services.search_title("matrix")
    assert result.titles[0].title == "The Matrix"
    assert result.names


def test_search_title_includes_rating(monkeypatch):
    monkeypatch.setattr(
        services.niquests,
        "post",
        mock_post_factory("sample_search.json"),
        raising=False,
    )
    result = services.search_title("matrix")
    assert result.titles[0].rating == 8.7
    assert result.titles[1].rating == 7.2
    assert result.titles[2].rating == 5.6


def test_get_name(monkeypatch):
    monkeypatch.setattr(
        services.niquests, "get", mock_get_factory("sample_person.json")
    )
    person = services.get_name("nm0000126")
    assert person.name == "Kevin Costner"
    assert "Balla coi lupi" in person.knownfor


# ── Exception hierarchy tests ────────────────────────────────────────────────

import pytest
from imdbinfo.exceptions import (
    ImdbinfoError,
    HTTPError,
    WAFError,
    GraphQLError,
    ParseError,
)


def _make_get_stub(status_code: int, text: str = "", content: bytes = b""):
    def stub(*args, **kwargs):
        return SimpleNamespace(
            status_code=status_code,
            text=text,
            content=content,
        )

    return stub


def test_http_error_raised_on_non_200(monkeypatch):
    monkeypatch.setattr(services.niquests, "get", _make_get_stub(404, text="not found"))
    with pytest.raises(HTTPError) as exc_info:
        services.get_movie.cache_clear()
        services.get_movie("tt9999999")
    err = exc_info.value
    assert err.status_code == 404
    assert "tt9999999" in err.url
    assert isinstance(err, ImdbinfoError)


def test_waf_error_raised_on_202(monkeypatch):
    monkeypatch.setattr(
        services.niquests, "get", _make_get_stub(202, text="waf challenge")
    )
    with pytest.raises(WAFError) as exc_info:
        services.get_movie.cache_clear()
        services.get_movie("tt9999998")
    err = exc_info.value
    assert err.status_code == 202
    assert "tt9999998" in err.url
    assert "waf challenge" in err.response_text
    assert isinstance(err, HTTPError)
    assert isinstance(err, ImdbinfoError)


def test_waf_error_is_subclass_of_http_error():
    assert issubclass(WAFError, HTTPError)
    assert issubclass(HTTPError, ImdbinfoError)
    assert issubclass(GraphQLError, ImdbinfoError)
    assert issubclass(ParseError, ImdbinfoError)


def test_parse_error_raised_when_no_next_data(monkeypatch):
    # Return a 200 response whose HTML has no __NEXT_DATA__ script tag
    monkeypatch.setattr(
        services.niquests,
        "get",
        _make_get_stub(200, content=b"<html><body>nothing here</body></html>"),
    )
    with pytest.raises(ParseError) as exc_info:
        services.get_movie.cache_clear()
        services.get_movie("tt9999997")
    err = exc_info.value
    assert "tt9999997" in err.url
    assert isinstance(err, ImdbinfoError)


def test_graphql_error_raised_on_non_200_post(monkeypatch):
    def stub_post(*args, **kwargs):
        return SimpleNamespace(
            status_code=503, text="service unavailable", json=lambda: {}
        )

    monkeypatch.setattr(services.niquests, "post", stub_post, raising=False)
    with pytest.raises(GraphQLError) as exc_info:
        services.search_title.cache_clear()
        services.search_title("matrix_test_error")
    err = exc_info.value
    assert err.status_code == 503
    assert err.query_term == "matrix_test_error"
    assert isinstance(err, ImdbinfoError)


def test_graphql_error_raised_on_errors_payload(monkeypatch):
    import json as _json

    payload = {"errors": [{"message": "some graphql error"}]}

    def stub_post(*args, **kwargs):
        return SimpleNamespace(
            status_code=200,
            text=_json.dumps(payload),
            json=lambda: payload,
        )

    monkeypatch.setattr(services.niquests, "post", stub_post, raising=False)
    with pytest.raises(GraphQLError) as exc_info:
        services.search_title.cache_clear()
        services.search_title("matrix_test_gql_err")
    err = exc_info.value
    assert err.status_code is None
    assert err.errors == [{"message": "some graphql error"}]
    assert err.query_term == "matrix_test_gql_err"


def test_http_error_metadata():
    err = HTTPError(
        "bad gateway", status_code=502, url="https://example.com", response_text="oops"
    )
    assert err.status_code == 502
    assert err.url == "https://example.com"
    assert err.response_text == "oops"
    assert "502" in repr(err)
    assert "example.com" in repr(err)


def test_waf_error_metadata():
    err = WAFError(
        "waf blocked", status_code=202, url="https://imdb.com/title/tt1/reference"
    )
    assert err.status_code == 202
    assert "tt1" in err.url


def test_graphql_error_metadata():
    err = GraphQLError(
        "gql fail",
        url="https://api.graphql.imdb.com/",
        query_term="tt0133093",
        status_code=500,
        errors=[{"message": "internal"}],
        response_text="err body",
    )
    assert err.status_code == 500
    assert err.errors == [{"message": "internal"}]
    assert err.response_text == "err body"
    assert "tt0133093" in repr(err)


def test_parse_error_metadata():
    err = ParseError("no script", url="https://www.imdb.com/title/tt1/reference")
    assert "tt1" in err.url
    assert "tt1" in repr(err)
