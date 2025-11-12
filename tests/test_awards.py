from imdbinfo import parsers


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



