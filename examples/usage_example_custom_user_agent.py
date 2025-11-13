"""
Example: Using a custom User-Agent

This example demonstrates how to override the default User-Agent
used for HTTP requests to IMDb.
"""

from imdbinfo import  get_movie
from imdbinfo.services import USER_AGENTS_LIST

# Check the default User-Agent
print(f"Default User-Agent: {USER_AGENTS_LIST}")

# Override with a custom User-Agent
USER_AGENTS_LIST = ["MyCustomApp/1.0 (Contact: myemail@example.com)"]

print(f"Custom User-Agent: {USER_AGENTS_LIST}")

# Now all requests will use the custom User-Agent
try:
    movie = get_movie("tt0133093")  # The Matrix
    print(f"\nFetched movie: {movie.title} ({movie.year})")
    print(f"Rating: {movie.rating}")
except Exception as e:
    print(f"Error: {e}")

# Note: If you get an error, the error message will now include
# more details like HTTP status code and response text
