from imdbinfo.services import search_title, get_movie

list_q = "France to find his estate confiscated by governor Narbonne, for back taxes, and resold to Katrina, a Dutch Countess. Katrina offers to return Pierre's property if he will help her get possession".split(" ")
#Example 1: Search for a movie by title

for word in list_q:
    print(f"Searching for movies with title containing: {word}")
    results = search_title(word)
    if results:
        for movie in results.titles:
            print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")
            movie = get_movie(movie.imdb_id)
            print(f"  Valutazione: {movie.rating}")
            # DONE
            print("----------------------------------------------")

# Example 2: Get detailed information about a specific movie by IMDb ID



