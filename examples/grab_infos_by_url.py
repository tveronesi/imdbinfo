import requests
import json
from lxml import html
import re

IMDB_URL = "https://www.imdb.com/title/tt0133093/soundtrack"

def url_to_filename(url):
    # Remove the full 'https://www.imdb.com/' prefix
    url = re.sub(r'^https?://www\.imdb\.com/', '', url)
    # Remove query params and fragments
    url = re.sub(r'[\?#].*$', '', url)
    # Replace / with _
    url = url.replace('/', '_')
    return url + ".json"

def fetch_and_save_json(url):
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    tree = html.fromstring(resp.content)
    script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script:
        raise Exception("No script found with id '__NEXT_DATA__'")
    raw_json = json.loads(script[0])
    filename = url_to_filename(url)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(raw_json, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON to {filename}")

if __name__ == "__main__":
    fetch_and_save_json(IMDB_URL)