import pytest
from pydantic import ValidationError

from imdbinfo.models import Person, CastMember, MovieBriefInfo, MovieDetail, BulkedEpisode
from imdbinfo.models import SeriesMixin
from imdbinfo.models import InfoSeries, InfoEpisode
from imdbinfo.models import (
    ParentalGuideContentDescription,
    ParentalGuideCategory,
    ParentalGuideList,
)


@pytest.mark.parametrize(
    ("season", "episode", "expected_season", "expected_episode"),
    [
        ("", "", None, None),
        ("", "2", None, 2),
        ("1", "", 1, None),
        ("1", "2", 1, 2),
        (0, 0, 0, 0),
        (None, None, None, None),
    ],
)
def test_bulked_episode_numbers(season, episode, expected_season, expected_episode):
    data = {
        "titleId": "tt14136640",
        "titleText": "Joseph Losey",
        "series": {"seasonNumber": season, "episodeNumber": episode},
        "releaseDate": None,
    }

    result = BulkedEpisode.from_bulked_episode_data(data)
    assert result.season_number == expected_season
    assert result.episode_number == expected_episode


def test_bulked_episode_invalid_number_is_not_silently_discarded():
    data = {
        "titleId": "tt14136640",
        "titleText": "Joseph Losey",
        "series": {"seasonNumber": "invalid", "episodeNumber": "2"},
        "releaseDate": None,
    }

    with pytest.raises(ValidationError):
        BulkedEpisode.from_bulked_episode_data(data)


def test_person_from_directors():
    data = {"name": {"nameText": {"text": "Lana Wachowski"}, "id": "nm0905154"}}
    person = Person.from_directors(data)
    assert person.name == "Lana Wachowski"
    assert person.imdb_id == "0905154"
    assert person.job == "Director"
    assert person.url == "https://www.imdb.com/name/nm0905154"


def test_cast_member_from_cast():
    data = {
        "rowTitle": "Keanu Reeves",
        "id": "nm0000206",
        "characters": ["Neo"],
        "imageProps": {"imageModel": {"url": "http://example.com/neo.jpg"}},
    }
    cast = CastMember.from_cast(data)
    assert cast.name == "Keanu Reeves"
    assert cast.characters == ["Neo"]
    assert cast.picture_url == "http://example.com/neo.jpg"


def test_movieinfo_from_movie_search():
    data = {
        "__typename": "Title",
        "id": "tt0133093",
        "titleText": {"text": "The Matrix"},
        "canonicalUrl": "https://www.imdb.com/title/tt0133093/",
        "originalTitleText": {"text": "The Matrix"},
        "releaseDate": {"year": 1999, "month": 9, "day": 11},
        "primaryImage": {
            "url": "https://m.media-amazon.com/images/M/MV5BN2NmN2VhMTQtMDNiOS00NDlhLTliMjgtODE2ZTY0ODQyNDRhXkEyXkFqcGc@._V1_.jpg"
        },
        "titleType": {
            "id": "movie",
            "text": "Movie",
            "categories": [{"id": "movie", "text": "Movie", "value": "movie"}],
        },
        "ratingsSummary": {"aggregateRating": 8.7},
        "runtime": {"seconds": 8160},
    }
    info = MovieBriefInfo.from_movie_search(data)
    assert info.title == "The Matrix"
    assert info.imdb_id == "0133093"
    assert info.url == "https://www.imdb.com/title/tt0133093/"


def test_movie_detail_validator_lists():
    data = {
        "id": "1",
        "imdb_id": "1",
        "imdbId": "tt1",
        "title": "Test",
        "languages": None,
        "genres": None,
        "country_codes": None,
    }
    movie = MovieDetail.model_validate(data)
    assert movie.languages == []
    assert movie.genres == []
    assert movie.country_codes == []


