# Field Parser Plugin System Implementation Summary

## Overview

A comprehensive plugin system has been implemented for the imdbinfo package using the `pluggy` library. This system allows users to customize how specific fields are parsed from IMDb JSON data.

## What Was Implemented

### Core Components

1. **Hook Specification (`imdbinfo/hooks.py`)**
   - Defines the `FieldParserHookSpec` interface
   - Specifies the `parse_field` hook that plugins must implement
   - Documents the hook's parameters and return values

2. **Plugin Manager (`imdbinfo/plugin_manager.py`)**
   - Manages plugin registration and lifecycle
   - Provides `register_field_parser()`, `unregister_field_parser()`, and `list_registered_plugins()` functions
   - Implements `parse_field_with_plugins()` to apply plugins during parsing
   - Uses a singleton pattern for the global plugin manager

3. **Parser Integration (`imdbinfo/parsers.py`)**
   - Updated `pjmespatch()` to accept an optional `field_name` parameter
   - When `field_name` is provided, applies registered plugins to the field value
   - Currently supports plugins for: `title`, `rating`, `votes`, and `genres`
   - Plugin system is opt-in per field to maintain backward compatibility

4. **Public API (`imdbinfo/__init__.py`)**
   - Exports plugin management functions: `register_field_parser`, `unregister_field_parser`, `list_registered_plugins`
   - Makes plugin system easily accessible to users

### Example Plugins

**`imdbinfo/example_plugins.py`** includes three demonstration plugins:

1. **UppercaseTitlePlugin** - Converts movie titles to uppercase
2. **RatingRounderPlugin** - Rounds rating values to 1 decimal place
3. **GenreFilterPlugin** - Filters out specific genres from the list

### Testing

**Comprehensive test coverage with 17 new tests:**

1. **Unit Tests (`tests/test_plugins.py`)** - 12 tests covering:
   - Plugin registration/unregistration
   - Field parsing with and without plugins
   - Multiple plugins handling the same field
   - Context-aware plugins using raw_json
   - Type transformation
   - Plugin manager singleton behavior

2. **Integration Tests (`tests/test_plugin_integration.py`)** - 5 tests covering:
   - Real movie parsing with plugins
   - Rating modification
   - Genre filtering
   - Pydantic type validation with plugins
   - Multiple plugin processing order

All existing tests (44 total) continue to pass, ensuring no regression.

### Documentation

1. **Plugin Documentation (`docs/PLUGINS.md`)**
   - Comprehensive guide on creating and using plugins
   - API reference
   - Best practices and considerations
   - Multiple examples

2. **Example Usage Script (`examples/usage_example_plugins.py`)**
   - Working demonstration of the plugin system
   - Shows title formatting, rating conversion, genre filtering
   - Demonstrates using multiple plugins together

### Dependencies

- Added `pluggy` to `pyproject.toml` dependencies
- Updated `Dockerfile` to include pluggy

## How It Works

### Plugin Creation

```python
import pluggy

hookimpl = pluggy.HookimplMarker("imdbinfo")

class MyPlugin:
    @hookimpl
    def parse_field(self, field_name, raw_value, raw_json):
        if field_name == "title":
            return raw_value.upper()
        return None  # Don't handle other fields
```

### Plugin Registration and Usage

```python
from imdbinfo import register_field_parser, get_movie

plugin = MyPlugin()
register_field_parser(plugin)

movie = get_movie("tt0133093")
print(movie.title)  # "THE MATRIX"
```

### How Plugins Are Applied

1. Parser extracts raw value using jmespath
2. Optional post-processing function is applied
3. If `field_name` is provided, `parse_field_with_plugins()` is called
4. All registered plugins are queried via their `parse_field` hook
5. First non-None result is used, or raw value if no plugin handles it
6. Result is validated by Pydantic model

## Key Features

### Type Safety
Plugins must return values compatible with Pydantic model types, ensuring data integrity.

### Opt-in Design
Only fields explicitly configured with `field_name` parameter support plugins, maintaining backward compatibility.

### Context Awareness
Plugins receive the complete `raw_json` data, allowing them to make decisions based on additional context.

### Flexible Architecture
- Support for multiple plugins handling different fields
- Plugin registration/unregistration at runtime
- Clean separation between core parsing and plugin logic

## Extensibility

### Adding Plugin Support to New Fields

To add plugin support to additional fields:

1. Update the `pjmespatch` call in `parsers.py`:
   ```python
   data["field_name"] = pjmespatch(
       "json.path.to.field", raw_json,
       field_name="field_name"
   )
   ```

2. Ensure the field name is descriptive and consistent

3. Add tests for the new field

4. Update documentation

### Future Enhancements

The architecture supports potential future features:
- Different hook types (pre-parse, post-validate, etc.)
- Plugin discovery via setuptools entry points
- Configuration file support for plugins
- More sophisticated plugin ordering/priority

## Technical Decisions

### Why Pluggy?

- Industry standard (used by pytest)
- Lightweight and focused
- Excellent hook specification system
- Good documentation and community support

### Why Field-Level Plugins?

- Fine-grained control over parsing
- Easier to reason about plugin behavior
- Type safety at field level
- Simpler testing

### Why Opt-in?

- Maintains backward compatibility
- Minimal performance impact when not used
- Allows gradual adoption
- Keeps codebase clean

## Testing Strategy

Tests ensure:
- ✅ Plugins can be registered and unregistered
- ✅ Plugins correctly modify field values
- ✅ Plugins respect Pydantic types
- ✅ Multiple plugins work together
- ✅ Context-aware parsing works
- ✅ No regressions in existing functionality

## Conclusion

The implementation provides a robust, extensible plugin system that allows users to customize field parsing while maintaining:
- Type safety through Pydantic validation
- Backward compatibility with existing code
- Clean architecture and separation of concerns
- Comprehensive test coverage
- Excellent documentation

Users can now easily extend imdbinfo's parsing capabilities without modifying the core library.
