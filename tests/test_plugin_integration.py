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

"""Integration tests for plugin system with actual parsing."""

import json
import os
import pytest
import pluggy
from imdbinfo import parsers
from imdbinfo.plugin_manager import (
    register_field_parser,
    unregister_field_parser,
    get_plugin_manager,
)

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_json_source")

hookimpl = pluggy.HookimplMarker("imdbinfo")


def load_sample(filename):
    """Load a sample JSON file."""
    with open(os.path.join(SAMPLE_DIR, filename), "r") as f:
        return json.load(f)


@pytest.fixture
def clean_plugins():
    """Clean up plugins before and after tests."""
    pm = get_plugin_manager()
    for plugin in list(pm.get_plugins()):
        pm.unregister(plugin)
    yield
    for plugin in list(pm.get_plugins()):
        pm.unregister(plugin)


def test_plugin_with_real_movie_parsing(clean_plugins):
    """Test that a plugin actually modifies movie parsing results."""
    
    class TitlePrefixPlugin:
        """Plugin that adds a prefix to movie titles."""
        
        @hookimpl
        def parse_field(self, field_name, raw_value, raw_json):
            if field_name == "title" and raw_value:
                return f"Movie: {raw_value}"
            return None
    
    # Parse without plugin
    raw_json = load_sample("sample_resource.json")
    movie1 = parsers.parse_json_movie(raw_json)
    assert movie1.title == "The Matrix"
    
    # Register plugin and parse again
    plugin = TitlePrefixPlugin()
    register_field_parser(plugin)
    
    movie2 = parsers.parse_json_movie(raw_json)
    assert movie2.title == "Movie: The Matrix"
    
    # Cleanup
    unregister_field_parser(plugin)


def test_plugin_modifies_rating(clean_plugins):
    """Test that a plugin can modify rating values."""
    
    class RatingMultiplierPlugin:
        """Plugin that multiplies ratings."""
        
        @hookimpl
        def parse_field(self, field_name, raw_value, raw_json):
            if field_name == "rating" and raw_value is not None:
                return raw_value * 10  # Convert to 0-100 scale
            return None
    
    raw_json = load_sample("sample_resource.json")
    
    # Parse without plugin
    movie1 = parsers.parse_json_movie(raw_json)
    original_rating = movie1.rating
    assert original_rating == 8.7
    
    # Register plugin and parse again
    plugin = RatingMultiplierPlugin()
    register_field_parser(plugin)
    
    movie2 = parsers.parse_json_movie(raw_json)
    assert movie2.rating == 87.0
    
    unregister_field_parser(plugin)


def test_plugin_filters_genres(clean_plugins):
    """Test that a plugin can filter genre lists."""
    
    class GenreFilterPlugin:
        """Plugin that filters out specific genres."""
        
        @hookimpl
        def parse_field(self, field_name, raw_value, raw_json):
            if field_name == "genres" and raw_value:
                # Remove "Action" from genres
                return [g for g in raw_value if g != "Action"]
            return None
    
    raw_json = load_sample("sample_resource.json")
    
    # Parse without plugin
    movie1 = parsers.parse_json_movie(raw_json)
    assert "Action" in movie1.genres
    
    # Register plugin and parse again
    plugin = GenreFilterPlugin()
    register_field_parser(plugin)
    
    movie2 = parsers.parse_json_movie(raw_json)
    assert "Action" not in movie2.genres
    assert "Sci-Fi" in movie2.genres  # Other genres should remain
    
    unregister_field_parser(plugin)


def test_plugin_respects_pydantic_types(clean_plugins):
    """Test that plugins must respect Pydantic model types or validation fails."""
    
    class BadTypePlugin:
        """Plugin that returns wrong type - should cause validation error."""
        
        @hookimpl
        def parse_field(self, field_name, raw_value, raw_json):
            # Return string for fields that expect numbers
            if field_name in ("rating", "votes"):
                return "INVALID_TYPE"
            return None
    
    raw_json = load_sample("sample_resource.json")
    
    plugin = BadTypePlugin()
    register_field_parser(plugin)
    
    # Should raise validation error because plugin returns wrong type
    with pytest.raises(Exception) as exc_info:
        parsers.parse_json_movie(raw_json)
    
    # Check it's a Pydantic validation error
    assert "ValidationError" in str(type(exc_info.value))
    
    unregister_field_parser(plugin)


def test_multiple_plugins_processing_order(clean_plugins):
    """Test that multiple plugins can handle the same field."""
    
    class FirstPlugin:
        @hookimpl
        def parse_field(self, field_name, raw_value, raw_json):
            if field_name == "title" and raw_value:
                return f"First-{raw_value}"
            return None
    
    class SecondPlugin:
        @hookimpl
        def parse_field(self, field_name, raw_value, raw_json):
            if field_name == "title" and raw_value:
                return f"Second-{raw_value}"
            return None
    
    raw_json = load_sample("sample_resource.json")
    
    # Register plugins in order
    plugin1 = FirstPlugin()
    plugin2 = SecondPlugin()
    register_field_parser(plugin1)
    register_field_parser(plugin2)
    
    movie = parsers.parse_json_movie(raw_json)
    # The system returns the first non-None result from the list of results
    # Pluggy returns results in reverse registration order by default
    assert movie.title in ("First-The Matrix", "Second-The Matrix")
    
    unregister_field_parser(plugin1)
    unregister_field_parser(plugin2)
