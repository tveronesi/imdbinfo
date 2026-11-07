"""Public helpers for reading and updating the shared imdbinfo configuration."""

from typing import Dict, Optional, Union

from .config import MAX_ITEMS_DEFAULTS, Settings, config, configure

MAX_ITEMS_KINDS = tuple(name.removeprefix("max_items_") for name in MAX_ITEMS_DEFAULTS)


def set_locale(locale: str) -> None:
    """Set the default locale used by IMDb requests."""
    configure(locale=locale)


def get_locale() -> str:
    """Get the configured locale, returning an empty string for English."""
    return "" if config.locale == "en" else config.locale


def set_proxy(proxies: Optional[Union[Dict[str, str], str]]) -> None:
    """Set the proxy mapping used by all HTTP transports."""
    configure(proxies=proxies)


def get_proxy() -> Optional[Dict[str, str]]:
    """Return the currently configured proxy mapping."""
    return config.proxies


def set_max_items(
    *,
    search: int | None = None,
    images: int | None = None,
    interests: int | None = None,
    akas: int | None = None,
    trivia: int | None = None,
    reviews: int | None = None,
    guide_items: int | None = None,
    quotes: int | None = None,
    credits: int | None = None,
) -> None:
    """Set one or more result limits by type after validating the full update."""
    requested = {
        kind: value
        for kind, value in {
            "search": search,
            "images": images,
            "interests": interests,
            "akas": akas,
            "trivia": trivia,
            "reviews": reviews,
            "guide_items": guide_items,
            "quotes": quotes,
            "credits": credits,
        }.items()
        if value is not None
    }
    if not requested:
        return

    updates = {f"max_items_{kind}": value for kind, value in requested.items()}
    validated = Settings.model_validate({**config.model_dump(), **updates})
    for name in updates:
        setattr(config, name, getattr(validated, name))


def get_max_items(kind: str | None = None) -> int | dict[str, int]:
    """Get one limit by type, or a mapping containing all configured limits."""
    if kind is not None:
        if kind.startswith("max_items_"):
            kind = kind.removeprefix("max_items_")
        if kind not in MAX_ITEMS_KINDS:
            raise ValueError(
                f"unknown max_items kind {kind!r}; expected one of {MAX_ITEMS_KINDS}"
            )
        return getattr(config, f"max_items_{kind}")
    return {
        name.removeprefix("max_items_"): getattr(config, name)
        for name in MAX_ITEMS_DEFAULTS
    }


__all__ = [
    "get_locale",
    "set_locale",
    "get_proxy",
    "set_proxy",
    "get_max_items",
    "set_max_items",
]
