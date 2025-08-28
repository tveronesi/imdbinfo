from typing import Optional, List
import logging

import jmespath

from .models import (
    MovieDetail,
    Person,
    MovieBriefInfo,
    SearchResult,
    CastMember,
    PersonDetail,
    InfoSeries,
    InfoEpisode,
    SeasonEpisode,
    SeasonEpisodesList,
    BulkedEpisode,
    TvSeriesDetail,
    TvEpisodeDetail,
    SERIES_IDENTIFIERS,
    EPISODE_IDENTIFIERS, AkaInfo, CompanyInfo,
)
from .transformers import (
    _release_date,
    _dict_votes_,
    _none_to_string_in_list,
    _join,
    _certificates_to_dict, _parse_mpaa
)

VIDEO_URL = "https://www.imdb.com/video/"
TITLE_URL = "https://www.imdb.com/title/"
COMPANY_URL = "https://www.imdb.com/company/"

logger = logging.getLogger(__name__)


def pjmespatch(query, data, post_process=None, *args, **kwargs):
    result = jmespath.search(query, data)
    logger.debug("Query %s -> %s", query, result)
    if post_process:
        return post_process(result, *args, **kwargs)
    return result


def _parse_directors(result):
    if result is None:
        return []
    return [
        Person.from_directors(a)
        for a in result
        if a.get("name") and a.get("name").get("id")
    ]


def _parse_credits(result) -> dict:
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
        genres = ",".join(itemCast[6] or [])

        res.setdefault(category, [])
        res[category].append(
            MovieBriefInfo(
                id=imdbId.replace("tt", ""),
                imdbId=imdbId,
                imdb_id=imdbId.replace("tt", ""),
                title=titleOriginal,
                kind=type,
                cover_url=imageUrl,
                url=f"{TITLE_URL}{imdbId}/",
                year=year,
            )
        )
    return res


