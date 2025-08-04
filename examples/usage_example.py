from imdbinfo.services import search_title, get_movie

import logging
logging.basicConfig(level=logging.WARNING)

#Example 1: Search for a movie by title
results = search_title("The Matrix")
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")

# Example 2: Get detailed information about a specific movie by IMDb ID
movie = get_movie("0133093")
print(f"Titolo: {movie.title}")
print(f"Title Localized: {movie.title_localized}")
print("title_akas:", " ".join(movie.title_akas))
print(f"Anno: {movie.year}")
print(f"Valutazione: {movie.rating}")
print(f"Generi: {', '.join(movie.genres)}")
print(f"Trama: {movie.plot}")
# certificates
print(f"Certificazioni: {', '.join(movie.certificates)}")

