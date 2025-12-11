from imdbinfo import get_movie, get_all_interests
import logging


logging.basicConfig(level=logging.WARNING)

# List of movie IMDb IDs with comments for maintainability
MOVIE_IDS = [
    "tt1490017",   # Frozen (2013)
    "tt0133093",   # The Matrix (1999)
    "tt2347569",   # Pacific Rim (2013)
    "tt31184028",  # Dune: Part Two (2024)
    "tt1745960",  # Top Gun: Maverick (2022)
]

for imdb_id in MOVIE_IDS:
    movie_details = get_movie(imdb_id)
    print(f"#{movie_details.title} ({movie_details.year})")
    interests = get_all_interests(imdb_id)
    print("Genres:", movie_details.genres)
    print(f"Interests : {interests}")
    print("-----------------------")