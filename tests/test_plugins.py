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

import pytest
import pluggy
from imdbinfo.plugin_manager import (
    register_field_parser,
    unregister_field_parser,
    parse_field_with_plugins,
    list_registered_plugins,
    get_plugin_manager,
)
from imdbinfo.hooks import FieldParserHookSpec


hookimpl = pluggy.HookimplMarker("imdbinfo")


class TestFieldParserPlugin:
    """Test plugin for field parsing."""

    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        if field_name == "title":
            return raw_value.upper() if raw_value else None
        return None


class AnotherTestPlugin:
    """Another test plugin."""

    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        if field_name == "rating":
            return raw_value * 2 if raw_value else None
        return None


@pytest.fixture
def clean_plugin_manager():
    """Fixture to clean up plugin manager between tests."""
    # Get plugin manager and unregister all plugins
    pm = get_plugin_manager()
    for plugin in list(pm.get_plugins()):
        pm.unregister(plugin)
    yield pm
    # Cleanup after test
    for plugin in list(pm.get_plugins()):
        pm.unregister(plugin)


def test_register_field_parser(clean_plugin_manager):
    """Test registering a field parser plugin."""
    plugin = TestFieldParserPlugin()
    register_field_parser(plugin)
    
    plugins = list_registered_plugins()
    assert plugin in plugins


def test_unregister_field_parser(clean_plugin_manager):
    """Test unregistering a field parser plugin."""
    plugin = TestFieldParserPlugin()
    register_field_parser(plugin)
    
    plugins = list_registered_plugins()
    assert plugin in plugins
    
    unregister_field_parser(plugin)
    plugins = list_registered_plugins()
    assert plugin not in plugins


def test_parse_field_with_plugins(clean_plugin_manager):
    """Test parsing a field with a registered plugin."""
    plugin = TestFieldParserPlugin()
    register_field_parser(plugin)
    
    result = parse_field_with_plugins("title", "The Matrix", {})
    assert result == "THE MATRIX"


def test_parse_field_without_matching_plugin(clean_plugin_manager):
    """Test parsing a field when no plugin handles it."""
    plugin = TestFieldParserPlugin()
    register_field_parser(plugin)
    
    # Plugin only handles "title", not "rating"
    result = parse_field_with_plugins("rating", 8.7, {})
    assert result == 8.7  # Should return unchanged


def test_parse_field_no_plugins(clean_plugin_manager):
    """Test parsing a field when no plugins are registered."""
    result = parse_field_with_plugins("title", "The Matrix", {})
    assert result == "The Matrix"  # Should return unchanged


def test_multiple_plugins_first_wins(clean_plugin_manager):
    """Test that when multiple plugins handle a field, first one wins."""
    plugin1 = TestFieldParserPlugin()  # Returns uppercase
    plugin2 = TestFieldParserPlugin()  # Would also return uppercase
    
    register_field_parser(plugin1)
    register_field_parser(plugin2)
    
    result = parse_field_with_plugins("title", "The Matrix", {})
    assert result == "THE MATRIX"


def test_plugin_with_raw_json_context(clean_plugin_manager):
    """Test that plugins receive the full raw_json for context."""
    
    class ContextAwarePlugin:
        @hookimpl
        def parse_field(self, field_name, raw_value, raw_json):
            if field_name == "title" and raw_json.get("year"):
                return f"{raw_value} ({raw_json['year']})"
            return None
    
    plugin = ContextAwarePlugin()
    register_field_parser(plugin)
    
    raw_json = {"year": 1999}
    result = parse_field_with_plugins("title", "The Matrix", raw_json)
    assert result == "The Matrix (1999)"


def test_plugin_returns_none_for_unhandled_fields(clean_plugin_manager):
    """Test that plugins return None for fields they don't handle."""
    plugin = TestFieldParserPlugin()  # Only handles "title"
    register_field_parser(plugin)
    
    result = parse_field_with_plugins("genres", ["Action", "Sci-Fi"], {})
    assert result == ["Action", "Sci-Fi"]  # Unchanged


def test_plugin_handles_none_values(clean_plugin_manager):
    """Test that plugins can handle None values gracefully."""
    plugin = TestFieldParserPlugin()
    register_field_parser(plugin)
    
    result = parse_field_with_plugins("title", None, {})
    assert result is None


def test_different_plugins_for_different_fields(clean_plugin_manager):
    """Test registering different plugins for different fields."""
    title_plugin = TestFieldParserPlugin()  # Handles title
    rating_plugin = AnotherTestPlugin()  # Handles rating
    
    register_field_parser(title_plugin)
    register_field_parser(rating_plugin)
    
    title_result = parse_field_with_plugins("title", "The Matrix", {})
    rating_result = parse_field_with_plugins("rating", 4.35, {})
    
    assert title_result == "THE MATRIX"
    assert rating_result == 8.7


def test_plugin_can_transform_data_types(clean_plugin_manager):
    """Test that plugins can transform data types appropriately."""
    
    class TypeTransformPlugin:
        @hookimpl
        def parse_field(self, field_name, raw_value, raw_json):
            if field_name == "rating" and isinstance(raw_value, (int, float)):
                # Return as string with 1 decimal
                return f"{raw_value:.1f}"
            return None
    
    plugin = TypeTransformPlugin()
    register_field_parser(plugin)
    
    result = parse_field_with_plugins("rating", 8.7, {})
    assert result == "8.7"
    assert isinstance(result, str)


def test_plugin_manager_singleton(clean_plugin_manager):
    """Test that get_plugin_manager returns the same instance."""
    pm1 = get_plugin_manager()
    pm2 = get_plugin_manager()
    assert pm1 is pm2
