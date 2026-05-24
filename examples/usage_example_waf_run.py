#!/usr/bin/env python
"""Debug script to test WAF solver and see actual errors."""

import sys
import logging
import traceback

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(message)s")

# Patch the request_handler to show WAF solver errors
import imdbinfo.services as services
from imdbinfo_aws.aws import AwsSolver

original_get_cookies = services.get_cookies


def patched_get_cookies(text, user_agent, force=False):
    """Patched version that shows full error details."""
    try:
        print("\n" + "=" * 80)
        print("DEBUG: WAF solver starting...")
        print("=" * 80)
        print(f"Response HTML length: {len(text)}")
        print(f"First 500 chars:\n{text[:500]}")
        print("=" * 80)

        solver = AwsSolver(user_agent=user_agent, domain="www.imdb.com")

        # Try extract first
        print("\nDEBUG: Attempting to extract goku and host...")
        try:
            goku, host = solver.extract(text)
            print(
                f"SUCCESS: Extracted goku (keys: {list(goku.keys()) if isinstance(goku, dict) else 'not a dict'}) and host: {host}"
            )
        except Exception as e:
            print(f"ERROR in extract(): {e}")
            traceback.print_exc()
            raise

        # Try get final values
        print(f"\nDEBUG: Attempting to get final values from {host}...")
        try:
            values = solver._get_final_values(host)
            print(f"SUCCESS: Got final values: {values}")
        except Exception as e:
            print(f"ERROR in _get_final_values(): {e}")
            traceback.print_exc()
            raise

        # Try build payload
        print("\nDEBUG: Attempting to build payload...")
        try:
            payload = solver._build_payload(values, goku)
            print(f"SUCCESS: Built payload (keys: {list(payload.keys())})")
        except Exception as e:
            print(f"ERROR in _build_payload(): {e}")
            traceback.print_exc()
            raise

        # Try post payload
        print(f"\nDEBUG: Attempting to post payload to {host}...")
        try:
            temp = solver.post_payload(payload, host)
            print(f"SUCCESS: Got response: {temp}")
            return {"aws-waf-token": temp["token"]}
        except Exception as e:
            print(f"ERROR in post_payload(): {e}")
            traceback.print_exc()
            raise

    except Exception as e:
        print(f"\nERROR: WAF solver failed: {e}")
        traceback.print_exc()
        raise


# Monkey-patch
services.get_cookies = patched_get_cookies

# Now try to fetch a movie
from imdbinfo import get_movie

print("\nAttempting to fetch movie tt2112570...")
try:
    movie = get_movie("tt2112570")
    print(f"SUCCESS: {movie.title}")
except Exception as e:
    print(f"FINAL ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
