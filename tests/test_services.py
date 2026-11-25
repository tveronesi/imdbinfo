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


def test_get_all_episodes_with_missing_numbers(monkeypatch):
    items = [
        {
            "titleId": "tt14136640",
            "titleText": "Joseph Losey",
            "series": {"seasonNumber": "", "episodeNumber": ""},
            "releaseDate": None,
        },
        {
            "titleId": "tt1234567",
            "titleText": "Numbered episode",
            "series": {"seasonNumber": "1", "episodeNumber": "2"},
            "releaseDate": None,
        },
    ]
    payload = {
        "props": {"pageProps": {"searchResults": {"titleResults": {"titleListItems": items}}}}
    }
    services.clear_all_caches()
    monkeypatch.setattr(services, "request_json_url", lambda url: payload)
    episodes = services.get_all_episodes("tt0815353")
    assert len(episodes) == 2
    assert (episodes[0].season_number, episodes[0].episode_number) == (None, None)
    assert (episodes[1].season_number, episodes[1].episode_number) == (1, 2)


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
        services.clear_all_caches()
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
        services.clear_all_caches()
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
        services.clear_all_caches()
        services.get_movie("tt9999997")
    err = exc_info.value
    assert "tt9999997" in err.url
    assert isinstance(err, ImdbinfoError)


def test_graphql_request_includes_client_headers(monkeypatch):
    payload = {"query": "{ __typename }"}
    response_data = {"data": {"__typename": "Query"}}
    caller_headers = {"Content-Type": "application/json", "x-imdb-user-country": "US"}

    def stub_post(url, *, headers, json):
        assert url == services.GRAPHQL_URL
        assert json == payload
        assert headers == {
            "Referer": "https://www.imdb.com/",
            "x-imdb-client-name": "imdb-web-next",
            **caller_headers,
        }
        return SimpleNamespace(status_code=200, json=lambda: response_data)

    monkeypatch.setattr(services.niquests, "post", stub_post, raising=False)
    assert services.request_graphql_url(
        caller_headers, "test", payload, services.GRAPHQL_URL
    ) == response_data
    assert caller_headers == {
        "Content-Type": "application/json",
        "x-imdb-user-country": "US",
    }


def test_graphql_error_raised_on_non_200_post(monkeypatch):
    def stub_post(*args, **kwargs):
        return SimpleNamespace(
            status_code=503, text="service unavailable", json=lambda: {}
        )

    monkeypatch.setattr(services.niquests, "post", stub_post, raising=False)
    with pytest.raises(GraphQLError) as exc_info:
        services.clear_all_caches()
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
        services.clear_all_caches()
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


def test_get_media_gallery(monkeypatch):
    monkeypatch.setattr(
        services.niquests,
        "post",
        mock_post_factory("sample_media_gallery.json"),
        raising=False,
    )
    services.clear_all_caches()
    gallery = services.get_media_gallery("tt0133093")
    assert gallery is not None
    assert gallery.total == 557
    assert len(gallery.items) == 50
    assert gallery.imdb_id == "0910970"

    first = gallery[0]
    assert first.id == "rm401243905"
    assert first.url.startswith("https://m.media-amazon.com/images/")
    assert first.type == "still_frame"
    assert "Ben Burtt" in first.caption


def test_get_media_gallery_caches(monkeypatch):
    call_count = 0

    def counting_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        json_text = load_sample_text("sample_media_gallery.json")
        return SimpleNamespace(
            status_code=200,
            content=json_text,
            json=lambda: json.loads(json_text),
        )

    monkeypatch.setattr(services.niquests, "post", counting_post, raising=False)
    services.clear_all_caches()

    g1 = services.get_media_gallery("tt0133093")
    g2 = services.get_media_gallery("tt0133093")
    assert g1.total == g2.total
    assert call_count == 1


