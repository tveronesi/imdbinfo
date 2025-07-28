from imdbinfo.services import search_title, get_person_detail


# Example 1: Search for a person by name
person_results = search_title("Keanu Reeves")
for person in person_results.names:
    print(f"{person.name} - {person.job} ({person.id})")

# Example 2: Get detailed information about a person by IMDb ID
person = get_person_detail("0000126")
print(f"Name: {person.name}")
print(f"Known For: {', '.join(person.knownfor)}")
print(f"Birth Date: {person.birth_date}")
print(f"Birth Place: {person.birth_place}")
print(f"Death Date: {person.death_date}")
print(f"Death Place: {person.death_place}")
print(f"Bio: {person.bio}")
print(f"Height: {person.height}")
print(f"Primary Profession: {', '.join(person.primary_profession)}")
print(f"Image URL: {person.image_url}")
print(f"IMDb URL: {person.url}")
# Example 3: Print all known professions of the person

