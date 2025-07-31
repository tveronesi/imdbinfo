from imdbinfo.models import Person, CastMember, MovieInfo, MovieDetail


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
    info = MovieInfo.from_movie_search(data)
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
