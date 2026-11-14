from imdbinfo import get_filmography, CreditRole

import logging


logging.basicConfig(level=logging.WARNING)

n = "nm0000055"

filmography_results = get_filmography(n, locale="es", roles=[CreditRole.ACTOR])
if filmography_results:
    for role, films in filmography_results.items():
        print(f"\nRole: {role}")
        for film in films:
            print(f" - {film.title} ({film.year}) [{film.imdbId}]")
            # cover
            print(f"   Cover URL: {film.cover_url}")

filmography_results = get_filmography(n, locale="es", roles=[CreditRole.COMPOSER,'asdfadsf'])
if filmography_results:
    for role, films in filmography_results.items():
        print(f"\nRole: {role}")
        for film in films:
            print(f" - {film.title} ({film.year}) [{film.imdbId}]")
            # cover
            print(f"   Cover URL: {film.cover_url}")

filmography_results = get_filmography(n, locale="es")
if filmography_results:
    for role, films in filmography_results.items():
        print(f"\nRole: {role}")
        for film in films:
            print(f" - {film.title} ({film.year}) [{film.imdbId}]")
            # cover
            print(f"   Cover URL: {film.cover_url}")
