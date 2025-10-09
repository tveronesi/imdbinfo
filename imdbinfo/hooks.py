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

"""Hook specifications for imdbinfo plugins."""

import pluggy
from typing import Any, Optional

hookspec = pluggy.HookspecMarker("imdbinfo")


class FieldParserHookSpec:
    """Hook specification for field parser plugins."""

    @hookspec
    def parse_field(self, field_name: str, raw_value: Any, raw_json: dict) -> Optional[Any]:
        """Parse a specific field from raw JSON data.

        This hook allows plugins to customize parsing for specific fields
        in the movie/person data models.

        Args:
            field_name: The name of the field being parsed (e.g., "title", "rating", "directors")
            raw_value: The raw value extracted from the JSON (could be result of jmespath query)
            raw_json: The complete raw JSON data for additional context

        Returns:
            The parsed value for this field, or None if this plugin doesn't handle this field.
            If multiple plugins return non-None values, the first one wins.

        Example:
            >>> def parse_field(field_name, raw_value, raw_json):
            ...     if field_name == "title":
            ...         # Custom title parsing
            ...         return raw_value.upper() if raw_value else None
            ...     return None
        """
