# Changelog

## v0.1.0
- Fix bug in something
- Improve documentation

## v0.1.1
- Initial release

## v0.2.5
- Add new feature to fetch movie ratings
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