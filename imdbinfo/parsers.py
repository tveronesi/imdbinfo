from typing import Optional
import logging

import jmespath

from .models import MovieDetail, Person, MovieInfo, SearchResult, CastMember, PersonDetail

VIDEO_URL = "https://www.imdb.com/video/"
TITLE_URL = "https://www.imdb.com/title/"

logger = logging.getLogger(__name__)

def pjmespatch(query, data, post_process=None, *args, **kwargs):
    result = jmespath.search(query, data)
    if post_process :
        return post_process(result, *args, **kwargs)
    return result

def _none_to_string_in_list(result):
    """
     given a list of lists , if a None is found replace with '' recursively
    """
    return [[str(item) if item is not None else '' for item in sublist] for sublist in result]

def _to_directors(result):
    if result is None:
        return []
    return [Person.from_directors(a) for a in result if a.get('name') and a.get('name').get('id')]

def _join(result, separator=' '):
    if result is None:
        return None
    return separator.join(map(str, result)) if isinstance(result, list) else str(result)

def _certificates_to_dict(result):
    """
    given a list of lists, convert it to a dict with country id as key and (country text, rating) as value
    """
    return {item[0]: (item[1], item[2]) for item in result if item[0] and item[1] and item[2]}

def _feed_credits(result) -> dict:
    """feed credits from the page 'name' to the PersonDetail model"""

    res = {}
    for itemCast in result:
        # ['writer', 'tt27665778', 'Horizon: An American Saga - Chapter 2', 'Movie', 'https://m.media-amazon.com/images/M/MV5BMDg1OWI3NTYtY2IwMy00NmQ4LTk5YWUtZmViNmU5YTFkNGU5XkEyXkFqcGc@._V1_.jpg', 2024, None]
        category = itemCast[0]
        imdbId = itemCast[1]
        titleOriginal = itemCast[2]
        type = itemCast[3]
        imageUrl = itemCast[4]
        year = itemCast[5]
        genres = ','.join(itemCast[6] or [])

        res.setdefault(category, [])
        res[category].append(
            MovieInfo(
                id=imdbId.replace('tt', ''),
                imdbId=imdbId,
                imdb_id=imdbId.replace('tt', ''),
                title=titleOriginal,
                kind=type,
                cover_url=imageUrl,
                url=f"{TITLE_URL}{imdbId}/",
                year=year,

            )
        )
    return res


def parse_json_movie(raw_json) -> Optional[MovieDetail]:
    data = {}
    mainColumnData = pjmespatch('props.pageProps.mainColumnData', raw_json)
    if not mainColumnData:
        return None

    data['imdbId'] = pjmespatch('props.pageProps.mainColumnData.id', raw_json) # mainColumnData['id']
    data['imdb_id'] = data['imdbId'].replace('tt', '') # movie id without 'tt'
    data['id'] = data['imdb_id']  # same as imdb_id
    data['url'] = f"{TITLE_URL}{data['imdbId']}/"
    data['title'] =  pjmespatch('props.pageProps.aboveTheFoldData.originalTitleText.text', raw_json)
    data['kind'] = pjmespatch('props.pageProps.mainColumnData.titleType.id',raw_json )
    data['metacritic_rating'] = pjmespatch('props.pageProps.mainColumnData.metacritic.metascore.score',raw_json)
    data["cover_url"] = pjmespatch('props.pageProps.aboveTheFoldData.primaryImage.url', raw_json)
    data['plot'] = pjmespatch('props.pageProps.mainColumnData.plot.plotText.plainText',raw_json)
    data['release_date'] = pjmespatch('props.pageProps.mainColumnData.releaseDate.[year,month,day]', raw_json, _join, separator='-')
    data['year'] = pjmespatch('props.pageProps.aboveTheFoldData.releaseYear.year', raw_json)
    data['duration'] = pjmespatch('props.pageProps.aboveTheFoldData.runtime.seconds', raw_json, lambda x: x / 60 if x else None)
    data['rating'] = pjmespatch('props.pageProps.mainColumnData.ratingsSummary.aggregateRating', raw_json)
    data['votes'] = pjmespatch('props.pageProps.mainColumnData.ratingsSummary.voteCount', raw_json)
    data['genres'] = pjmespatch('props.pageProps.mainColumnData.titleGenres.genres[].genre.text', raw_json)
    data['worldwide_gross'] = pjmespatch('props.pageProps.mainColumnData.worldwideGross.total.[amount,currency]', raw_json, _join)
    data['production_budget'] = pjmespatch('props.pageProps.mainColumnData.productionBudget.budget.[amount,currency]', raw_json, _join)
    data['trailers'] = pjmespatch('props.pageProps.mainColumnData.primaryVideos.edges[].node.id', raw_json, lambda x: [f"{VIDEO_URL}{id}" for id in x if id])
    data['interests'] = pjmespatch('props.pageProps.mainColumnData.interests.edges[].node.primaryText.text', raw_json)
    data['certificates'] = pjmespatch('props.pageProps.mainColumnData.certificates.edges[].node.[country.id,country.text,rating]', raw_json, _certificates_to_dict)
    data['stars'] = pjmespatch('props.pageProps.aboveTheFoldData.castPageTitle.edges[]', raw_json, lambda x: [Person.from_cast(a) for a in x])
    data['directors'] = pjmespatch('props.pageProps.mainColumnData.directorsPageTitle[0].credits[]', raw_json, _to_directors )
    data['filming_locations'] = pjmespatch('props.pageProps.mainColumnData.filmingLocations.edges[].node.text', raw_json)
    data['country_codes'] = pjmespatch('props.pageProps.mainColumnData.countriesDetails.countries[].id', raw_json)
    data['storyline_keywords'] = pjmespatch('props.pageProps.mainColumnData.storylineKeywords.edges[].node.text', raw_json)
    data['production'] = pjmespatch('props.pageProps.mainColumnData.production.edges[].node.company.companyText.text', raw_json)
    data['summaries'] = pjmespatch('props.pageProps.mainColumnData.summaries.edges[].node.plotText.plaidHtml', raw_json)
    data['synopses'] = pjmespatch('props.pageProps.mainColumnData.synopses.edges[].node.plotText.plaidHtml', raw_json)
    data['sound_mixes'] = pjmespatch('props.pageProps.mainColumnData.technicalSpecifications.soundMixes.items[].text', raw_json)
    data['processes'] = pjmespatch('props.pageProps.mainColumnData.technicalSpecifications.processes.items[].process', raw_json)
    data['printed_formats'] = pjmespatch('props.pageProps.mainColumnData.technicalSpecifications.printedFormats.items[].printedFormat', raw_json)
    data['negative_formats'] = pjmespatch('props.pageProps.mainColumnData.technicalSpecifications.negativeFormats.items[].negativeFormat', raw_json)
    data['laboratories'] = pjmespatch('props.pageProps.mainColumnData.technicalSpecifications.laboratories.items[].laboratory', raw_json)
    data['colorations'] = pjmespatch('props.pageProps.mainColumnData.technicalSpecifications.colorations.items[].text', raw_json)
    data['cameras'] = pjmespatch('props.pageProps.mainColumnData.technicalSpecifications.cameras.items[].camera', raw_json)
    data['aspect_ratios'] = pjmespatch('props.pageProps.mainColumnData.technicalSpecifications.aspectRatios.items[].[aspectRatio,attributes[0].text]', raw_json, _none_to_string_in_list)
    data['languages'] = pjmespatch('props.pageProps.mainColumnData.spokenLanguages.spokenLanguages[].id', raw_json)

    # categories
    data['categories'] = {}
    for category in pjmespatch('props.pageProps.mainColumnData.categories[]', raw_json):
        data['categories'].setdefault(category['id'], [])
        jobtitle = category['name']
        category_id  = category['id']
        for category_person in category['section']['items']:
            if category_id == 'cast':
                # cast is a special case, it has character and order
                person = CastMember.from_cast(category_person)
            else:
                category_person['jobTitle'] = jobtitle
                person = Person.from_category(category_person)
            person = person
            data['categories'][category['id']].append(person)

    movie = MovieDetail.model_validate(data)

    return movie