def parse_json_movie(raw_json) -> Optional[MovieDetail]:
    logger.debug("Parsing movie JSON")
    data = {}
    mainColumnData = pjmespatch("props.pageProps.mainColumnData", raw_json)
    if not mainColumnData:
        logger.warning("'mainColumnData' not found in movie JSON")
        return None
    movie_kind = pjmespatch("props.pageProps.mainColumnData.titleType.id", raw_json) # movie/tvSeries/tvEpisode
    data["imdbId"] = pjmespatch("props.pageProps.mainColumnData.id", raw_json)  # mainColumnData['id']
    data["imdb_id"] = data["imdbId"].replace("tt", "")  # movie id without 'tt'
    data["id"] = data["imdb_id"]  # same as imdb_id
    data["url"] = f"{TITLE_URL}{data['imdbId']}/"
    data["title"] = pjmespatch("props.pageProps.aboveTheFoldData.originalTitleText.text", raw_json)
    data["title_localized"] = pjmespatch("props.pageProps.aboveTheFoldData.titleText.text", raw_json)
    data["title_akas"] = pjmespatch("props.pageProps.mainColumnData.akas.edges[].node.text", raw_json)
    data["kind"] = movie_kind
    data["metacritic_rating"] = pjmespatch("props.pageProps.mainColumnData.metacritic.metascore.score", raw_json)
    data["cover_url"] = pjmespatch("props.pageProps.aboveTheFoldData.primaryImage.url", raw_json)
    data["plot"] = pjmespatch("props.pageProps.mainColumnData.plot.plotText.plainText", raw_json)
    # TODO release_date format with datetime...
    data["release_date"] = pjmespatch(
        "props.pageProps.mainColumnData.releaseDate", raw_json, _release_date)
    data["year"] = pjmespatch("props.pageProps.aboveTheFoldData.releaseYear.year", raw_json)
    data["year_end"] = pjmespatch("props.pageProps.aboveTheFoldData.releaseYear.endYear", raw_json)
    data["duration"] = pjmespatch(
        "props.pageProps.aboveTheFoldData.runtime.seconds", raw_json, lambda x: x / 60 if x else None
    )
    data["rating"] = pjmespatch("props.pageProps.mainColumnData.ratingsSummary.aggregateRating", raw_json)
    data["votes"] = pjmespatch("props.pageProps.mainColumnData.ratingsSummary.voteCount", raw_json)
    data["genres"] = pjmespatch("props.pageProps.mainColumnData.titleGenres.genres[].genre.text", raw_json)
    data["worldwide_gross"] = pjmespatch(
        "props.pageProps.mainColumnData.worldwideGross.total.[amount,currency]", raw_json, _join
    )
    data["production_budget"] = pjmespatch(
        "props.pageProps.mainColumnData.productionBudget.budget.[amount,currency]", raw_json, _join
    )
    data["trailers"] = pjmespatch(
        "props.pageProps.mainColumnData.primaryVideos.edges[].node.id",
        raw_json,
        lambda x: [f"{VIDEO_URL}{id}" for id in x if id],
    )
    data["interests"] = pjmespatch("props.pageProps.mainColumnData.interests.edges[].node.primaryText.text", raw_json)
    data["certificates"] = pjmespatch(
        "props.pageProps.mainColumnData.certificates.edges[].node.[id,country.id,country.text,rating,ratingReason,attributes[].text]",
        raw_json,
        _certificates_to_dict,
    )
    # TODO is not working 100% need deeper check
    data["mpaa"] = pjmespatch(f"props.pageProps.mainColumnData.certificates.edges[?node.ratingsBody.id=='MPAA']", raw_json, _parse_mpaa)
    data["stars"] = pjmespatch(
        "props.pageProps.aboveTheFoldData.castPageTitle.edges[]", raw_json, lambda x: [Person.from_cast(a) for a in x]
    )
    data["directors"] = pjmespatch(
        "props.pageProps.mainColumnData.directorsPageTitle[0].credits[]", raw_json, _parse_directors
    )
    data["filming_locations"] = pjmespatch(
        "props.pageProps.mainColumnData.filmingLocations.edges[].node.text", raw_json
    )
    data["country_codes"] = pjmespatch("props.pageProps.mainColumnData.countriesDetails.countries[].id", raw_json)
    data["countries"] = pjmespatch("props.pageProps.mainColumnData.countriesDetails.countries[].text", raw_json)
    data["storyline_keywords"] = pjmespatch(
        "props.pageProps.mainColumnData.storylineKeywords.edges[].node.text", raw_json
    )
    data["production"] = pjmespatch(
        "props.pageProps.mainColumnData.production.edges[].node.company.companyText.text", raw_json
    )
    data["summaries"] = pjmespatch("props.pageProps.mainColumnData.summaries.edges[].node.plotText.plaidHtml", raw_json)
    data["synopses"] = pjmespatch("props.pageProps.mainColumnData.synopses.edges[].node.plotText.plaidHtml", raw_json)
    data["sound_mixes"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.soundMixes.items[].text", raw_json
    )
    data["processes"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.processes.items[].process", raw_json
    )
    data["printed_formats"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.printedFormats.items[].printedFormat", raw_json
    )
    data["negative_formats"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.negativeFormats.items[].negativeFormat", raw_json
    )
    data["laboratories"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.laboratories.items[].laboratory", raw_json
    )
    data["colorations"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.colorations.items[].text", raw_json
    )
    data["cameras"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.cameras.items[].camera", raw_json
    )
    data["aspect_ratios"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.aspectRatios.items[].[aspectRatio,attributes[0].text]",
        raw_json,
        _none_to_string_in_list,
    )
    data["languages"] = pjmespatch("props.pageProps.mainColumnData.spokenLanguages.spokenLanguages[].id", raw_json)
    data["languages_text"] = pjmespatch("props.pageProps.mainColumnData.spokenLanguages.spokenLanguages[].text", raw_json)
    # categories
    data["categories"] = {}
    for category in pjmespatch("props.pageProps.mainColumnData.categories[]", raw_json):
        data["categories"].setdefault(category["id"], [])
        jobtitle = category["name"]
        category_id = category["id"]
        for category_person in category["section"]["items"]:
            if category_id == "cast":
                # cast is a special case, it has character and order
                person = CastMember.from_cast(category_person)
            else:
                category_person["jobTitle"] = jobtitle
                person = Person.from_category(category_person)
            person = person
            data["categories"][category["id"]].append(person)

    # company_credits [ distributors , production_companies, special_effects_companies, etc ]
    data["company_credits"] =  {}
    for company_credits_category in pjmespatch("props.pageProps.mainColumnData.companyCreditCategories[]",raw_json):
        cat_id = company_credits_category.get('category').get('id')
        if not cat_id: # sometimes there is no id, skip those
            continue
        data["company_credits"].setdefault(cat_id, [])
        for company in company_credits_category["companyCredits"]["edges"]:
            company_node = company.get("node", {})
            company_data = {
                "id": company_node.get("company", {}).get("id", "").replace("co", ""),
                "imdb_id": company_node.get("company", {}).get("id", "").replace("co", ""),
                "imdbId": company_node.get("company", {}).get("id", ""),
                "name": company_node.get("displayableProperty", {}).get("value", {}).get("plainText", ""),
                "url": f"{COMPANY_URL}{company_node.get('company', {}).get('id', '')}/",
                "attributes": pjmespatch("[].text",company_node.get("attributes")),
                "countries" : pjmespatch("[].text",company_node.get("countries"))
            }
            data["company_credits"][cat_id].append(CompanyInfo(**company_data))

    # If Series/Episode kind
    # tvMovie,short,movie,tvEpisode,tvMiniseries,tvSpecial,tvShort,videoGame,video,musicVideo,podcastEpisode,podcastSeries
    if movie_kind in SERIES_IDENTIFIERS:
        data["info_series"] = InfoSeries(
            display_years= pjmespatch("props.pageProps.mainColumnData.episodes.displayableYears.edges[].node.year", raw_json),
            display_seasons= pjmespatch("props.pageProps.mainColumnData.episodes.displayableSeasons.edges[].node.season", raw_json)
        )
        logger.info("Parsed series %s", data["imdbId"])
        movie = TvSeriesDetail.model_validate(data)

    elif movie_kind in EPISODE_IDENTIFIERS:
        data["info_episode"] = InfoEpisode (
            season_n= pjmespatch("props.pageProps.mainColumnData.series.episodeNumber.seasonNumber", raw_json),
            episode_n= pjmespatch("props.pageProps.mainColumnData.series.episodeNumber.episodeNumber", raw_json),
            series_imdbId= pjmespatch("props.pageProps.mainColumnData.series.series.id", raw_json),
            series_title= pjmespatch("props.pageProps.mainColumnData.series.series.originalTitleText.text", raw_json),
            series_title_localized= pjmespatch("props.pageProps.mainColumnData.series.series.titleText.text", raw_json),
        )
        logger.info("Parsed episode %s", data["imdbId"])
        movie = TvEpisodeDetail.model_validate(data)
    else:
        movie = MovieDetail.model_validate(data)
        logger.info("Parsed movie %s", movie.imdbId)

    return movie


