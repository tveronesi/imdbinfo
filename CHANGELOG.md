# Changelog

## v0.1.0
- Fix bug in something
- Improve documentation

## v0.1.1
- Initial release

## v0.2.5
- Add new feature to fetch movie ratings
- Fix bug in movie search functionality
- Fix bug in movie search functionality
- Update dependencies to latest versions
- Improve error handling for network requests
- Add support for fetching movie reviews

## v0.2.8
- Fix bug in movie rating fetching
- Updated README with json response example

## v0.3.0
- Add support for movie categories in `MovieDetail.categories`
- Added `MovieDetail.stars` to get the main cast of the movie, and deprecating `MovieDetail.cast` later
- FIX: directorsPageTitle out of range
- Updated README with new features and deprecations notice

## v0.3.1
- Fix release date formatting to handle missing values gracefully
- Update models.py to clarify year attribute handling for series
- Refactor parsers.py to simplify data extraction and improve readability

## v0.3.2
- Using jmespath to parse json response 
- removing MovieDetail.cast now using MovieDetail.stars instead
- MovieDetail.directors, kept for backward compatibility 
- MovieDetail.categories['directors'] as List[Person] for directors with additional information
- MovieDetail.categories['cast'] for characters as List[CastMember] adding information about characters image, url and Role
- Some fixes in parsers and models to improve type hints and code clarity

## v0.3.3
- New get_name function to fetch person details by IMDb ID.
- Fixed some bugs pointed out in issues.

## v0.3.4
- Added new test cases to increase coverage
- Improved example scripts for better usability
- Updated logging levels for enhanced traceability
- Improved string representation of models (__str__ and __repr__)
- Various code fixes and optimizations for quality and functionality

## v0.3.5
- Added support for localized titles (`title_localized`) and alternate titles (`title_akas`) in the `MovieDetail` model and parsing logic.
- Improved the `CastMember` model with new attributes, including additional cast details (`attributes`).
- Enhanced certificate parsing to handle region-specific ratings and consolidate them into a structured format.
- Overhauled documentation in `docs/index.md` with detailed instructions, usage examples, and project highlights.
- Updated the PyPI downloads badge in `README.md` using `pepy.tech`.
- Enhanced the test suite for `parse_json_movie` to validate the new certificate parsing and compatibility with updated models.
- Added the `jekyll-theme-cayman` theme for documentation in `docs/_config.yml`.
- Updated `pyproject.toml` with the package homepage URL.
- Added a step in the GitHub Actions workflow (`pypi-publish.yml`) to install dependencies before running tests.

## v0.4.0
- Added `SeriesMixin` with `is_series()` and `is_episode()` methods to `MovieDetail` and `MovieInfo` for movie kind checking.
- Introduced `SeriesInfo` and `EpisodeInfo` models for structured series and episode metadata.
- Added new `EpisodeData` and `EpisodesList` models to represent episodes and collections of episodes.
- Expanded the README and main documentation to highlight support for series, miniseries, and episodes, with new sections and code examples.
- Updated and added example scripts (`usage_example.py`, `usage_example_episodes.py`, `all_usage_example.py`) to demonstrate searching, fetching, and displaying information for movies, series, and episodes.
- Enhanced feature lists in documentation to enumerate new capabilities such as series and episode support, release dates, and international titles.
- Added user guidance for the new features and pointers to related projects for REST API access.

## v0.4.1
- Added service `get_all_episodes` to fetch all episodes of a series, all in a row no season, no episode number. Sorted by release_date.
- Updated README with example for fetching all episodes.
- Added example script `usage_example_all_episodes.py` to demonstrate fetching all episodes of a series.

## v0.4.2
- HOT FIX Refactor _release_date function to improve handling of None values

## v0.4.3
- no functional changes: code clean, refactor clas names for clarity and consistency
- Refactor movie-related models: `SeriesInfo` -> `InfoSeries`, `EpisodeInfo` `InfoEpisode`. added specialized classes for `TvSeriesDetail` / `TvEpisodeDetail` extending `MovieDetail`
- Deprecate `get_episodes` function and add warning log for alternative usage
- Update movie kind identifiers in usage_example.py and models.py for better clarity and consistency, now handling all: tvMovie, short, movie, tvEpisode, tvMiniseries, tvSpecial, tvShort, videoGame, video, musicVideo, podcastEpisode, podcastSeries

## v0.4.4   
- add `get_akas(imdb_id: str) -> List[AkaInfo]` function to fetch alternate titles and AkaInfo model to represent them
- add caching to services using `functools.lru_cache` for improved performance on repeated requests
- add `SeasonEpisodesList.series_imdbId`and `SeasonEpisodesList.season_number` to identify the imdbId of the serie and the season number
- updated DISCLAIMER.txt
- add services to `__init__.py` for immediate access

## v0.5.0
- add locale support to services: `search_movie`, `get_movie`, `get_episodes`, `get_all_episodes`, `get_name`, `get_akas` 

## v0.5.1
- fix locale handling in services, errors in `'en'` when no locale provided

## v0.5.2
- **Company Credits Extraction:** Added support for extracting detailed company credits (distribution, production, sales, special effects, miscellaneous) from IMDb. This includes a new `CompanyInfo` model and updates to the `MovieDetail` model and parser logic to populate `company_credits`
- **Additional Movie Metadata:** The `MovieDetail` model and parser now include fields for `mpaa` rating, `countries`, and `languages_text`, allowing for richer movie information.
- **HTTP Library Migration:** Replaced all usages of `requests` with `niquests` for making HTTP requests, including updates in the `Dockerfile`, `services.py`, and documentation.
- **Locale Handling:** Improved locale management by changing `supported_locales` to a tuple and introducing a normalization function for IMDb IDs.
- **README and Examples:** Updated the `README.md` and example scripts to showcase new features, including company credits extraction and additional metadata fields. Also clarified usage of `niquests` and improved code samples.

## v0.5.3
- **Movie Reviews Extraction:** Added new `get_reviews` function to fetch user reviews for any IMDb title, including review text, ratings, author information, and helpfulness votes
- **Trivia Information Access:** Added new `get_trivia` function to retrieve interesting trivia facts about movies and TV shows, complete with interest scores from the community

## v0.5.4
- **Bug Fixes and Improvements:** Fixed bug in get_movies for movies without country pr languages