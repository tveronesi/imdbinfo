from imdbinfo import get_movie
from imdbinfo.services import get_episodes

series_mail_tile =  get_movie('tt0944947')
print(f"Movie Title: {series_mail_tile.title} ({series_mail_tile.year}) - {series_mail_tile.imdbId}")
print(f"Kind: {series_mail_tile.kind}")
print(f"Serires Info: {series_mail_tile.info_series or 'N/A'}")

episodes = get_episodes(series_mail_tile.imdb_id, 1 )  # Fetch episodes for season 1
print(f"Total Episodes in Season 1: {len(episodes)}")
