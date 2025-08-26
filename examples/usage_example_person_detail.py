from imdbinfo import search_title, get_name, get_movie

import logging
logging.basicConfig(level=logging.WARNING)

# Example 1: Search for a person by name
person_results = search_title("Mary")
for p in person_results.names:
    print(f"{p.name} - {p.job} ({p.id})")
    person = get_name(p.id)
    if person:
        print(f"Known For: {', '.join(person.knownfor)}")
        print(f"Image URL: {person.image_url}")
        print(f"IMDb URL: {person.url}")
        print(f"Name: {person.name}")
        print(f"Known For: {', '.join(person.knownfor)}")
        print(f"Birth Date: {person.birth_date}")
        print(f"Birth Place: {person.birth_place}")
        print(f"Death Date: {person.death_date}")
        print(f"Death Place: {person.death_place}")
        print(f"Death Reason: {person.death_reason}")
        print(f"Bio: {person.bio[:100]}...")  # Print first 100 characters of bio
        print(f"Height: {person.height}")
        print(f"Primary Profession: {', '.join(person.primary_profession)}")
        print(f"Image URL: {person.image_url}")
        print(f"IMDb URL: {person.url}")

movie = get_movie("0133093")
for p in movie.categories['cast']:
    print(f"{p.name} - {p.job} ({p.id})")
    person = get_name(p.id)
    if person:
        print(f"Known For: {', '.join(person.knownfor)}")
        print(f"Image URL: {person.image_url}")
        print(f"IMDb URL: {person.url}")
        print(f"Name: {person.name}")
        print(f"Known For: {', '.join(person.knownfor)}")
        print(f"Birth Date: {person.birth_date}")
        print(f"Birth Place: {person.birth_place}")
        print(f"Death Date: {person.death_date}")
        print(f"Death Place: {person.death_place}")
        print(f"Death Reason: {person.death_reason}")
        print(f"Bio: {person.bio[:100]}...")  # Print first 100 characters of bio
        print(f"Height: {person.height}")
        print(f"Primary Profession: {', '.join(person.primary_profession)}")
        print(f"Image URL: {person.image_url}")
        print(f"IMDb URL: {person.url}")