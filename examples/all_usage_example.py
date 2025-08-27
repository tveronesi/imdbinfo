from time import time
from imdbinfo import search_title, get_movie, get_name

import logging
logging.basicConfig(level=logging.WARNING)
# list_q = "little house|matrix|walking dead|horizon".split("|")
list_q = "France to find his estate confiscated by governor Narbonne, for back taxes, and resold to Katrina, a Dutch Countess. Katrina offers to return Pierre's property if he will help her get possession".split(" ")
#Example 1: Search for a movie by title

for word in list_q:
    print(f"Searching for movies with title containing: {word}")
    results = search_title(word)
    if results:
        for movie in results.titles:
            print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")
            movie = get_movie(movie.imdb_id)
            print(f"  URL: {movie.url}")
            print(f"  Rating: {movie.rating}")
            print(f"  MPAA: {movie.mpaa}")
            print(f"  Countries: {', '.join(movie.countries) if movie.countries else 'N/A'}")
            print(f"  Languages codes: {', '.join(movie.languages) if movie.languages else 'N/A'}")
            print(f"  Languages: {', '.join(movie.languages_text) if movie.languages_text else 'N/A'}")

            print(f"  Kind: {movie.kind}")
            if movie.is_series():
                print(f"  Series Info: {movie.info_series or 'N/A'}")
            if movie.is_episode():
                print(f"  Episode Info: {movie.info_episode or 'N/A'}")
            for director in movie.directors:
                print(f"  Director: {director.name}")
            for c in movie.categories['cast'][:1]:  # Limit to first 3 cast members for brevity
                #print(c)
                t0 = time()
                person = get_name(c.imdb_id)
                t1 = time()
                print(f"  Cast: \n\t{person.name} ({', '.join(c.characters)}) - {' ° '.join(person.primary_profession[:2])} - {person.url} ")
            # DONE
            print("----------------------------------------------")




