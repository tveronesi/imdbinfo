import json
import os
import pytest
from imdbinfo import parsers

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_json_source")

def load_sample(filename):
    with open(os.path.join(SAMPLE_DIR, filename), encoding="utf-8") as f:
        return json.load(f)

def test_parse_json_movie():
    raw_json = load_sample("sample_resource.json")
    movie = parsers.parse_json_movie(raw_json)
    assert movie is not None
    assert hasattr(movie, "imdbId")
    assert hasattr(movie, "title")
    assert hasattr(movie, "duration")

def test_parse_json_search():
    raw_json = load_sample("sample_search.json")
    result = parsers.parse_json_search(raw_json)
    assert result is not None
    assert hasattr(result, "titles")
    assert hasattr(result, "names")


