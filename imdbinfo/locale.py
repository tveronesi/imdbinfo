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
DEFAULT_LOCALE = "en"
_configured_locale = None


def set_locale(locale: str):
    global _configured_locale
    _configured_locale = locale


def _normalize_locale(lcl: str):
    if lcl not in SUPPORTED_LOCALES:
        logger.warning("Locale '%s' is not supported. Using '%s'", lcl, DEFAULT_LOCALE)
        return DEFAULT_LOCALE
    return lcl


def get_locale():
    lcl = _configured_locale or DEFAULT_LOCALE
    lcl = _normalize_locale(lcl)
    return "" if lcl == DEFAULT_LOCALE else lcl


def _retrieve_url_lang(locale=None):
    lcl = locale or _configured_locale or DEFAULT_LOCALE
    lcl = _normalize_locale(lcl)
    return "" if lcl == DEFAULT_LOCALE else lcl
