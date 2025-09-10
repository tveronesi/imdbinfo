import os
from types import SimpleNamespace

from imdbinfo import ImdbInfoService

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


def test_imdb_info_service_get_movie(monkeypatch):
    """Test the new ImdbInfoService class get_movie method"""
    from imdbinfo import services
    monkeypatch.setattr(services.niquests, "get", mock_get_factory("sample_resource.json"))
    movie = ImdbInfoService.get_movie("tt0133093")
    assert movie.title == "The Matrix"
    assert movie.duration == 136


def test_imdb_info_service_search_title(monkeypatch):
    """Test the new ImdbInfoService class search_title method"""
    from imdbinfo import services
    monkeypatch.setattr(services.niquests, "get", mock_get_factory("sample_search.json"))
    result = ImdbInfoService.search_title("matrix")
    assert result.titles[0].title == "The Matrix"
    assert result.names


def test_imdb_info_service_get_name(monkeypatch):
    """Test the new ImdbInfoService class get_name method"""
    from imdbinfo import services
    monkeypatch.setattr(services.niquests, "get", mock_get_factory("sample_person.json"))
    person = ImdbInfoService.get_name("nm0000126")
    assert person.name == "Kevin Costner"
    assert "The Postman" in person.knownfor


def test_imdb_info_service_normalize_imdb_id():
    """Test the normalize_imdb_id static method"""
    imdb_id, lang = ImdbInfoService.normalize_imdb_id("tt0133093")
    assert imdb_id == "0133093"
    assert lang == ""
    
    imdb_id, lang = ImdbInfoService.normalize_imdb_id("133093")
    assert imdb_id == "0133093"
    assert lang == ""


def test_class_and_functions_produce_same_results(monkeypatch):
    """Test that the new class methods and old functions produce the same results"""
    from imdbinfo import services
    monkeypatch.setattr(services.niquests, "get", mock_get_factory("sample_resource.json"))
    
    # Compare class method vs function
    class_result = ImdbInfoService.get_movie("tt0133093")
    function_result = services.get_movie("tt0133093") 
    
    assert class_result.title == function_result.title
    assert class_result.duration == function_result.duration
    assert class_result.imdb_id == function_result.imdb_id


def test_imdb_info_service_available_in_main_module():
    """Test that ImdbInfoService is available when importing from main module"""
    from imdbinfo import ImdbInfoService as ImportedService
    assert ImportedService is not None
    assert hasattr(ImportedService, 'get_movie')
    assert hasattr(ImportedService, 'search_title')
    assert hasattr(ImportedService, 'get_name')