from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from imdbinfo import services
from imdbinfo.config import MAX_ITEMS_DEFAULTS, Settings, config, configure, reset_config
from imdbinfo.helpers import (
    get_locale,
    get_max_items,
    get_proxy,
    set_locale,
    set_max_items,
    set_proxy,
)
from imdbinfo.locale import _get_country_code_from_lang_locale


def test_settings_defaults_match_existing_graphql_limits():
    settings = Settings(_env_file=None)
    assert settings.locale == "en"
    assert {name: getattr(settings, name) for name in MAX_ITEMS_DEFAULTS} == (
        MAX_ITEMS_DEFAULTS
    )
    assert settings.proxies is None


def test_configure_and_assignment_update_runtime_values():
    configure(
        locale="fr",
        max_items_search=12,
        max_items_akas=300,
        proxies="http://proxy.example:8080",
    )
    assert config.locale == "fr"
    assert config.max_items_search == 12
    assert config.max_items_akas == 300
    assert config.proxies == {
        "http": "http://proxy.example:8080",
        "https": "http://proxy.example:8080",
    }

    config.proxies = {"https": "https://proxy.example:8443"}
    assert config.proxies == {"https": "https://proxy.example:8443"}


def test_set_and_get_max_items_helpers():
    set_max_items(search=24, akas=321)

    assert get_max_items("search") == 24
    assert get_max_items("max_items_akas") == 321
    assert get_max_items() == {
        "search": 24,
        "images": 50,
        "interests": 20,
        "akas": 321,
        "trivia": 50,
        "reviews": 50,
        "guide_items": 10,
        "quotes": 100,
        "credits": 250,
    }


def test_helpers_module_owns_public_locale_accessors():
    set_locale(" IT ")

    assert get_locale() == "it"
    assert _get_country_code_from_lang_locale() == "IT"


def test_set_max_items_is_atomic_on_validation_error():
    with pytest.raises(ValidationError):
        set_max_items(search=24, akas=0)

    assert get_max_items("search") == 50
    assert get_max_items("akas") == 200


def test_get_max_items_rejects_unknown_kind():
    with pytest.raises(ValueError, match="unknown max_items kind"):
        get_max_items("unknown")


def test_proxy_helpers_share_the_central_configuration():
    set_proxy("http://proxy.example:8080")

    assert get_proxy() == config.proxies
    assert get_proxy()["https"] == "http://proxy.example:8080"

    set_proxy(None)
    assert config.proxies is None


def test_http_transports_receive_configured_proxy(monkeypatch):
    proxies = {"https": "http://proxy.example:8080"}
    config.proxies = proxies
    received = {}

    def fake_post(url, headers, json, proxies=None):
        received.update(proxies=proxies)
        return SimpleNamespace(status_code=200, json=dict)

    monkeypatch.setattr(services.niquests, "post", fake_post, raising=False)

    services.request_graphql_url({}, "term", {"query": "{}"}, "https://example.test")

    assert received["proxies"] == proxies


@pytest.mark.parametrize(
    "field,value",
    [
        ("locale", "unsupported"),
        ("max_items_search", 0),
        ("max_items_akas", -1),
        ("proxies", 123),
        ("proxies", "not-a-url"),
    ],
)
def test_settings_assignment_rejects_invalid_values(field, value):
    with pytest.raises(ValidationError):
        setattr(config, field, value)


def test_environment_variables_are_loaded_and_proxy_url_is_normalized(monkeypatch):
    monkeypatch.setenv("IMDBINFO_LOCALE", " IT ")
    monkeypatch.setenv("IMDBINFO_MAX_ITEMS_AKAS", "321")
    monkeypatch.setenv("IMDBINFO_PROXIES", "http://proxy.example:8080")

    settings = Settings(_env_file=None)

    assert settings.locale == "it"
    assert settings.max_items_akas == 321
    assert settings.proxies == {
        "http": "http://proxy.example:8080",
        "https": "http://proxy.example:8080",
    }


def test_reset_config_restores_import_time_values():
    initial_locale = config.locale
    initial_limit = config.max_items_akas
    configure(locale="it", max_items_akas=999)

    reset_config()

    assert config.locale == initial_locale
    assert config.max_items_akas == initial_limit


def test_graphql_query_limits_are_independent_and_call_override_wins(monkeypatch):
    queries = []

    def fake_request(headers, search_term, payload, url):
        queries.append(payload["query"])
        return {"data": {"title": {}}}

    monkeypatch.setattr(services, "request_graphql_url", fake_request)
    configure(max_items_images=61, max_items_interests=17, max_items_akas=201)

    services.get_akas("tt1234567", max_items=333)

    query = queries[0]
    assert "images(first: 61)" in query
    assert "interests(first: 17)" in query
    assert "akas(first: 333)" in query
    assert "trivia(first: 50)" in query
    assert "reviews(first: 50)" in query
    assert "guideItems(first: 10)" in query
    assert "quotes(first: 100)" in query


def test_search_title_uses_configured_limit_and_override(monkeypatch):
    queries = []

    def fake_request(**kwargs):
        queries.append(kwargs["payload"]["query"])
        return {"data": {"mainSearch": {"edges": []}}}

    monkeypatch.setattr(services, "request_graphql_url", fake_request)

    configure(max_items_search=23)
    services.search_title("configured-limit")
    services.search_title("call-override", max_items=7)

    assert "first: 23" in queries[0]
    assert "first: 7" in queries[1]
