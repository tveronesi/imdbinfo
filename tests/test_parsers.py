import json
import os
import pytest
from imdbinfo import parsers

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_json_source")

def load_sample(filename):
    with open(os.path.join(SAMPLE_DIR, filename), encoding="utf-8") as f:
        return json.load(f)

def test_parse_json_movie():
    raw_json = load_sample("sample_resource.json")
    movie = parsers.parse_json_movie(raw_json)
    assert movie is not None

    # Basic fields
    assert movie.imdbId == "tt0133093"
    assert movie.title == "The Matrix"
    assert movie.year == 1999
    assert movie.duration == 136
    assert movie.rating == 8.7
    assert movie.plot.startswith("When a beautiful stranger leads computer hacker Neo")
    assert "Action" in movie.genres
    assert "Sci-Fi" in movie.genres
    assert "US" in movie.country_codes
    assert "AU" in movie.country_codes
    assert movie.cover_url.startswith("https://m.media-amazon.com/images/")
    assert movie.url == "https://www.imdb.com/title/tt0133093/"
    assert movie.release_date == "1999-05-07"

    # Directors
    assert len(movie.directors) == 2
    assert movie.directors[0].name == "Lana Wachowski"
    assert movie.directors[1].name == "Lilly Wachowski"

    # Stars
    assert len(movie.stars) >= 4
    star_names = [star.name for star in movie.stars]
    assert "Keanu Reeves" in star_names
    assert "Laurence Fishburne" in star_names
    assert "Carrie-Anne Moss" in star_names
    assert "Hugo Weaving" in star_names

    # Certificates
    assert "US" in movie.certificates
    assert movie.certificates["US"][1] == "TV-14  :: R certificate #36569"

    # Trailers
    assert len(movie.trailers) >= 2
    assert movie.trailers[0].startswith("https://www.imdb.com/video/")

    # Interests
    assert "Cyberpunk" in movie.interests

    # Categories
    assert "director" in movie.categories
    assert "writer" in movie.categories
    assert "cast" in movie.categories
    assert "producer" in movie.categories

    #cast
    assert "cast" in movie.categories
    assert isinstance(movie.categories["cast"], list)
    assert len(movie.categories["cast"]) >= 4
    cast = movie.categories["cast"]
    assert len(cast) >= 3

    # First cast member
    assert cast[0].name == "Keanu Reeves"
    assert "Neo" in cast[0].characters
    assert cast[0].picture_url.startswith("https://m.media-amazon.com/images/")

    # Second cast member
    assert cast[1].name == "Laurence Fishburne"
    assert "Morpheus" in cast[1].characters
    assert cast[1].picture_url.startswith("https://m.media-amazon.com/images/")

    # Third cast member
    assert cast[2].name == "Carrie-Anne Moss"
    assert "Trinity" in cast[2].characters
    assert cast[2].picture_url.startswith("https://m.media-amazon.com/images/")



    # Production
    assert "Warner Bros." in movie.production

    # Summaries and synopses
    assert any("Thomas A. Anderson" in s for s in movie.summaries)
    assert any("Neo" in s for s in movie.synopses)

def test_parse_json_search():
    raw_json = load_sample("sample_search.json")
    result = parsers.parse_json_search(raw_json)
    assert result is not None
    assert hasattr(result, "titles")
    assert hasattr(result, "names")

    # test title  0
    assert len(result.titles) > 0
    first_title = result.titles[0]
    assert first_title.cover_url.startswith("https://m.media-amazon.com/images/")
    assert first_title.id == "0133093"
    assert first_title.imdbId == "tt0133093"
    assert first_title.imdb_id == "0133093"
    assert first_title.kind == "movie"
    assert first_title.title == "The Matrix"
    assert first_title.url == "https://www.imdb.com/title/tt0133093/"
    assert first_title.year == 1999

    # test name 0
    assert len(result.names) > 0
    first_name = result.names[0]
    assert first_name.id == "4210667"
    assert first_name.imdbId == "nm4210667"
    assert first_name.imdb_id == "4210667"
    assert first_name.job == "Soundtrack"
    assert first_name.name == "The Matrix"
    assert first_name.url == "https://www.imdb.com/name/nm4210667"

def test_parse_json_person_detail():
    raw_json = load_sample("sample_person.json")
    person = parsers.parse_json_person_detail(raw_json)
    assert person is not None
    assert person.name == "Kevin Costner"
    assert "Guardia del corpo" in person.knownfor


def test_parse_json_series():
    raw_json = load_sample("sample_series.json")
    series = parsers.parse_json_movie(raw_json)
    assert series is not None

    # basic checks for a series
    assert series.is_series()
    assert series.imdbId == "tt1520211"
    assert series.url == "https://www.imdb.com/title/tt1520211/"

    # info_series must be present and contain lists
    assert hasattr(series, "info_series")
    assert series.info_series is not None
    assert isinstance(series.info_series.display_seasons, list)
    assert len(series.info_series.display_seasons) == 11
    assert isinstance(series.info_series.display_years, list)
    assert len(series.info_series.display_years) == 13
    assert isinstance(series.info_series.creators, list)
    assert series.info_series.creators[0].id == "0001104"



    # at least seasons or years should be present
    assert len(series.info_series.display_seasons) >= 1 or len(series.info_series.display_years) >= 1

    # categories should include cast
    # '0005342' id first cast member
    assert "cast" in series.categories
