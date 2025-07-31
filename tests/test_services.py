import os
from types import SimpleNamespace

from imdbinfo import services

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_json_source")


def load_sample_text(filename: str) -> str:
    with open(os.path.join(SAMPLE_DIR, filename), encoding="utf-8") as f:
        return f.read()


def mock_get_factory(filename: str):
    json_text = load_sample_text(filename)
    html = f'<html><script id="__NEXT_DATA__">{json_text}</script></html>'.encode("utf-8")

    def mock_get(*args, **kwargs):
        return SimpleNamespace(status_code=200, content=html)

    return mock_get


def test_get_movie(monkeypatch):
    monkeypatch.setattr(services.requests, "get", mock_get_factory("sample_resource.json"))
    movie = services.get_movie("tt0133093")
    assert movie.title == "The Matrix"
    assert movie.duration == 136


def test_search_title(monkeypatch):
    monkeypatch.setattr(services.requests, "get", mock_get_factory("sample_search.json"))
    result = services.search_title("matrix")
    assert result.titles[0].title == "The Matrix"
    assert result.names


def test_get_name(monkeypatch):
    monkeypatch.setattr(services.requests, "get", mock_get_factory("sample_person.json"))
    person = services.get_name("nm0000126")
    assert person.name == "Kevin Costner"
    assert "The Postman" in person.knownfor
