from typing import Optional
import logging
import requests
import json
from lxml import html

from .models import SearchResult, MovieDetail, PersonDetail
from .parsers import parse_json_movie, parse_json_search, parse_json_person_detail

logger = logging.getLogger(__name__)

def get_movie(imdb_id: str)->MovieDetail:
    """Fetch movie details from IMDb using the provided IMDb ID without 'tt' as string, preserve 00
    padding."""
    url = f"https://www.imdb.com/title/tt{imdb_id}/reference"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        raise Exception(f"Error fetching {url}")
    tree = html.fromstring(resp.content)
    script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script:
        raise Exception("No script found with id '__NEXT_DATA__'")
    raw_json = json.loads(script[0])
    return parse_json_movie(raw_json)




def search_title(title: str) ->Optional[SearchResult]:
    """Search for a movie by title and return a list of titles and names."""
    url = f"https://www.imdb.com/find?q={title}&ref_=nv_sr_sm"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        return None
    tree = html.fromstring(resp.content)
    script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script: # throw if no script found
        raise Exception("No script found with id '__NEXT_DATA__'")
    raw_json = json.loads(script[0])

    return parse_json_search(raw_json)



def get_name(person_id: str) -> Optional['PersonDetail']:
    """Fetch person details from IMDb using the provided IMDb ID."""
    #https://www.imdb.com/name/nm0000206/
    url = f"https://www.imdb.com/name/nm{person_id}/"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        raise Exception(f"Error fetching {url}")
    tree = html.fromstring(resp.content)
    script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script:
        raise Exception("No script found with id '__NEXT_DATA__'")
    raw_json = json.loads(script[0])
    return parse_json_person_detail(raw_json)
