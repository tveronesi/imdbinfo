from imdbinfo import get_filmography

import logging

logging.basicConfig(level=logging.WARNING)

n = "nm0123456"

filmography_results = get_filmography(n)
if filmography_results:
    for role, films in filmography_results.items():
        print(f"\nRole: {role}")
        for film in films:
            print(f" - {film.title} ({film.year}) [{film.imdbId}]")
            # cover
            print(f"   Cover URL: {film.cover_url}")
