import logging
from unittest.mock import DEFAULT

logger = logging.getLogger(__name__)
supported_locales = [
    "en", "fr-ca","fr","hi", "de", "it", "es", "pt", "es", "es-es"
]

DEFAULT_LOCALE = "en"
_configured_locale = None

def set_locale(locale: str):
    global _configured_locale
    _configured_locale = locale

def get_locale():
    lcl = _configured_locale or DEFAULT_LOCALE
    if lcl not in supported_locales:
        logger.warning("Locale '%s' is not supported. Using '%s'", lcl, DEFAULT_LOCALE)
        lcl = DEFAULT_LOCALE
    if lcl == "en":
        return ""
    return lcl