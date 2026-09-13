import json
import os
from unittest.mock import patch
from imdbinfo import parsers, get_awards, Award

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


def load_root_json(filename):
    with open(os.path.join(PROJECT_ROOT, filename), encoding="utf-8") as f:
        return json.load(f)


def test_parse_awards_with_full_node_returns_awardinfo():
    awards_node = [5, 10, {"award": {"text": "Oscar"}, "wins": 3, "nominations": 7}]
    aw = parsers._parse_awards(awards_node)
    assert aw.wins == 5
    assert aw.nominations == 10
    assert isinstance(aw.prestigious_award, dict)
    assert aw.prestigious_award.get("wins") == 3
    assert aw.prestigious_award.get("nominations") == 7
    assert aw.prestigious_award.get("name") == "Oscar"


def test_parse_awards_with_none_returns_zeroed_awardinfo():
    aw = parsers._parse_awards(None)
    assert aw.wins == 0
    assert aw.nominations == 0
    assert aw.prestigious_award is None


def test_parse_awards_with_partial_node_no_prestigious():
    awards_node = [2, 4]
    aw = parsers._parse_awards(awards_node)
    assert aw.wins == 2
    assert aw.nominations == 4
    assert aw.prestigious_award is None


def test_parse_awards_with_partial_prestigious_info_handles_missing_fields():
    awards_node = [1, 2, {"award": {}, "wins": 0}]
    aw = parsers._parse_awards(awards_node)
    assert aw.wins == 1
    assert aw.nominations == 2
    assert isinstance(aw.prestigious_award, dict)
    # missing nominations in prestigious award should default to 0 via parser logic
    assert aw.prestigious_award.get("wins") == 0
    assert aw.prestigious_award.get("nominations") == 0
    assert aw.prestigious_award.get("name") == ""


def test_parse_json_awards_tt5716464():
    raw_json = load_root_json("title_tt5716464_awards_.json")
    awards = parsers.parse_json_awards(raw_json)

    assert isinstance(awards, list)
    assert len(awards) == 6
    assert all(isinstance(a, Award) for a in awards)

    first_award = awards[0]
    assert first_award.event == "British Independent Film Awards"
    assert first_award.status == "2017 Nominee"
    assert first_award.award == "British Independent Film Award"
    assert first_award.category == "Best Make Up & Hair Design"
    assert first_award.nominees == "Jan Sewell"
    assert "British Independent Film Awards - 2017 Nominee - British Independent Film Award - Best Make Up & Hair Design - (Jan Sewell)" in str(first_award)


def test_parse_json_awards_tt0034583():
    raw_json = load_root_json("title_tt0034583_awards_.json")
    awards = parsers.parse_json_awards(raw_json)

    assert isinstance(awards, list)
    assert len(awards) == 27
    assert all(isinstance(a, Award) for a in awards)

    first_award = awards[0]
    assert first_award.event == "Academy Awards, USA"
    assert first_award.status == "1944 Winner"
    assert first_award.award == "Oscar"
    assert first_award.category == "Best Picture"
    assert first_award.nominees == ""
    assert str(first_award) == "Academy Awards, USA - 1944 Winner - Oscar - Best Picture"

    # award with nominees
    second_award = awards[1]
    assert second_award.status == "1944 Nominee"
    assert second_award.award == "Oscar"
    assert second_award.category == "Best Actor in a Leading Role"
    assert second_award.nominees == "Humphrey Bogart"
    assert "Humphrey Bogart" in str(second_award)


def test_parse_json_awards_empty():
    assert parsers.parse_json_awards({}) == []
    assert parsers.parse_json_awards(None) == []


def test_get_awards_service():
    raw_json = load_root_json("title_tt5716464_awards_.json")
    with patch("imdbinfo.services.request_json_url", return_value=raw_json) as mock_request:
        get_awards.cache_clear()
        awards = get_awards("5716464", locale="it")
        mock_request.assert_called_once_with("https://www.imdb.com/it/title/tt5716464/awards/")
        assert isinstance(awards, list)
        assert len(awards) == 6
        assert isinstance(awards[0], Award)
        assert awards[0].event == "British Independent Film Awards"
