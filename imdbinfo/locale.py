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

import logging

logger = logging.getLogger(__name__)
SUPPORTED_LOCALES = ("en", "fr-ca", "fr", "hi", "de", "it", "es", "pt", "es-es")
DEFAULT_LOCALE = "en"  # fallback locale
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
    if lcl not in SUPPORTED_LOCALES:
        logger.warning("Locale '%s' is not supported. Using '%s'", lcl, DEFAULT_LOCALE)
        lcl = DEFAULT_LOCALE
    if lcl == "en":
        return "" # used to build the url and en is the default one the url doesn't contain it
    return lcl


def _retrieve_url_lang(locale=None):
    """
    Internal function to retrieve the locale for URL composition.
    Priority: function argument > configured locale > default locale
    """
    lcl = locale or _configured_locale or DEFAULT_LOCALE
    if lcl not in SUPPORTED_LOCALES:
        logger.warning("Locale '%s' is not supported. Using '%s'", lcl, DEFAULT_LOCALE)
        lcl = DEFAULT_LOCALE
    if lcl == "en":
        return ""
    return lcl
