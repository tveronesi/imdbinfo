"""Centralized, validated configuration for imdbinfo."""

import json
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import Field, TypeAdapter, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SupportedLocale = Literal["en", "fr-ca", "fr", "hi", "de", "it", "es", "pt", "es-es"]

MAX_ITEMS_DEFAULTS = {
    "max_items_search": 50,
    "max_items_images": 50,
    "max_items_interests": 20,
    "max_items_akas": 200,
    "max_items_trivia": 50,
    "max_items_reviews": 50,
    "max_items_guide_items": 10,
    "max_items_quotes": 100,
    "max_items_credits": 250,
}
_cache_clearers = []
_MAX_ITEMS_TYPE = Annotated[int, Field(gt=0)]
_MAX_ITEMS_ADAPTER = TypeAdapter(_MAX_ITEMS_TYPE)


def register_config_change_callback(callback) -> None:
    """Register a callback to clear caches when the active config changes."""
    _cache_clearers.append(callback)


def validate_locale(locale: str) -> SupportedLocale:
    """Normalize and validate a locale using the configured supported set."""
    normalized = locale.strip().lower() if isinstance(locale, str) else locale
    return TypeAdapter(SupportedLocale).validate_python(normalized)


class Settings(BaseSettings):
    """Runtime settings loaded from environment and overridable in code."""

    model_config = SettingsConfigDict(
        env_prefix="IMDBINFO_",
        env_file=".env",
        extra="ignore",
        validate_assignment=True,
        enable_decoding=False,
    )

    locale: SupportedLocale = "en"
    max_items_search: int = Field(default=50, gt=0)
    max_items_images: int = Field(default=50, gt=0)
    max_items_interests: int = Field(default=20, gt=0)
    max_items_akas: int = Field(default=200, gt=0)
    max_items_trivia: int = Field(default=50, gt=0)
    max_items_reviews: int = Field(default=50, gt=0)
    max_items_guide_items: int = Field(default=10, gt=0)
    max_items_quotes: int = Field(default=100, gt=0)
    max_items_credits: int = Field(default=250, gt=0)
    proxies: dict[str, str] | None = None

    @field_validator("locale", mode="before")
    @classmethod
    def normalize_locale(cls, value):
        if isinstance(value, str):
            value = value.strip().lower()
        return value

    @field_validator("proxies", mode="before")
    @classmethod
    def normalize_proxies(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("{"):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError as exc:
                    raise ValueError("proxies must be a URL or a JSON object") from exc
            else:
                _validate_proxy_url(value)
                return {"http": value, "https": value}
        if not isinstance(value, dict):
            raise ValueError("proxies must be a URL or a mapping of protocols to URLs")
        for protocol, url in value.items():
            if not isinstance(protocol, str) or not isinstance(url, str):
                raise ValueError("proxy protocols and URLs must be strings")
            _validate_proxy_url(url)
        return value

    def __setattr__(self, name, value):
        track_change = name in type(self).model_fields and hasattr(self, name)
        previous = getattr(self, name, None) if track_change else None
        super().__setattr__(name, value)
        if (
            self is globals().get("config")
            and track_change
            and previous != getattr(self, name)
        ):
            for callback in tuple(_cache_clearers):
                callback()


def _validate_proxy_url(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https", "socks4", "socks5"} or not parsed.hostname:
        raise ValueError(f"invalid proxy URL: {url!r}")
    try:
        _ = parsed.port
    except ValueError as exc:
        raise ValueError(f"invalid proxy URL: {url!r}") from exc


def validate_max_items(value: int) -> int:
    """Validate a per-call result limit."""
    return _MAX_ITEMS_ADAPTER.validate_python(value)


config = Settings()
_INITIAL_VALUES = config.model_dump()


def configure(
    *,
    locale: SupportedLocale | None = None,
    max_items_search: int | None = None,
    max_items_images: int | None = None,
    max_items_interests: int | None = None,
    max_items_akas: int | None = None,
    max_items_trivia: int | None = None,
    max_items_reviews: int | None = None,
    max_items_guide_items: int | None = None,
    max_items_quotes: int | None = None,
    max_items_credits: int | None = None,
    proxies: dict[str, str] | str | None = ...,
) -> Settings:
    """Update selected settings and return the shared settings object."""
    updates = {
        "locale": locale,
        "max_items_search": max_items_search,
        "max_items_images": max_items_images,
        "max_items_interests": max_items_interests,
        "max_items_akas": max_items_akas,
        "max_items_trivia": max_items_trivia,
        "max_items_reviews": max_items_reviews,
        "max_items_guide_items": max_items_guide_items,
        "max_items_quotes": max_items_quotes,
        "max_items_credits": max_items_credits,
    }
    if proxies is not ...:
        updates["proxies"] = proxies
    for name, value in updates.items():
        if value is not None:
            setattr(config, name, value)
    if proxies is not ...:
        config.proxies = proxies
    return config


def reset_config() -> Settings:
    """Restore the settings loaded when imdbinfo was imported."""
    for name, value in _INITIAL_VALUES.items():
        setattr(config, name, value)
    return config
