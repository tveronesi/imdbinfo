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

import os

# SSL verification setting - can be controlled via environment variable
# Set to False to disable SSL certificate verification (not recommended for production)
_SSL_VERIFY = os.environ.get("IMDBINFO_VERIFY_SSL", "true").lower() != "false"


def set_ssl_verify(verify: bool) -> None:
    """
    Set SSL verification for all HTTP requests.
    
    Args:
        verify: True to verify SSL certificates (default), False to disable verification
    
    Warning:
        Disabling SSL verification is not recommended for production use as it makes
        connections vulnerable to man-in-the-middle attacks.
    """
    global _SSL_VERIFY
    _SSL_VERIFY = verify


def get_ssl_verify() -> bool:
    """
    Get the current SSL verification setting.
    
    Returns:
        bool: True if SSL verification is enabled, False otherwise
    """
    return _SSL_VERIFY
