import pytest

from imdbinfo import services
from imdbinfo.config import configure
from imdbinfo.graphql_adapter import graphql_title_to_next_data
from imdbinfo.parsers import OldCategoryIdToNewCategoryIdObject, parse_json_movie

STARS = OldCategoryIdToNewCategoryIdObject["stars"]


def _title(kind="movie", **extra):
    title = {
        "id": "tt1490017",
        "titleType": {"id": kind},
        "titleText": {"text": "The LEGO Movie"},
        "originalTitleText": {"text": "The Lego Movie"},
        "releaseYear": {"year": 2014, "endYear": None},
        "runtime": {"seconds": 6000},
        "ratingsSummary": {"aggregateRating": 7.7, "voteCount": 10},
        "wins": {"total": 72},
        "nominationsExcludeWins": {"total": 68},
        "prestigiousAwardSummary": {
            "wins": 0,
            "nominations": 1,
            "awardNomination": {"award": {"text": "Oscar"}},
        },
        "countriesOfOrigin": {"countries": [{"id": "US", "text": "United States"}]},
        "keywords": {"edges": [{"node": {"keyword": {"text": {"text": "lego"}}}}]},
        "companyCredits": {
            "edges": [
                {
                    "node": {
                        "company": {"id": "co0002663", "companyText": {"text": "Warner Bros."}},
                        "category": {"id": "production", "text": "Production"},
                        "displayableProperty": {"value": {"plainText": "Warner Bros."}},
                        "attributes": [],
                        "countries": None,
                    }
                }
            ]
        },
        "principalCreditsV2": [
            {
                "grouping": {"groupingId": STARS, "text": "Stars"},
                "credits": [{"name": {"id": "nm0695435", "nameText": {"text": "Chris Pratt"}}}],
            }
        ],
        "credits": {
            "edges": [
                {
                    "node": {
                        "__typename": "Cast",
                        "name": {"id": "nm0004715", "nameText": {"text": "Will Arnett"}},
                        "category": {"id": "actor", "text": "Actor"},
                        "characters": [{"name": "Batman"}],
                        "attributes": [{"text": "voice"}],
                    }
                },
                {
                    "node": {
                        "__typename": "Crew",
                        "name": {"id": "nm0520488", "nameText": {"text": "Phil Lord"}},
                        "category": {"id": "director", "text": "Director"},
                        "jobs": [],
                    }
                },
            ]
        },
    }
    title.update(extra)
    return title


def test_graphql_movie_adapter():
    movie = parse_json_movie(graphql_title_to_next_data(_title()))
    assert movie.imdbId == "tt1490017"
    assert movie.kind == "movie"
    assert movie.duration == 100
    assert movie.awards.wins == 72
    assert movie.awards.prestigious_award["name"] == "Oscar"
    assert movie.country_codes == ["US"]
    assert movie.storyline_keywords == ["lego"]
    assert movie.production == ["Warner Bros."]
    assert [p.name for p in movie.stars] == ["Chris Pratt"]
    assert [p.name for p in movie.directors] == ["Phil Lord"]
    cast = movie.categories["cast"][0]
    assert cast.characters == ["Batman"]
    assert cast.attributes == "(voice)"
    assert movie.company_credits["production"][0].name == "Warner Bros."


def test_graphql_series_adapter():
    title = _title(
        "tvSeries",
        episodes={
            "displayableYears": {"edges": [{"node": {"year": "2010"}}, {"node": {"year": "2011"}}]},
            "displayableSeasons": {"edges": [{"node": {"season": "1"}}, {"node": {"season": "2"}}]},
        },
    )
    movie = parse_json_movie(graphql_title_to_next_data(title))
    assert movie.is_series()
    assert movie.info_series.display_years == ["2011", "2010"]
    assert movie.info_series.display_seasons == ["2", "1"]


def test_graphql_episode_adapter():
    title = _title(
        "tvEpisode",
        series={
            "series": {
                "id": "tt0944947",
                "titleText": {"text": "Game of Thrones"},
                "originalTitleText": {"text": "Game of Thrones"},
            },
            "episodeNumber": {"episodeNumber": 1, "seasonNumber": 1},
        },
    )
    movie = parse_json_movie(graphql_title_to_next_data(title))
    assert movie.is_episode()
    assert movie.info_episode.season_n == 1
    assert movie.info_episode.series_imdbId == "tt0944947"


def test_get_movie_graphql_uses_query_defaults_and_locale(monkeypatch):
    seen = {}

    def fake(headers, term, payload, url):
        seen["headers"] = headers
        seen["variables"] = payload["variables"]
        seen["query"] = payload["query"]
        return {"data": {"title": _title()}}

    monkeypatch.setattr(services, "request_graphql_url", fake)
    services.get_movie_graphql.cache_clear()
    configure(
        locale="it",
        max_items_credits=31,
        max_items_images=32,
        max_items_interests=33,
        max_items_akas=34,
        max_items_trivia=35,
        max_items_reviews=36,
        max_items_guide_items=37,
        max_items_quotes=38,
    )
    movie = services.get_movie_graphql("1490017")
    assert seen["variables"] == {"id": "tt1490017"}
    assert seen["headers"]["x-imdb-user-country"] == "IT"
    assert "credits(first: 250)" in seen["query"]
    assert "interests(first: 20)" in seen["query"]
    assert "akas(first: 10)" in seen["query"]
    assert "primaryVideos(first: 5)" in seen["query"]
    assert "reviews(" not in seen["query"]
    assert "trivia(" not in seen["query"]
    assert "guideItems(" not in seen["query"]
    assert "quotes(" not in seen["query"]
    assert movie.title == "The Lego Movie"


def test_get_movie_graphql_missing_title(monkeypatch):
    monkeypatch.setattr(services, "request_graphql_url", lambda *a: {"data": {"title": None}})
    services.get_movie_graphql.cache_clear()
    with pytest.raises(services.ParseError):
        services.get_movie_graphql("tt0000001")
