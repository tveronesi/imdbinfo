import json

from imdbinfo.services import search_title, get_movie

#Example 1: Search for a movie by title
results = search_title("The Matrix")
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")

# Example 2: Get detailed information about a specific movie by IMDb ID
movie = get_movie("0133093")
print(f"Titolo: {movie.title}")
print(f"Anno: {movie.year}")
print(f"Valutazione: {movie.rating}")
print(f"Generi: {', '.join(movie.genres)}")
print(f"Trama: {movie.plot}")

print(json.dumps(movie.model_dump()))
