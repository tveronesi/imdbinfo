from imdbinfo.services import search_title, get_movie

import logging
logging.basicConfig(level=logging.WARNING)

#Example 1: Search title/name and print the results
title_query = "little house on the prairie"
results = search_title(title_query)
print(f"Search Results for {title_query} in titles:")
for movie in results.titles:
    print(f"Found a movie: {movie.title} ({movie.year}) - {movie.imdbId} of kind {movie.kind}")
print(f"Search Results for '{title_query}' in names:")
for name in results.names:
    print(f"Name: {name.name} - {name.imdbId}")

print("----------------------------------------------")
print("----------------------------------------------")
print("----------------------------------------------")


# Example 2: Search for a movie by title and get detailed information
movies_list = [
    "tt1520211",  # The Walking Dead (series)
    "tt30406366",  # The Walking Dead: Daryl Dixon (mini-series)
    "tt1589921",  # The Walking Dead S01E01 (episode series)
    "tt0133093"   # The Matrix (movie)

]

for imdb_id in movies_list:
    movie = get_movie(imdb_id)
    if movie.is_series():
        print(f"#########################################################################")
        print(f"##### this is a SERIES: extra info available in movie.info_series  #####")
        print(f"#########################################################################")
        print(f"Series: {movie.info_series or 'N/A'}")
    elif movie.is_episode():
        print(f"##########################################################################")
        print(f"##### this is an EPISODE: extra info available in movie.info_episode #####")
        print(f"##########################################################################")
        print(f"Episode: {movie.info_episode or 'N/A'}")
    else:
        print(f"##########################################################################")
        print(f"##################################### MOVIE ##############################")
        print(f"##########################################################################")
    print(f"Movie Title: {movie.title} ({movie.year}) - {movie.imdbId}")
    print(f"Kind: {movie.kind}")
    print(f"URL: {movie.url}")
    print(f"Rating: {movie.rating or 'N/A'}")
    print(f"Genres: {', '.join(movie.genres) if movie.genres else 'N/A'}")
    print(f"Languages: {', '.join(movie.languages) if movie.languages else 'N/A'}")
    print(f"Country Codes: {', '.join(movie.country_codes) if movie.country_codes else 'N/A'}")
    print("Directors:")
    for director in movie.directors:
        print(f"  - {director.name} ({director.imdbId})")
    print("Cast:")
    for cast_member in movie.categories['cast'][:3]:  # Limit to the first 3 cast members for brevity
        print(f"  - {cast_member.name} ({cast_member.imdbId})")
    print("----------------------------------------------")