def test_series_mixin_is_series_and_is_episode():
    class Dummy(SeriesMixin):
        def __init__(self, kind):
            self.kind = kind

    assert Dummy("tvSeries").is_series() is True
    assert Dummy("tvMiniSeries").is_series() is True
    assert Dummy("podcastSeries").is_series() is True
    assert Dummy("movie").is_series() is False
    assert Dummy("tvEpisode").is_episode() is True
    assert Dummy("podcastEpisode").is_episode() is True
    assert Dummy("movie").is_episode() is False


def test_info_series_filter_years_and_str():
    # Test validazione anni
    s = InfoSeries(
        display_years=["2013", "2014", "abcd", "1999"], display_seasons=["1", "2"]
    )
    assert s.display_years == ["2013", "2014", "1999"]
    # Test stringa
    s2 = InfoSeries(
        display_years=["2013", "2014", "2015"], display_seasons=["1", "2", "3"]
    )
    assert str(s2) == "Years: 2015-2013, Seasons: 3"
    s3 = InfoSeries(display_years=[], display_seasons=[])
    assert str(s3) == "Years: -, Seasons: 0"


def test_info_episode_str():
    e = InfoEpisode(
        season_n=1,
        episode_n=2,
        series_imdbId="tt123",
        series_title="Serie",
        series_title_localized=None,
    )
    assert str(e) == "Serie - S01E02 (tt123)"
    e2 = InfoEpisode(
        season_n=None,
        episode_n=None,
        series_imdbId="tt999",
        series_title="Titolo",
        series_title_localized=None,
    )
    assert str(e2) == "Titolo - S??E?? (tt999)"


def test_parental_guide_item_from_node():
    node = {"isSpoiler": True, "text": {"plaidHtml": "Contains spoilers"}}
    item = ParentalGuideContentDescription.from_node(node)
    assert item.is_spoiler is True
    assert item.text == "Contains spoilers"


def test_parental_guide_category_from_edge_and_severity():
    edge = {
        "category": {"id": "violence", "text": "Violence"},
        "guideItems": {
            "edges": [
                {
                    "node": {
                        "isSpoiler": False,
                        "text": {"plaidHtml": "Fighting scenes"},
                    }
                },
                {"node": {"isSpoiler": True, "text": {"plaidHtml": "Major spoiler"}}},
            ]
        },
        "severityBreakdown": [
            {"votedFor": 2, "voteType": "Mild"},
            {"votedFor": 8, "voteType": "Severe"},
            {"votedFor": 3, "voteType": "Moderate"},
        ],
    }
    cat = ParentalGuideCategory.from_edge(edge)
    assert cat.id == "violence"
    assert cat.text == "Violence"
    assert len(cat.content_descriptions) == 2
    assert cat.severity == "Severe"


def test_parental_guide_category_helpers():
    cat = ParentalGuideCategory(
        id="language",
        text="Language",
        content_descriptions=[
            ParentalGuideContentDescription(is_spoiler=False, text="Profanity"),
            ParentalGuideContentDescription(
                is_spoiler=True, text="Plot-revealing insult"
            ),
        ],
        severity="Mild",
    )
    assert cat.has_category_texts() is True
    assert cat.category_texts_list(spoiler=False) == ["Profanity"]
    assert cat.category_texts_list(spoiler=True) == ["Plot-revealing insult"]


def test_parental_guide_data_from_raw_and_list_categories():
    parental_guide = {
        "categories": [
            {
                "category": {"id": "violence", "text": "Violence"},
                "guideItems": {"edges": []},
                "severityBreakdown": [{"votedFor": 4, "voteType": "Moderate"}],
            }
        ]
    }
    pg = ParentalGuideList.from_raw(parental_guide)
    assert pg is not None
    assert len(pg.categories) == 1
    assert pg.summary == {"violence": "Moderate"}


def test_parental_guide_data_from_raw_with_empty_returns_none():
    assert ParentalGuideList.from_raw({}) is None
    assert ParentalGuideList.from_raw(None) is None
