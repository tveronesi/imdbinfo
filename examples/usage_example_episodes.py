from imdbinfo import get_movie
from imdbinfo.services import get_episodes

series_main_tile =  get_movie('tt1520211')
print(f"Movie Title: {series_main_tile.title} ({series_main_tile.year}) - {series_main_tile.imdbId}")
print(f"Kind: {series_main_tile.kind}")
print(f"Serires Info: {series_main_tile.info_series or 'N/A'}")

episodes = get_episodes(series_main_tile.imdb_id, 1)  # Fetch episodes for season 1
print(f"Total Episodes in Season 1: {len(episodes)}")
