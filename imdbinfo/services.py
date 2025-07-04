# python
import requests
import json
from lxml import html

from .parsers import parse_json_movie, parse_json_search


def get_movie(imdb_id: str):
    """Fetch movie details from IMDb using the provided IMDb ID without 'tt' ."""
    url = f"https://www.imdb.com/title/tt{imdb_id}/reference"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        return None
    tree = html.fromstring(resp.content)
    script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script:
        return None
    raw_json = json.loads(script[0])
    return parse_json_movie(raw_json)





def search_title(title: str):
    url = f"https://www.imdb.com/find?q={title}&ref_=nv_sr_sm"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        return None
    tree = html.fromstring(resp.content)
    script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script:
        return None
    raw_json = json.loads(script[0])

    return parse_json_search(raw_json)