#!/usr/bin/env python
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
Example of using field parser plugins with imdbinfo.

This example demonstrates how to create and register custom field parsers
that modify how specific fields are parsed from IMDb data.
"""

import pluggy
from imdbinfo import get_movie, register_field_parser, unregister_field_parser, list_registered_plugins

# Create the hook implementation marker
hookimpl = pluggy.HookimplMarker("imdbinfo")


# Example 1: Simple title formatter plugin
class TitleFormatterPlugin:
    """Plugin that formats movie titles with custom styling."""
    
    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        """Add year to title if available."""
        if field_name == "title" and raw_value:
            # Get year from raw_json for context
            year = None
            try:
                year = raw_json.get("props", {}).get("pageProps", {}).get("aboveTheFoldData", {}).get("releaseYear", {}).get("year")
            except (AttributeError, KeyError):
                pass
            
            if year:
                return f"{raw_value} [{year}]"
            return raw_value
        return None


# Example 2: Rating converter plugin
class RatingConverterPlugin:
    """Plugin that converts ratings to a different scale."""
    
    def __init__(self, scale=10):
        """Initialize with target scale (default 10)."""
        self.scale = scale
    
    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        """Convert rating to specified scale."""
        if field_name == "rating" and raw_value is not None:
            # IMDb ratings are 0-10, convert to different scale
            return (raw_value / 10.0) * self.scale
        return None


# Example 3: Genre filter plugin
class GenreFilterPlugin:
    """Plugin that filters genres based on user preferences."""
    
    def __init__(self, include_only=None, exclude=None):
        """Initialize with genre filters.
        
        Args:
            include_only: If provided, only include these genres
            exclude: If provided, exclude these genres
        """
        self.include_only = include_only or []
        self.exclude = exclude or []
    
    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        """Filter genres based on configuration."""
        if field_name == "genres" and raw_value:
            genres = raw_value
            
            # Apply include filter if specified
            if self.include_only:
                genres = [g for g in genres if g in self.include_only]
            
            # Apply exclude filter
            if self.exclude:
                genres = [g for g in genres if g not in self.exclude]
            
            return genres
        return None


def main():
    """Demonstrate plugin usage."""
    movie_id = "tt0133093"  # The Matrix
    
    # 1. Fetch movie without plugins
    print("=" * 60)
    print("1. Fetching movie WITHOUT plugins")
    print("=" * 60)
    movie = get_movie(movie_id)
    print(f"Title: {movie.title}")
    print(f"Rating: {movie.rating}")
    print(f"Genres: {', '.join(movie.genres)}")
    print()
    
    # 2. Register and use title formatter plugin
    print("=" * 60)
    print("2. Using TitleFormatterPlugin")
    print("=" * 60)
    title_plugin = TitleFormatterPlugin()
    register_field_parser(title_plugin)
    
    movie = get_movie(movie_id)
    print(f"Title: {movie.title}")
    print()
    
    unregister_field_parser(title_plugin)
    
    # 3. Register and use rating converter plugin
    print("=" * 60)
    print("3. Using RatingConverterPlugin (0-100 scale)")
    print("=" * 60)
    rating_plugin = RatingConverterPlugin(scale=100)
    register_field_parser(rating_plugin)
    
    movie = get_movie(movie_id)
    print(f"Rating (0-100): {movie.rating}")
    print()
    
    unregister_field_parser(rating_plugin)
    
    # 4. Register and use genre filter plugin
    print("=" * 60)
    print("4. Using GenreFilterPlugin (exclude 'Action')")
    print("=" * 60)
    genre_plugin = GenreFilterPlugin(exclude=["Action"])
    register_field_parser(genre_plugin)
    
    movie = get_movie(movie_id)
    print(f"Genres (filtered): {', '.join(movie.genres)}")
    print()
    
    unregister_field_parser(genre_plugin)
    
    # 5. Use multiple plugins together
    print("=" * 60)
    print("5. Using MULTIPLE plugins together")
    print("=" * 60)
    title_plugin = TitleFormatterPlugin()
    rating_plugin = RatingConverterPlugin(scale=5)
    genre_plugin = GenreFilterPlugin(include_only=["Sci-Fi", "Action"])
    
    register_field_parser(title_plugin)
    register_field_parser(rating_plugin)
    register_field_parser(genre_plugin)
    
    print(f"Registered plugins: {len(list_registered_plugins())}")
    
    movie = get_movie(movie_id)
    print(f"Title: {movie.title}")
    print(f"Rating (0-5): {movie.rating}")
    print(f"Genres: {', '.join(movie.genres)}")
    print()
    
    # Cleanup
    unregister_field_parser(title_plugin)
    unregister_field_parser(rating_plugin)
    unregister_field_parser(genre_plugin)
    
    # 6. Verify plugins are cleared
    print("=" * 60)
    print("6. After unregistering all plugins")
    print("=" * 60)
    movie = get_movie(movie_id)
    print(f"Title: {movie.title}")
    print(f"Rating: {movie.rating}")
    print(f"Genres: {', '.join(movie.genres)}")
    print()
    
    print("=" * 60)
    print("Plugin demonstration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
