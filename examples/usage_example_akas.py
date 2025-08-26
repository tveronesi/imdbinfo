from imdbinfo import get_akas

import logging
logging.basicConfig(level=logging.WARNING)


movies_list = [
    "tt0133093",   # The Matrix (movie)
    "tt1520211",  # The Walking Dead (tvSeries)
    "tt30406366",  # The Walking Dead: Daryl Dixon (tvMiniSeries)
    "tt1589921",  # The Walking Dead S01E01 (tvEpisode series)
    "tt12326830", #  'The Sandman' (podcastSeries)
    "tt15110916", # 'The Sandman' (2022)  s01e01 (podcastEpisode)
    "tt2080323", # Hotel Desire (short)
    "tt36048590", # Marc Maron: Panicked (tvSpecial)
    "tt6582384" , # Red Nose Day Actually (tvShort)
    "tt33238076", # Mafia: The Old Country (videoGame)
    "tt11771594", # American Pie Presents: Girls' Rules (video)
    "tt37195825" , # Talking Heads: Psycho Killer (musicVideo)
    "tt33501878", #title akas
]

for imdb_id in movies_list:
    movie_akas = get_akas(imdb_id)
    print(f"##########################################################################")
    print(movie_akas['akas'])
