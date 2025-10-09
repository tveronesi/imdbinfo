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

"""Plugin manager for imdbinfo field parser plugins."""

import logging
import pluggy
from typing import Any, Optional

from .hooks import FieldParserHookSpec

logger = logging.getLogger(__name__)

# Global plugin manager instance
_plugin_manager: Optional[pluggy.PluginManager] = None


def get_plugin_manager() -> pluggy.PluginManager:
    """Get or create the global plugin manager instance.

    Returns:
        The plugin manager instance.
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = pluggy.PluginManager("imdbinfo")
        _plugin_manager.add_hookspecs(FieldParserHookSpec)
        logger.debug("Plugin manager initialized")
    return _plugin_manager


def register_field_parser(plugin: Any) -> None:
    """Register a field parser plugin.

    Args:
        plugin: An object implementing the field parser hook(s).

    Example:
        >>> class MyFieldParser:
        ...     @pluggy.HookimplMarker("imdbinfo")
        ...     def parse_field(self, field_name, raw_value, raw_json):
        ...         if field_name == "title":
        ...             return raw_value.upper()
        ...         return None
        >>> register_field_parser(MyFieldParser())
    """
    pm = get_plugin_manager()
    pm.register(plugin)
    logger.info(f"Registered field parser plugin: {plugin}")


def unregister_field_parser(plugin: Any) -> None:
    """Unregister a field parser plugin.

    Args:
        plugin: The plugin object to unregister.
    """
    pm = get_plugin_manager()
    pm.unregister(plugin)
    logger.info(f"Unregistered field parser plugin: {plugin}")


def parse_field_with_plugins(field_name: str, raw_value: Any, raw_json: dict) -> Any:
    """Parse a field using registered plugins.

    This function calls all registered field parser plugins and returns the first
    non-None result. If no plugin handles the field, returns the raw_value unchanged.

    Args:
        field_name: The name of the field being parsed.
        raw_value: The raw value extracted from JSON.
        raw_json: The complete raw JSON data.

    Returns:
        The parsed value, or raw_value if no plugin handled it.
    """
    pm = get_plugin_manager()
    
    # Call all plugins and get their results
    # firstresult=True means return the first non-None result
    result = pm.hook.parse_field(
        field_name=field_name,
        raw_value=raw_value,
        raw_json=raw_json,
    )
    
    # result is a list of results from all plugins
    # We want the first non-None result
    for plugin_result in result:
        if plugin_result is not None:
            logger.debug(f"Field '{field_name}' parsed by plugin: {plugin_result}")
            return plugin_result
    
    # No plugin handled this field, return raw value
    return raw_value


def list_registered_plugins() -> list:
    """List all registered plugins.

    Returns:
        A list of registered plugin objects.
    """
    pm = get_plugin_manager()
    return list(pm.get_plugins())
