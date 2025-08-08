from imdbinfo import get_movie
from imdbinfo.services import get_episodes

series_ids = [
     'tt1520211',  # The Walking Dead
     'tt0944947',  # Game of Thrones
     'tt0903747',  # Breaking Bad
    'tt1838556',  # a movie ... skip it
     'tt4574334',  # The Mandalorian
     'tt0071007'   # little house on the prairie
]


for series_id in series_ids:
    series = get_movie(series_id)
    if not series.is_series():
        print(f"Series with ID {series_id} not found.")
        continue
    print(f"Movie Title: {series.title} ({series.year}) - {series.imdbId}")
    print(f"Kind: {series.kind}")
    print(f"Series Info: {series.info_series or 'N/A'}")
    print("----------------------------------------------")
    seasons = series.info_series.display_seasons
    seasons.reverse()
    for season_number in seasons:
        season_list = get_episodes(series_id, season_number)
        print(f"\nTotal Episodes in Season {season_number}: {len(season_list)}")
        for episode in season_list.episodes:
            print(f"{episode}")
    print("\n" + "="*50 + "\n")
