"""
Example demonstrating SSL verification configuration in imdbinfo.

This example shows how to handle SSL certificate verification errors
that may occur in certain environments when using imdbinfo.
"""

import imdbinfo

# Example 1: Basic usage with default SSL verification (enabled)
print("Example 1: Default usage with SSL verification enabled")
try:
    movie = imdbinfo.get_movie("0133093")  # The Matrix
    print(f"✓ Successfully fetched: {movie.title}")
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nIf you see an SSL/TLS error, see Example 2 below.")

print("\n" + "="*60 + "\n")

# Example 2: Disabling SSL verification when needed
print("Example 2: Disabling SSL verification for troubleshooting")
print("⚠️  Warning: Only disable SSL verification in trusted environments!")

# Disable SSL verification
imdbinfo.set_ssl_verify(False)
print(f"SSL verification is now: {'enabled' if imdbinfo.get_ssl_verify() else 'disabled'}")

try:
    movie = imdbinfo.get_movie("0133093")  # The Matrix
    print(f"✓ Successfully fetched: {movie.title}")
except Exception as e:
    print(f"✗ Error: {e}")

# Re-enable SSL verification (best practice)
imdbinfo.set_ssl_verify(True)
print(f"SSL verification is now: {'enabled' if imdbinfo.get_ssl_verify() else 'disabled'}")

print("\n" + "="*60 + "\n")

# Example 3: Checking SSL verification status
print("Example 3: Checking SSL verification status")
status = "enabled" if imdbinfo.get_ssl_verify() else "disabled"
print(f"Current SSL verification status: {status}")

print("\n" + "="*60 + "\n")

# Example 4: Using environment variable (run script with IMDBINFO_VERIFY_SSL=false)
print("Example 4: Using environment variable")
print("To disable SSL verification via environment variable, run:")
print("  export IMDBINFO_VERIFY_SSL=false  # Linux/Mac")
print("  set IMDBINFO_VERIFY_SSL=false     # Windows")
print("\nThen run your Python script normally.")
