"""
Test that Pydantic Field defaults are properly used to avoid mutable default issues.
This test ensures that list and dict defaults don't share state between instances.
"""
from imdbinfo.models import (
    InfoSeries,
    CastMember,
    MovieDetail,
    SearchResult,
    PersonDetail,
    SeasonEpisodesList,
)


def test_info_series_list_defaults_are_independent():
    """Test that InfoSeries instances don't share list state."""
    series1 = InfoSeries()
    series2 = InfoSeries()
    
    # Modify series1's lists
    series1.display_years.append("2020")
    series1.display_seasons.append("1")
    
    # series2 should not be affected
    assert series2.display_years == []
    assert series2.display_seasons == []
    assert series1.display_years == ["2020"]
    assert series1.display_seasons == ["1"]


def test_cast_member_list_defaults_are_independent():
    """Test that CastMember instances don't share list state."""
    cast1 = CastMember(id="1", imdb_id="1", imdbId="nm1", name="Actor 1", url="url1")
    cast2 = CastMember(id="2", imdb_id="2", imdbId="nm2", name="Actor 2", url="url2")
    
    # Modify cast1's characters list
    cast1.characters.append("Character A")
    
    # cast2 should not be affected
    assert cast2.characters == []
    assert cast1.characters == ["Character A"]


def test_movie_detail_list_defaults_are_independent():
    """Test that MovieDetail instances don't share list state."""
    movie1 = MovieDetail(id="1", imdb_id="1", imdbId="tt1", title="Movie 1")
    movie2 = MovieDetail(id="2", imdb_id="2", imdbId="tt2", title="Movie 2")
    
    # Modify movie1's lists
    movie1.genres.append("Action")
    movie1.languages.append("en")
    
    # movie2 should not be affected
    assert movie2.genres == []
    assert movie2.languages == []
    assert movie1.genres == ["Action"]
    assert movie1.languages == ["en"]


def test_movie_detail_dict_defaults_are_independent():
    """Test that MovieDetail instances don't share dict state."""
    movie1 = MovieDetail(id="1", imdb_id="1", imdbId="tt1", title="Movie 1")
    movie2 = MovieDetail(id="2", imdb_id="2", imdbId="tt2", title="Movie 2")
    
    # Modify movie1's dicts
    movie1.certificates["US"] = ("PG-13", "some reason")
    
    # movie2 should not be affected
    assert movie2.certificates == {}
    assert movie1.certificates == {"US": ("PG-13", "some reason")}


def test_search_result_list_defaults_are_independent():
    """Test that SearchResult instances don't share list state."""
    result1 = SearchResult()
    result2 = SearchResult()
    
    # Modify result1's lists
    from imdbinfo.models import MovieBriefInfo
    movie = MovieBriefInfo(id="1", imdb_id="1", imdbId="tt1", title="Test", title_localized="Test")
    result1.titles.append(movie)
    
    # result2 should not be affected
    assert result2.titles == []
    assert len(result1.titles) == 1


def test_person_detail_list_and_dict_defaults_are_independent():
    """Test that PersonDetail instances don't share list/dict state."""
    person1 = PersonDetail(id="1", imdb_id="1", imdbId="nm1", name="Person 1", url="url1")
    person2 = PersonDetail(id="2", imdb_id="2", imdbId="nm2", name="Person 2", url="url2")
    
    # Modify person1's lists and dicts
    person1.knownfor.append("Movie A")
    person1.jobs.append("Actor")
    person1.credits["actor"] = []
    
    # person2 should not be affected
    assert person2.knownfor == []
    assert person2.jobs == []
    assert person2.credits == {}
    assert person1.knownfor == ["Movie A"]
    assert person1.jobs == ["Actor"]
    assert "actor" in person1.credits


def test_season_episodes_list_defaults_are_independent():
    """Test that SeasonEpisodesList instances don't share list state."""
    episodes1 = SeasonEpisodesList(series_imdbId="tt1", season_number=1)
    episodes2 = SeasonEpisodesList(series_imdbId="tt2", season_number=2)
    
    # Modify episodes1's list
    from imdbinfo.models import SeasonEpisode
    episode = SeasonEpisode(
        id="1", imdbId="tt1", imdb_id="1", title="Ep 1",
        season=1, episode=1, plot="Test"
    )
    episodes1.episodes.append(episode)
    
    # episodes2 should not be affected
    assert episodes2.episodes == []
    assert len(episodes1.episodes) == 1