def parse_json_search(raw_json) -> SearchResult:
    logger.debug("Parsing search results JSON")
    title = []
    for title_data in pjmespatch("props.pageProps.titleResults.results[]", raw_json):
        title.append(MovieBriefInfo.from_movie_search(title_data))
    people = []
    for person_data in pjmespatch("props.pageProps.nameResults.results[]", raw_json):
        people.append(Person.from_search(person_data))

    res = SearchResult(titles=title, names=people)
    logger.info("Parsed search results: %s titles, %s names", len(title), len(people))
    return res


def parse_json_person_detail(raw_json) -> PersonDetail:
    logger.debug("Parsing person detail JSON")

    data = dict()
    data["imdbId"] = pjmespatch("props.pageProps.aboveTheFold.id", raw_json)  # mainColumnData['id']
    data["id"] = pjmespatch("props.pageProps.mainColumnData.id", raw_json).replace("nm", "")
    data["imdb_id"] = data["id"]  # same as imdb_id
    data["name"] = pjmespatch("props.pageProps.aboveTheFold.nameText.text", raw_json)
    data["url"] = f"https://www.imdb.com/name/{data['imdbId']}/"
    data["knownfor"] = pjmespatch("props.pageProps.aboveTheFold.knownFor.edges[].node.title.titleText.text", raw_json)
    data["knownfor2"] = pjmespatch(
        "props.pageProps.mainColumnData.knownForFeature.edges[].node.[title.id,title.titleText.text,credit.characters[].name]",
        raw_json,
    )
    data["image_url"] = pjmespatch("props.pageProps.aboveTheFold.primaryImage.url", raw_json)
    data["bio"] = pjmespatch("props.pageProps.aboveTheFold.bio.text.plainText", raw_json)
    data["height"] = pjmespatch("props.pageProps.mainColumnData.height.displayableProperty.value.plainText", raw_json)
    data["primary_profession"] = pjmespatch("props.pageProps.aboveTheFold.primaryProfessions[].category.text", raw_json)
    data["birth_date"] = pjmespatch("props.pageProps.aboveTheFold.birthDate.date", raw_json)
    data["birth_place"] = pjmespatch("props.pageProps.mainColumnData.birthLocation.text", raw_json)
    data["death_date"] = pjmespatch("props.pageProps.aboveTheFold.deathDate.date", raw_json)
    data["death_place"] = pjmespatch("props.pageProps.mainColumnData.deathLocation.text", raw_json)
    data["death_reason"] = pjmespatch("props.pageProps.mainColumnData.deathReason.text", raw_json)
    data["jobs"] = pjmespatch("props.pageProps.mainColumnData.jobs[].category.text", raw_json)
    data["credits"] = pjmespatch(
        "props.pageProps.mainColumnData.releasedPrimaryCredits[].credits[].edges[].node[].[category.id,title.id,title.originalTitleText.text,title.titleType.text,title.primaryImage.url,title.releaseYear.year,titleGenres.genres[].genre.text]",
        raw_json,
        _parse_credits,
    )
    data["unreleased_credits"] = pjmespatch(
        "props.pageProps.mainColumnData.unreleasedPrimaryCredits[].credits[].edges[].node[].[category.id,title.id,title.originalTitleText.text,title.titleType.text,title.primaryImage.url,title.releaseYear.year,titleGenres.genres[].genre.text]",
        raw_json,
        _parse_credits,
    )

    person = PersonDetail.model_validate(data)
    logger.info("Parsed person %s", person.name)
    return person