def test_request_json_url_caches(monkeypatch):
    calls = []
    def fake_handler(url):
        calls.append(url)
        class FakeResp:
            status_code = 200
            content = b'<html><script id="__NEXT_DATA__">{"title": "Matrix"}</script></html>'
        return FakeResp()

    monkeypatch.setattr(services, "request_handler", fake_handler)
    services.clear_all_caches()
    url = "https://www.imdb.com/title/tt0133093/reference"

    data1 = services.request_json_url(url)
    assert len(calls) == 1
    assert data1 == {"title": "Matrix"}

    # Second call should hit LRU cache without calling request_handler
    data2 = services.request_json_url(url)
    assert len(calls) == 1
    assert data2 == data1

    # clear_all_caches should invalidate request_json_url cache
    services.clear_all_caches()
    data3 = services.request_json_url(url)
    assert len(calls) == 2



def test_request_graphql_url_caches(monkeypatch):
    calls = []

    def stub_http(headers, search_term, payload, url):
        calls.append((headers, search_term, payload, url))
        return {"data": {"result": "ok", "country": headers.get("x-imdb-user-country", "")}}

    monkeypatch.setattr(services, "_request_graphql_http", stub_http)
    services.clear_all_caches()

    headers_en = {"Content-Type": "application/json", "x-imdb-user-country": "EN"}
    payload = {"query": '{ title(id: "tt0133093") { id } }'}

    # 1. First call -> executes HTTP call
    data1 = services.request_graphql_url(headers_en, "tt0133093", payload, services.GRAPHQL_URL)
    assert len(calls) == 1
    assert data1["data"]["country"] == "EN"

    # 2. Second call with same payload and country -> cache hit
    data2 = services.request_graphql_url(headers_en, "tt0133093", payload, services.GRAPHQL_URL)
    assert len(calls) == 1
    assert data2 == data1

    # 3. Call with different country -> cache miss (locale-aware)
    headers_it = {"Content-Type": "application/json", "x-imdb-user-country": "IT"}
    data3 = services.request_graphql_url(headers_it, "tt0133093", payload, services.GRAPHQL_URL)
    assert len(calls) == 2
    assert data3["data"]["country"] == "IT"

    # 4. Call back with English -> cache hit (multi-locale retention)
    data4 = services.request_graphql_url(headers_en, "tt0133093", payload, services.GRAPHQL_URL)
    assert len(calls) == 2
    assert data4 == data1

    # 5. cache_clear clears the GraphQL cache
    services.request_graphql_url.cache_clear()
    data5 = services.request_graphql_url(headers_en, "tt0133093", payload, services.GRAPHQL_URL)
    assert len(calls) == 3


def test_set_locale_does_not_clear_cache_by_default(monkeypatch):
    from imdbinfo.locale import set_locale

    calls_html = []
    calls_gql = []

    def fake_handler(url):
        calls_html.append(url)
        class FakeResp:
            status_code = 200
            content = b'<html><script id="__NEXT_DATA__">{"title": "Matrix"}</script></html>'
        return FakeResp()

    def fake_gql(headers, search_term, payload, url):
        calls_gql.append((headers, payload))
        return {"data": {"search": "matrix"}}

    monkeypatch.setattr(services, "request_handler", fake_handler)
    monkeypatch.setattr(services, "_request_graphql_http", fake_gql)
    services.clear_all_caches()

    url = "https://www.imdb.com/title/tt0133093/reference"
    services.request_json_url(url)
    assert len(calls_html) == 1

    headers = {"Content-Type": "application/json", "x-imdb-user-country": "EN"}
    services.request_graphql_url(headers, "test", {"query": "{ id }"}, services.GRAPHQL_URL)
    assert len(calls_gql) == 1

    # Changing locale without clear_cache=True should NOT invalidate existing caches
    set_locale("it")
    services.request_json_url(url)
    assert len(calls_html) == 1  # Still 1, cache was preserved!

    services.request_graphql_url(headers, "test", {"query": "{ id }"}, services.GRAPHQL_URL)
    assert len(calls_gql) == 1  # Still 1, cache was preserved!

    # Calling with clear_cache=True should invalidate caches
    set_locale("en", clear_cache=True)
    services.request_json_url(url)
    assert len(calls_html) == 2

    services.request_graphql_url(headers, "test", {"query": "{ id }"}, services.GRAPHQL_URL)
    assert len(calls_gql) == 2
