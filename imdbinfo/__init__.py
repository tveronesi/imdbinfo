import logging

from .services import (
    get_movie,
    search_title,
    get_name,
    get_episodes,
    get_all_episodes,
    get_season_episodes,
    get_akas,
    get_reviews,
    get_trivia,
    get_filmography,
)

__all__ = [
    "get_movie",
    "search_title",
    "get_name",
    "get_episodes",
    "get_all_episodes",
    "get_season_episodes",
    "get_akas",
    "get_reviews",
    "get_trivia",
    "get_filmography",
]

# setup library logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
