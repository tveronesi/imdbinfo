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

"""
Example field parser plugins for imdbinfo.

This module demonstrates how to create custom field parsers using the plugin system.
"""

import pluggy

hookimpl = pluggy.HookimplMarker("imdbinfo")


class UppercaseTitlePlugin:
    """Example plugin that converts movie titles to uppercase.
    
    This is a simple example to demonstrate the plugin system.
    In practice, you might want to do more sophisticated parsing,
    like cleaning up titles, extracting year from title, etc.
    """

    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        """Convert title field to uppercase."""
        if field_name == "title" and raw_value:
            return raw_value.upper()
        return None


class RatingRounderPlugin:
    """Example plugin that rounds rating values to 1 decimal place."""

    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        """Round rating to 1 decimal place."""
        if field_name == "rating" and raw_value is not None:
            try:
                return round(float(raw_value), 1)
            except (ValueError, TypeError):
                pass
        return None


class GenreFilterPlugin:
    """Example plugin that filters out specific genres.
    
    This plugin demonstrates how to modify list values.
    """

    def __init__(self, excluded_genres=None):
        """Initialize with genres to exclude.
        
        Args:
            excluded_genres: List of genre names to filter out.
        """
        self.excluded_genres = excluded_genres or []

    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        """Filter out excluded genres."""
        if field_name == "genres" and raw_value:
            return [g for g in raw_value if g not in self.excluded_genres]
        return None


# Example usage (to be placed in user code):
"""
from imdbinfo import register_field_parser, get_movie
from imdbinfo.example_plugins import UppercaseTitlePlugin

# Register the plugin
register_field_parser(UppercaseTitlePlugin())

# Now when you fetch a movie, the title will be in uppercase
movie = get_movie("tt0133093")
print(movie.title)  # Will print "THE MATRIX" instead of "The Matrix"
"""
