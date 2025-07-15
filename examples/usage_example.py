from imdbinfo.services import search_title, get_movie

# Esempio 1: Ricerca di un film per titolo
results = search_title("The Matrix")
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")

# Esempio 2: Ottenere dettagli di un film tramite IMDb ID
movie = get_movie("0133093")
print(f"Titolo: {movie.title}")
print(f"Anno: {movie.year}")
print(f"Valutazione: {movie.rating}")
print(f"Generi: {', '.join(movie.genres)}")
print(f"Trama: {movie.plot}")

