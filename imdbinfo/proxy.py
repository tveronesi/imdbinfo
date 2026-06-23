from typing import Optional, Dict

_configured_proxy: Optional[Dict] = None


def set_proxy(proxies: Optional[Dict]) -> None:
    global _configured_proxy
    if proxies is None:
        _configured_proxy = None
        return
    if not isinstance(proxies, dict):
        _configured_proxy = None
        return
    _configured_proxy = proxies


def get_proxy() -> Optional[Dict]:
    return _configured_proxy
