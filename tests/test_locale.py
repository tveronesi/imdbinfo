from imdbinfo.locale import set_locale, get_locale


def test_set_locale_falls_back_to_default_for_unsupported_locale():
    assert get_locale() == ""

def test_set_locale_sets_supported_locale():
    set_locale("it")
    assert get_locale() == "it"

def test_get_locale_returns_default_when_no_locale_is_set():
    assert get_locale() == "it"

def test_set_locale_falls_back_to_default_for_unsupported_locale_again():
    set_locale("unsupported-locale")
    assert get_locale() == ""  # fallback to default which is "en" and returns ""
