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
