import logging
from imdbinfo import search_title, get_movie
from imdbinfo.locale import set_locale

set_locale('es')
logging.basicConfig(level=logging.WARNING)
list_q = "nobody was safe, and the confidants of queens".split(" ")

for word in list_q:
    print(f"Searching for movies with title containing: {word}")
    results = search_title(word)
    if results:
        print(f"Search Results for '{word}' in titles:")
        print(f"Total movies found: {len(results.titles)}")
        for movie in results.titles:
            print(f"Movie title from search   : {movie.title}")
            print(f"Movie title from search (localized)   : {movie.title_localized}")
            movie = get_movie(movie.imdb_id)
            print(f"Movie title from get_movie: {movie.title}")
            print(f"movie title from get_movie (localized): {movie.title_localized}")
            print(f"Movie plot: {movie.plot}")
            print("Genres:"+ ",".join(movie.genres))
            print("Interests:"+ ",".join(movie.interests))
            print("Storyline keywords:" +",".join(movie.storyline_keywords))
            print("----------------------------------------------")