def parse_json_season_episodes(raw_json) -> SeasonEpisodesList:
    series_imdbId = pjmespatch("props.pageProps.contentData.data.title.id", raw_json)
    current_season = pjmespatch("props.pageProps.contentData.section.currentSeason", raw_json)
    top_rated_episode = pjmespatch("props.pageProps.contentData.data.title.episodes.topRated.edges[0].node.ratingsSummary.aggregateRating",raw_json)
    total_series_episodes = pjmespatch("props.pageProps.contentData.data.title.episodes.totalEpisodes.total", raw_json)
    total_series_seasons = len(pjmespatch("props.pageProps.contentData.data.title.episodes.seasons", raw_json))
    top_ten_episodes =pjmespatch("props.pageProps.contentData.data.title.episodes.topTenEpisodes.edges[].[node.id,node.ratingsSummary.aggregateRating,node.ratingsSummary.voteCount]", raw_json,
                                 _dict_votes_)
    logger.debug("Parsing episodes JSON")
    season_episodes = []
    for episode_data in pjmespatch("props.pageProps.contentData.section.episodes.items", raw_json):
        season_episodes.append(SeasonEpisode.from_episode_data(episode_data))

    episodes_list_object = SeasonEpisodesList(
        series_imdbId=series_imdbId,  # remove 'tt' prefix
        season_number=current_season,
        top_rating_episode=top_rated_episode,
        total_series_episodes=total_series_episodes,
        total_series_seasons=total_series_seasons,
        top_ten_episodes=top_ten_episodes,
        episodes=season_episodes,
    )
    logger.info("Parsed %d episodes for season", len(season_episodes))
    return episodes_list_object


def parse_json_bulked_episodes(raw_json) -> List[BulkedEpisode]:
    all_episodes = []
    for episode_data in pjmespatch("props.pageProps.searchResults.titleResults.titleListItems", raw_json):
        all_episodes.append(BulkedEpisode.from_bulked_episode_data(episode_data))
    logger.info("Parsed %d bulked episodes", len(all_episodes))
    return all_episodes


def parse_json_akas(raw_json) -> List[AkaInfo]:
    logger.debug("Parsing akas JSON")
    data = {}
    data["imdbId"] = pjmespatch("id", raw_json)
    data["akas"] = [ AkaInfo.from_data(*a) for a in pjmespatch("akas.edges[].node[].[title, country.code,country.name, language.code, language.name]", raw_json)]
    return data