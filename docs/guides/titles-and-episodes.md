# Titles and episodes

## Retrieve a title

`get_movie` returns detailed data for films, series, and episodes:

```python
from imdbinfo import get_movie

movie = get_movie("tt0133093")
print(movie.title, movie.year)
print(movie.duration)  # minutes
print([director.name for director in movie.directors])
```

`MovieDetail.duration` is measured in minutes. It can be absent when IMDb
does not provide a runtime.

## Work with series and episodes

Check the title kind before reading specialized fields:

```python
series = get_movie("tt1520211")
if series.is_series():
    print(series.info_series.display_seasons)
```

Fetch a single season with `get_season_episodes`:

```python
from imdbinfo import get_season_episodes

season = get_season_episodes("tt1520211", season=1)
for episode in season.episodes:
    print(episode.season, episode.episode, episode.title)
```

Fetch every episode returned by IMDb's bulk endpoint with
`get_all_episodes`:

```python
from imdbinfo import get_all_episodes

episodes = get_all_episodes("tt1520211")
for episode in episodes[:5]:
    print(episode.title, episode.season_number, episode.episode_number)
```

!!! warning
    `BulkedEpisode.duration` is measured in seconds, unlike
    `MovieDetail.duration`, which is in minutes.

`get_episodes` remains available for compatibility, but is deprecated. Use
`get_season_episodes` for one season or `get_all_episodes` for a full series.
