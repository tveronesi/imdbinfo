from imdbinfo.models import Person, CastMember, MovieBriefInfo, MovieDetail
from imdbinfo.models import SeriesMixin
from imdbinfo.models import InfoSeries, InfoEpisode


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
        "id": "tt0133093",
        "titleNameText": "The Matrix",
        "titlePosterImageModel": {"url": "http://example.com/matrix.jpg"},
        "titleReleaseText": "1999",
        "imageType": "movie",
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

    assert Dummy('tvSeries').is_series() is True
    assert Dummy('tvMiniSeries').is_series() is True
    assert Dummy('podcastSeries').is_series() is True
    assert Dummy('movie').is_series() is False
    assert Dummy('tvEpisode').is_episode() is True
    assert Dummy('podcastEpisode').is_episode() is True
    assert Dummy('movie').is_episode() is False


def test_info_series_filter_years_and_str():
    # Test validazione anni
    s = InfoSeries(display_years=['2013', '2014', 'abcd', '1999'], display_seasons=['1', '2'])
    assert s.display_years == ['2013', '2014', '1999']
    # Test stringa
    s2 = InfoSeries(display_years=['2013', '2014', '2015'], display_seasons=['1', '2', '3'])
    assert str(s2) == 'Years: 2015-2013, Seasons: 3'
    s3 = InfoSeries(display_years=[], display_seasons=[])
    assert str(s3) == 'Years: -, Seasons: 0'


def test_info_episode_str():
    e = InfoEpisode(season_n=1, episode_n=2, series_imdbId='tt123', series_title='Serie', series_title_localized=None)
    assert str(e) == 'Serie - S01E02 (tt123)'
    e2 = InfoEpisode(season_n=None, episode_n=None, series_imdbId='tt999', series_title='Titolo', series_title_localized=None)
    assert str(e2) == 'Titolo - S??E?? (tt999)'
