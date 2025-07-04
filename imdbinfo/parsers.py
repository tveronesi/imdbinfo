from typing import Optional

from .models import MovieDetail, Person, MovieInfo, SearchResult


def parse_json_movie(raw_json) -> Optional[MovieDetail]:
    data = {}
    mainColumnData = raw_json['props']['pageProps']['mainColumnData']
    aboveTheFoldData = raw_json['props']['pageProps']['aboveTheFoldData']
    if not mainColumnData:
        return None

    data['imdbId'] = mainColumnData['id']
    data['imdb_id'] = data['imdbId'].replace('tt', '') # movie id without 'tt'
    data['url'] = f"https://www.imdb.com/title/{data['imdbId']}/"
    data['title'] = aboveTheFoldData['originalTitleText']['text']
    data['kind'] = mainColumnData['titleType']['id']
    data['metacritic_rating'] = mainColumnData['metacritic']['metascore']['score'] if mainColumnData[
        'metacritic'] else None
    data['cover_url'] = aboveTheFoldData['primaryImage']['url']
    data['plot'] = mainColumnData['plot']['plotText']['plainText'] if mainColumnData['plot'] else None
    release_date = mainColumnData['releaseDate']
    data['year'] = aboveTheFoldData['releaseYear']['year']
    data['duration'] = aboveTheFoldData['runtime']['seconds'] / 60 if aboveTheFoldData['runtime'] else None
    data['rating'] = mainColumnData['ratingsSummary']['aggregateRating']
    data['votes'] = mainColumnData['ratingsSummary']['voteCount']
    data['genres'] = [genre['genre']['text'] for genre in mainColumnData['titleGenres']['genres']]
    data[
        'worldwide_gross'] = f"{mainColumnData['worldwideGross']['total']['amount']} {mainColumnData['worldwideGross']['total']['currency']}" if \
        mainColumnData['worldwideGross'] else None
    data[
        'production_budget'] = f"{mainColumnData['productionBudget']['budget']['amount']} {mainColumnData['productionBudget']['budget']['currency']}" if \
        mainColumnData['productionBudget'] else None

    trailers = mainColumnData['primaryVideos']['edges']
    data['trailers'] = [
        f"https://www.imdb.com/video/{trailer['node']['id']}" for trailer in trailers if trailer['node']['id']
    ]

    interests = mainColumnData['interests']['edges']
    data['interests'] = [interest['node']['primaryText']['text'] for interest in interests]

    data[
        'release_date'] = f"{release_date['year']}-{release_date['month']:02d}-{release_date['day']:02d}" if release_date else None

    certificates = mainColumnData['certificates']['edges']
    data['certificates'] = {
        cert['node']['country']['id']: (cert['node']['country']['text'], cert['node']['rating'])
        for cert in certificates if cert['node']['country']
    }

    directors_dump = mainColumnData['directorsPageTitle'][0]['credits']
    data['directors'] = []
    for director in directors_dump:
        d = Person.from_directors(director)
        data['directors'].append(d)

    cast_dump = aboveTheFoldData['castPageTitle']['edges']
    data['cast'] = []
    for cast_member in cast_dump:
        c = Person.from_cast(cast_member)
        data['cast'].append(c)

    filming_locations_dump = mainColumnData['filmingLocations']['edges']
    data['filming_locations'] = [location['node']['text'] for location in filming_locations_dump]

    country_codes_dump = mainColumnData['countriesDetails']['countries']
    data['country_codes'] = [country['id'] for country in country_codes_dump]

    storyline_keywords_dump = mainColumnData['storylineKeywords']['edges']
    data['storyline_keywords'] = [keyword['node']['text'] for keyword in storyline_keywords_dump]

    production_dump = mainColumnData['production']['edges']
    data['production'] = [prod['node']['company']['companyText']['text'] for prod in production_dump]

    summaries_dump = mainColumnData['summaries']['edges']
    data['summaries'] = [summary['node']['plotText']['plaidHtml'] for summary in summaries_dump]

    synopses_dump = mainColumnData['synopses']['edges']
    data['synopses'] = [synopsis['node']['plotText']['plaidHtml'] for synopsis in synopses_dump]

    sound_mixed_dump = mainColumnData['technicalSpecifications']['soundMixes']['items']
    data['sound_mixes'] = [sound['text'] for sound in sound_mixed_dump]

    processes_dump = mainColumnData['technicalSpecifications']['processes']['items']
    data['processes'] = [process['process'] for process in processes_dump]

    printed_formats_dump = mainColumnData['technicalSpecifications']['printedFormats']['items']
    data['printed_formats'] = [format['printedFormat'] for format in printed_formats_dump]

    negative_formats_dump = mainColumnData['technicalSpecifications']['negativeFormats']['items']
    data['negative_formats'] = [format['negativeFormat'] for format in negative_formats_dump]

    laboratories_dump = mainColumnData['technicalSpecifications']['laboratories']['items']
    data['laboratories'] = [lab['laboratory'] for lab in laboratories_dump]

    colorations_dump = mainColumnData['technicalSpecifications']['colorations']['items']
    data['colorations'] = [color['text'] for color in colorations_dump]

    cameras_dump = mainColumnData['technicalSpecifications']['cameras']['items']
    data['cameras'] = [camera['camera'] for camera in cameras_dump]

    aspect_ratios_dump = mainColumnData['technicalSpecifications']['aspectRatios']['items']
    data['aspect_ratios'] = [(ratio['aspectRatio'], (' '.join([atrb['text'] for atrb in ratio['attributes']]))) for
                             ratio in aspect_ratios_dump]

    languages_dump = mainColumnData['spokenLanguages']['spokenLanguages']
    data['languages'] = [lang['id'] for lang in languages_dump]

    movie = MovieDetail.model_validate(data)

    return movie


def parse_json_search(raw_json) ->SearchResult:
    title =[]
    for title_data in raw_json['props']['pageProps']['titleResults']['results']:
        title.append(MovieInfo.from_movie_info(title_data))
    people = []
    for person_data in raw_json['props']['pageProps']['nameResults']['results']:
        people.append(Person.from_search(person_data))

    res = SearchResult(titles=title, people=people)
    return res