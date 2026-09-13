import logging
from imdbinfo import get_awards

logging.basicConfig(level=logging.WARNING)

movies_list = [
    "tt0034583",  # Casablanca (movie)
    "tt0133093",  # The Matrix (movie)
    "tt5716464",  # Breathe (movie)
    "tt1520211",  # The Walking Dead (tvSeries)
    "tt30406366",  # The Walking Dead: Daryl Dixon (tvMiniSeries)
]

for imdb_id in movies_list:
    awards = get_awards(imdb_id)
    print(f"\nAwards for {imdb_id}: {len(awards)} found")
    for award in awards[:5]:
        print(f"  {repr(award)}")
        print(f"    Event: {award.event}")
        print(f"    Status: {award.status}")
        print(f"    Award: {award.award}")
        print(f"    Category: {award.category}")
        if award.nominees:
            print(f"    Nominees: {award.nominees}")
        print(f"    Formatted: {award}")
