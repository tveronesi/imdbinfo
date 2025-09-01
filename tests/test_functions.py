from imdbinfo import services


def test_normalize_imdb_id_handles_valid_id():
    imdb_id, lang = services.normalize_imdb_id("tt0123456", "en")
    assert imdb_id == "0123456"
    assert lang == "" # empty lang for url

def test_normalize_imdb_id_handles_id_without_prefix():
    imdb_id, lang = services.normalize_imdb_id("123456", "it")
    assert imdb_id == "0123456"
    assert lang == "it"

def test_normalize_imdb_id_handles_id_with_extra_characters():
    imdb_id, lang = services.normalize_imdb_id("tt00abc123456", "yy")
    assert imdb_id == "0123456"
    assert lang == "" # fallback to locale en , empty lang for url

def test_normalize_imdb_id_handles_non_numeric_id():
    try:
        services.normalize_imdb_id("ttabcdef", "en")
        assert False, "Expected ValueError for non-numeric ID"
    except ValueError:
        pass

def test_normalize_imdb_id_handles_empty_id():
    try:
        services.normalize_imdb_id("", "en")
        assert False, "Expected ValueError for empty ID"
    except ValueError:
        pass

# test the following tt0012345 -> 0012345
def test_normalize_imdb_id_handles_leading_zeros():
    imdb_id, lang = services.normalize_imdb_id("tt0012345", "en")
    assert imdb_id == "0012345"
    assert lang == "" # empty lang for url

# test 123456789 -> 123456789
def test_normalize_imdb_id_handles_long_id():
    imdb_id, lang = services.normalize_imdb_id("123456789", "en")
    assert imdb_id == "123456789"
    assert lang == "" # empty lang for url

# test 1 -> 0000001
def test_normalize_imdb_id_handles_short_id():
    imdb_id, lang = services.normalize_imdb_id("1", "en")
    assert imdb_id == "0000001"
    assert lang == "" # empty lang for url

# test 1 -> 0000001
def test_normalize_imdb_id_handles_short_id_int():
    imdb_id, lang = services.normalize_imdb_id(1, "en")
    assert imdb_id == "0000001"
    assert lang == "" # empty lang for url

def test_normalize_imdb_id_handles_long_id_int():
    imdb_id, lang = services.normalize_imdb_id(123456789, "es")
    assert imdb_id == "123456789"
    assert lang == "es" # empty lang for url