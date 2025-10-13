# Field Parser Plugins

The imdbinfo package supports a plugin system based on [pluggy](https://pluggy.readthedocs.io/) that allows you to customize how specific fields are parsed from IMDb data.

## Overview

Field parser plugins enable you to:
- Customize parsing logic for specific fields (e.g., `title`, `rating`, `genres`)
- Transform data before it's validated by Pydantic models
- Add business logic or data enrichment during parsing
- Filter or modify lists and other complex data structures

## Basic Concepts

### Hook Specification

The plugin system uses the `parse_field` hook which receives:
- `field_name`: The name of the field being parsed (e.g., "title", "rating")
- `raw_value`: The raw value extracted from JSON (result of jmespath query)
- `raw_json`: The complete raw JSON data for additional context

### Plugin Requirements

A plugin must:
1. Implement the `parse_field` method with the `@hookimpl` decorator
2. Return the parsed value for fields it handles, or `None` for fields it doesn't handle
3. Return values compatible with the Pydantic model field types

## Creating a Plugin

### Simple Example

```python
import pluggy
from imdbinfo import register_field_parser, get_movie

hookimpl = pluggy.HookimplMarker("imdbinfo")

class UppercaseTitlePlugin:
    """Convert movie titles to uppercase."""
    
    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        if field_name == "title" and raw_value:
            return raw_value.upper()
        return None

# Register the plugin
plugin = UppercaseTitlePlugin()
register_field_parser(plugin)

# Use it
movie = get_movie("tt0133093")
print(movie.title)  # "THE MATRIX"

# Cleanup
from imdbinfo import unregister_field_parser
unregister_field_parser(plugin)
```

### Configurable Plugin

```python
class RatingConverterPlugin:
    """Convert ratings to a different scale."""
    
    def __init__(self, target_scale=100):
        self.target_scale = target_scale
    
    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        if field_name == "rating" and raw_value is not None:
            # Convert from 0-10 to target scale
            return (raw_value / 10.0) * self.target_scale
        return None

# Use with different scales
plugin = RatingConverterPlugin(target_scale=5)  # Convert to 0-5 scale
register_field_parser(plugin)
```

### Context-Aware Plugin

```python
class TitleWithYearPlugin:
    """Add year to title using context from raw JSON."""
    
    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        if field_name == "title" and raw_value:
            # Extract year from raw JSON
            try:
                year = raw_json["props"]["pageProps"]["aboveTheFoldData"]["releaseYear"]["year"]
                return f"{raw_value} ({year})"
            except (KeyError, TypeError):
                return raw_value
        return None
```

## Supported Fields

Currently, the following fields support plugins:
- `title` - Movie/series title
- `rating` - IMDb rating
- `votes` - Number of votes
- `genres` - List of genres

More fields can be added by updating the `pjmespatch` calls in `parsers.py` to include the `field_name` parameter.

## Important Considerations

### Type Safety

Plugins must return values compatible with the Pydantic model field types:

```python
# ✅ Good: Returns correct type
@hookimpl
def parse_field(self, field_name, raw_value, raw_json):
    if field_name == "rating":
        return float(raw_value)  # rating expects float
    return None

# ❌ Bad: Returns wrong type
@hookimpl
def parse_field(self, field_name, raw_value, raw_json):
    if field_name == "rating":
        return "8.7"  # Pydantic will fail validation!
    return None
```

### Plugin Order

When multiple plugins handle the same field, the **first non-None result** is used. Plugins are called in the order they were registered.

### Return None for Unhandled Fields

Always return `None` for fields your plugin doesn't handle:

```python
@hookimpl
def parse_field(self, field_name, raw_value, raw_json):
    if field_name == "title":
        return raw_value.upper()
    # Return None for all other fields
    return None
```

## API Reference

### `register_field_parser(plugin)`
Register a field parser plugin.

```python
from imdbinfo import register_field_parser
register_field_parser(MyPlugin())
```

### `unregister_field_parser(plugin)`
Unregister a previously registered plugin.

```python
from imdbinfo import unregister_field_parser
unregister_field_parser(plugin)
```

### `list_registered_plugins()`
Get a list of all registered plugins.

```python
from imdbinfo import list_registered_plugins
plugins = list_registered_plugins()
print(f"Active plugins: {len(plugins)}")
```

## Examples

See `examples/usage_example_plugins.py` for comprehensive examples including:
- Title formatting
- Rating conversion
- Genre filtering
- Using multiple plugins together

## Advanced: Creating Reusable Plugin Packages

You can create reusable plugin packages that users can install:

```python
# my_imdb_plugins/__init__.py
import pluggy

hookimpl = pluggy.HookimplMarker("imdbinfo")

class MyCustomPlugin:
    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        # Custom logic
        pass
```

Users can then:
```python
from my_imdb_plugins import MyCustomPlugin
from imdbinfo import register_field_parser

register_field_parser(MyCustomPlugin())
```

## Future Enhancements

Future versions may support:
- More fields with plugin support
- Different hook types (e.g., pre-parse, post-validate)
- Plugin discovery via entry points
- Plugin configuration via files

## Contributing

To add plugin support for additional fields:
1. Update the `pjmespatch` call in `parsers.py` to include `field_name` parameter
2. Ensure the field name is descriptive and consistent
3. Add tests for the new field
4. Update this documentation
