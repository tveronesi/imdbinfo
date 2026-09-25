# MIT License
# Copyright (c) 2025 tveronesi+imdbinfo@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Locale and internationalization support for imdbinfo.

This module provides functions to configure language locales for IMDb API requests.
The library supports multiple locales for different regions and languages.

Supported Locales
-----------------
- ``"en"`` — English (default)
- ``"fr-ca"`` — French (Canada)
- ``"fr"`` — French
- ``"hi"`` — Hindi
- ``"de"`` — German
- ``"it"`` — Italian
- ``"es"`` — Spanish
- ``"pt"`` — Portuguese
- ``"es-es"`` — Spanish (Spain)

Examples
--------

```python
>>> from imdbinfo import set_locale, get_movie
>>> set_locale("it")  # Set global locale to Italian
>>> movie = get_movie("tt0133093")  # All requests now use Italian
```

Override locale per-request:

```python
>>> from imdbinfo import get_movie
>>> movie = get_movie("tt0133093", locale="it")  # Italian for this call only
```
"""

import logging

logger = logging.getLogger(__name__)

SUPPORTED_LOCALES = ("en", "fr-ca", "fr", "hi", "de", "it", "es", "pt", "es-es")
LOCALE_TO_COUNTRY_CODE = {
    "en": "EN",
    "fr-ca": "FR",
    "fr": "FR",
    "hi": "IN",
    "de": "DE",
    "it": "IT",
    "es": "ES",
    "pt": "PT",
    "es-es": "ES",
}
DEFAULT_LOCALE = "en"
_configured_locale = None


def set_locale(locale: str):
    """Set the global locale for all IMDb API requests.

    Once set, all subsequent calls to imdbinfo functions will use the configured
    locale unless overridden with a per-call ``locale`` parameter.

    Parameters
    ----------
    locale : str
        Locale code. Must be one of: ``"en"``, ``"fr-ca"``, ``"fr"``, ``"hi"``,
        ``"de"``, ``"it"``, ``"es"``, ``"pt"``, ``"es-es"``.
        If an unsupported locale is provided, silently falls back to ``"en"``.

    Warnings
    --------
    If an invalid locale is provided or the locale type is not a string,
    a warning is logged and the default locale (``"en"``) is used.

    Examples
    --------

    ```python
    >>> from imdbinfo import set_locale
    >>> set_locale("it")
    >>> # All subsequent API calls use Italian locale
    ```

    ```python
    >>> from imdbinfo import set_locale, get_movie
    >>> set_locale("fr")  # French
    >>> movie = get_movie("tt0133093")
    ```
    """
    global _configured_locale
    # accept only a single supported locale string
    if not isinstance(locale, str):
        logger.warning(
            "Invalid locale type: %r. Locale must be a string. Falling back to default '%s'.",
            locale,
            DEFAULT_LOCALE,
        )
        _configured_locale = DEFAULT_LOCALE
        return

    l = locale.strip()
    if l not in SUPPORTED_LOCALES:
        logger.warning(
            "Locale '%s' is not supported. Falling back to default '%s'.",
            l,
            DEFAULT_LOCALE,
        )
        _configured_locale = DEFAULT_LOCALE
        return

    _configured_locale = l


def _normalize_locale(lcl: str):
    """Validate and normalize a locale string.

    Parameters
    ----------
    lcl : str
        Locale code to validate.

    Returns
    -------
    str
        The normalized locale code if valid, otherwise ``"en"`` (default).
        Logs a warning if the locale is not supported.
    """
    if lcl not in SUPPORTED_LOCALES:
        logger.warning("Locale '%s' is not supported. Using '%s'", lcl, DEFAULT_LOCALE)
        return DEFAULT_LOCALE
    return lcl


def get_locale():
    """Get the currently configured global locale.

    Returns
    -------
    str
        The currently configured locale code. Returns empty string for English
        (``"en"``), or the locale code (e.g., ``"it"``, ``"fr"``) for other locales.
        Defaults to ``"en"`` if no locale has been set.

    Examples
    --------

    ```python
    >>> from imdbinfo import set_locale, get_locale
    >>> get_locale()
    ''
    >>> set_locale("it")
    >>> get_locale()
    'it'
    ```
    """
    lcl = _configured_locale or DEFAULT_LOCALE
    lcl = _normalize_locale(lcl)
    return "" if lcl == DEFAULT_LOCALE else lcl


def _retrieve_url_lang(locale=None):
    """Retrieve the URL language parameter for a given locale.

    Internal function used to construct IMDb API request URLs with the appropriate
    language parameter.

    Parameters
    ----------
    locale : str, optional
        Locale code. If ``None``, uses the globally configured locale.

    Returns
    -------
    str
        Empty string for English (``"en"``), or the locale code for other locales.
        Returns ``""`` by default; used as a path component in URLs (e.g., ``/en/`` vs. ``/it/``).
    """
    lcl = locale or _configured_locale or DEFAULT_LOCALE
    lcl = _normalize_locale(lcl)
    return "" if lcl == DEFAULT_LOCALE else lcl


def _get_country_code_from_lang_locale(locale=None):
    """Get the ISO country code for a given locale.

    Internal function used to construct IMDb GraphQL API requests with the
    appropriate country context (via the ``x-imdb-user-country`` header).

    Parameters
    ----------
    locale : str, optional
        Locale code. If ``None``, uses the globally configured locale.

    Returns
    -------
    str
        The ISO country code (e.g., ``"EN"``, ``"IT"``, ``"FR"``). Returns ``"EN"``
        if the locale is invalid or not found in the mapping.
    """
    lcl = locale or _configured_locale or DEFAULT_LOCALE
    lcl = _normalize_locale(lcl)
    return LOCALE_TO_COUNTRY_CODE.get(lcl, LOCALE_TO_COUNTRY_CODE[DEFAULT_LOCALE])
