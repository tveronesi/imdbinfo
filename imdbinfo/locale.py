import logging

logger = logging.getLogger(__name__)
supported_locales = ("en", "fr-ca","fr","hi", "de", "it", "es", "pt", "es", "es-es")


DEFAULT_LOCALE = "en" # fallback locale
_configured_locale = None

def set_locale(locale: str):
    """
        Set the locale for fetching data from IMDb.
        If the locale is not supported, it will fallback to DEFAULT_LOCALE.
    """
    global _configured_locale
    _configured_locale = locale

def get_locale():
    """
        Get the currently configured locale.
    """
    lcl = _configured_locale or DEFAULT_LOCALE
    if lcl not in supported_locales:
        logger.warning("Locale '%s' is not supported. Using '%s'", lcl, DEFAULT_LOCALE)
        lcl = DEFAULT_LOCALE
    if lcl == "en":
        return ""
    return lcl

def _retrieve_url_lang(l=None):
    """
        Internal function to retrieve the locale for URL construction.
        Priority: function argument > configured locale > default locale
    """
    lcl = l or _configured_locale or DEFAULT_LOCALE
    if lcl not in supported_locales:
        logger.warning("Locale '%s' is not supported. Using '%s'", lcl, DEFAULT_LOCALE)
        lcl = DEFAULT_LOCALE
    if lcl == "en":
        return ""
    return lcl