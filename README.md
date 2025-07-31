[![Build Status](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/tveronesi/imdbinfo/actions/workflows/pypi-publish.yml)
[![PyPI Version](https://img.shields.io/pypi/v/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
[![Python Versions](https://img.shields.io/pypi/pyversions/imdbinfo?style=flat-square)](https://pypi.org/project/imdbinfo/)
![PyPI - Daily Downloads](https://img.shields.io/pypi/dm/your-package-name?label=PyPI%20downloads&logo=pypi)

<p align="center">
  <img src="https://img.shields.io/badge/IMDb-INFO-yellow?style=for-the-badge&logo=imdb&logoColor=black" alt="IMDb Info"/>
</p>

# imdbinfo

**Your personal gateway to IMDb data**. Search for movies and people and get structured information in seconds.

## Features

- 🔍 **Search movies and people** by name or title
- 🎬 **Detailed movie info** including cast, crew, ratings and more
- 👥 **Detailed person info** with biography, filmography and images
- 📝 **Typed Pydantic models** for predictable responses
- ✅ **No API keys required**

## Installation

```bash
pip install imdbinfo
```

## Quick Start

```python
from imdbinfo.services import search_title, get_movie, get_name

# Search for a title
results = search_title("The Matrix")
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")

# Get movie details
movie = get_movie("0133093")
print(movie.title, movie.year, movie.rating)

# Get person details
person = get_name("nm0000206")
print(person.name, person.birth_date)
```

For more examples see the [examples](examples/) folder.

## Why choose imdbinfo?

- Easy to use Python API
- Returns clean structured data
- Powered by requests and lxml
- Uses Pydantic for type safety
- No external dependencies or API keys required
- Ideal for quick scripts and data analysis

## License

imdbinfo is released under the MIT License.
See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Open an issue or pull request on GitHub.

If you find this project useful, please consider giving it a ⭐ on GitHub!

Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.