def parse_json_search(raw_json) ->SearchResult:
    title =[]
    for title_data in pjmespatch('props.pageProps.titleResults.results[]', raw_json):
        if title_data.get('imageType','ND') != 'movie': # TODO only movies are supported for now
            continue
        title.append(MovieInfo.from_movie_search(title_data))
    people = []
    for person_data in pjmespatch('props.pageProps.nameResults.results[]', raw_json):
        people.append(Person.from_search(person_data))

    res = SearchResult(titles=title, names=people)
    return res


def parse_json_person_detail(raw_json)-> PersonDetail:

    data = dict()
    data['imdbId'] = pjmespatch('props.pageProps.aboveTheFold.id', raw_json)  # mainColumnData['id']
    data['id'] = pjmespatch('props.pageProps.mainColumnData.id', raw_json).replace('nm', '')
    data['imdb_id'] = data['id']  # same as imdb_id
    data['name'] = pjmespatch('props.pageProps.aboveTheFold.nameText.text', raw_json)
    data['url'] = f"https://www.imdb.com/name/{data['imdbId']}/"
    data['knownfor'] =pjmespatch('props.pageProps.aboveTheFold.knownFor.edges[].node.title.titleText.text', raw_json)
    data['knownfor2']  = pjmespatch('props.pageProps.mainColumnData.knownForFeature.edges[].node.[title.id,title.titleText.text,credit.characters[].name]', raw_json)
    data['image_url'] = pjmespatch('props.pageProps.aboveTheFold.primaryImage.url', raw_json)
    data['bio'] = pjmespatch('props.pageProps.aboveTheFold.bio.text.plainText', raw_json)
    data['height'] = pjmespatch('props.pageProps.mainColumnData.height.displayableProperty.value.plainText', raw_json)
    data['primary_profession'] = pjmespatch('props.pageProps.aboveTheFold.primaryProfessions[].category.text', raw_json)
    data['birth_date'] = pjmespatch('props.pageProps.aboveTheFold.birthDate.date', raw_json)
    data['birth_place'] = pjmespatch('props.pageProps.mainColumnData.birthLocation.text', raw_json)
    data['death_date'] = pjmespatch('props.pageProps.aboveTheFold.deathDate.date', raw_json)
    data['death_place'] = pjmespatch('props.pageProps.mainColumnData.deathLocation.text', raw_json)
    data['jobs'] = pjmespatch('props.pageProps.mainColumnData.jobs[].category.text', raw_json)
    data['credits'] = pjmespatch('props.pageProps.mainColumnData.releasedPrimaryCredits[].credits[].edges[].node[].[category.id,title.id,title.originalTitleText.text,title.titleType.text,title.primaryImage.url,title.releaseYear.year,titleGenres.genres[].genre.text]', raw_json, _feed_credits)
    data['unreleased_credits'] = pjmespatch('props.pageProps.mainColumnData.unreleasedPrimaryCredits[].credits[].edges[].node[].[category.id,title.id,title.originalTitleText.text,title.titleType.text,title.primaryImage.url,title.releaseYear.year,titleGenres.genres[].genre.text]', raw_json, _feed_credits)

    person = PersonDetail.model_validate(data)
    return person