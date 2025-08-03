# 🎬 imdbinfo – A Simple Python Tool to Fetch IMDb Movie & Actor Data (No API Keys Needed)

Have you ever needed to grab movie or actor details from IMDb, but didn’t want to deal with complicated APIs or authentication keys?

That’s exactly why I built [`imdbinfo`](https://github.com/tveronesi/imdbinfo) — a lightweight, easy-to-use Python package to search and fetch structured IMDb data, **with no API keys required**.

---

## 🚀 What is imdbinfo?

**imdbinfo** is your personal gateway to IMDb data. It lets you:

- 🔍 Search for movies and people by name/title  
- 🎬 Retrieve detailed movie info (year, rating, cast, etc.)  
- 👥 Get full person info like biography, birth date, and filmography  
- 🧩 Work with structured Pydantic models for predictable parsing  

No scraping mess. No API credentials. Just clean, simple data for your projects.

---

## 📦 Installation

```bash
pip install imdbinfo
```

That’s all you need.

---

## ⚙️ Quick Start

Here's how you can use it in a Python script:

```python
from imdbinfo.services import search_title, get_movie, get_name

# 🔍 Search for a title
results = search_title("The Matrix")
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")

# 🎬 Get movie details
movie = get_movie("0133093")  # or 'tt0133093'
print(movie.title, movie.year, movie.rating)

# 👤 Get person details
person = get_name("nm0000206")  # or '0000206'
print(person.name, person.birth_date)
```

More usage examples can be found in the [examples folder](https://github.com/tveronesi/imdbinfo/tree/main/examples).

---

## 🤔 Why Choose imdbinfo?

- ✅ No API keys or auth needed  
- ⚡ Blazing fast with `requests` + `lxml`  
- 🎯 Cleanly typed with [Pydantic](https://docs.pydantic.dev)  
- 🧪 Great for automation, data science, or bots  
- 🪶 Lightweight and dependency-minimal  

Whether you're building a movie catalog, a Telegram bot, or just scraping your favorite actors' filmographies — `imdbinfo` is built to be intuitive and developer-friendly.

---

## 🛠 Under the Hood

- Built using `requests` and `lxml` for fast scraping  
- Uses [Pydantic](https://docs.pydantic.dev) for typing and validation  
- No tracking, no telemetry, no nonsense  

---

## 💬 Feedback Welcome

I’m actively maintaining the project and open to improvements. Want to add support for series or images? Spot a bug? Just open a PR or issue.

⭐ If you like it, drop a star on [GitHub](https://github.com/tveronesi/imdbinfo) — it helps!

---

## 🔗 Resources

- GitHub: [tveronesi/imdbinfo](https://github.com/tveronesi/imdbinfo)  
- PyPI: [`imdbinfo`](https://pypi.org/project/imdbinfo/)  
- License: MIT  
- Contributions: Welcome!
