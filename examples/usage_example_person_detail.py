from imdbinfo.services import search_title, get_person_detail


# Example 1: Search for a person by name
person_results = search_title("Keanu Reeves")
for person in person_results.names:
    print(f"{person.name} - {person.job} ({person.id})")

# Example 2: Get detailed information about a person by IMDb ID
person = get_person_detail("0000206")  # Keanu Reeves' IMDb ID
print(f"Nome: {person.name}")
print(f"ID: {person.id}")
print(f"URL: {person.url}")

