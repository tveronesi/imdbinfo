from imdbinfo import get_movie, get_all_episodes

series_ids = [
    'tt1520211',  # The Walking Dead
    'tt0944947',  # Game of Thrones
    'tt0903747',  # Breaking Bad
    'tt1838556',  # a movie ... skip it
    'tt4574334',  # The Mandalorian
    'tt0071007',  # little house on the prairie
    'tt35373097'  # seires with no episodes
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

    all_episodes = get_all_episodes(series_id)
    print(f"\nTotal Episodes in Series: {len(all_episodes)}")
    for episode in all_episodes:
        print(f"{episode}")
    print("\n" + "=" * 50 + "\n")
