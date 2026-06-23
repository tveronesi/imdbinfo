from imdbinfo.proxy import set_proxy, get_proxy


def test_get_proxy_returns_none_by_default():
    set_proxy(None)
    assert get_proxy() is None


def test_set_proxy_sets_dict():
    proxies = {"http": "http://proxy:8080", "https": "http://proxy:8080"}
    set_proxy(proxies)
    assert get_proxy() == proxies


def test_set_proxy_none_clears():
    set_proxy({"http": "http://proxy:8080"})
    set_proxy(None)
    assert get_proxy() is None


def test_set_proxy_validates_dict():
    set_proxy("http://proxy:8080")
    assert get_proxy() is None
