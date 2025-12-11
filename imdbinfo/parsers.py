# MIT License
# Copyright (c) 2025 tveronesi+imdbinfo@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Optional, List, Dict, Union, Any
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
    EPISODE_IDENTIFIERS,
    AkaInfo,
    CompanyInfo,
    AkasData,
    AwardInfo,
)
from .transformers import (
    _release_date,
    _dict_votes_,
    _none_to_string_in_list,
    _join,
    _certificates_to_dict,
    _parse_mpaa,
)

VIDEO_URL = "https://www.imdb.com/video/"
TITLE_URL = "https://www.imdb.com/title/"
COMPANY_URL = "https://www.imdb.com/company/"

logger = logging.getLogger(__name__)

newCreditCategoryIdToOldCategoryIdObject = {
    "amzn1.imdb.concept.name_credit_category.a9ab2a8b-9153-4edb-a27a-7c2346830d77": "actor",
    "amzn1.imdb.concept.name_credit_category.7f6d81aa-23aa-4503-844d-38201eb08761": "actress",
    "amzn1.imdb.concept.name_credit_category.44d5f7aa-fe79-46e8-a72a-0f861c37bfff": "animation_department",
    "amzn1.imdb.concept.name_credit_category.d782ea94-18fe-4513-a71c-7cdd652ef2d8": "art_department",
    "amzn1.imdb.concept.name_credit_category.60a44752-af76-44f7-9de0-ec51aea2180d": "art_director",
    "amzn1.imdb.concept.name_credit_category.306aa45f-30d6-4786-a7f9-b3103ebca806": "assistant_director",
    "amzn1.imdb.concept.name_credit_category.daf5bc70-1a41-413b-af5a-af1e285bf049": "camera_department",
    "amzn1.imdb.concept.name_credit_category.5c60f6fa-29f1-40a4-8fe5-b4c26a6a7db4": "casting_department",
    "amzn1.imdb.concept.name_credit_category.67b6990c-f7de-4882-916b-dad87ec4406a": "casting_director",
    "amzn1.imdb.concept.name_credit_category.73ffe317-963e-4c19-b4fd-54a9a596c959": "choreographer",
    "amzn1.imdb.concept.name_credit_category.e2bf7217-c947-461b-aa58-47e27da1c78e": "cinematographer",
    "amzn1.imdb.concept.name_credit_category.00f5faa0-5f76-4eb5-87a1-ec8d484d1779": "composer",
    "amzn1.imdb.concept.name_credit_category.19e9f38d-89a0-4963-91c1-e3958f1d4534": "costume_department",
    "amzn1.imdb.concept.name_credit_category.a2d21716-45de-40e2-9f7d-9de01fc34a71": "costume_designer",
    "amzn1.imdb.concept.name_credit_category.92fde7c9-50a1-4ec5-9897-4514ea9851b2": "costume_supervisor",
    "amzn1.imdb.concept.name_credit_category.ace5cb4c-8708-4238-9542-04641e7c8171": "director",
    "amzn1.imdb.concept.name_credit_category.63b1f9c6-9d3b-4be6-88fc-6321c9fa5ae2": "editor",
    "amzn1.imdb.concept.name_credit_category.2677b7dc-373c-41d1-8b13-7bdc171ca372": "editorial_department",
    "amzn1.imdb.concept.name_credit_category.7f9c1f9d-8d79-461b-8b1e-31aecbc810fb": "electrical_department",
    "amzn1.imdb.concept.name_credit_category.672aa0f4-3d77-4a51-ac8f-2318eb03c2a2": "hair_stylist",
    "amzn1.imdb.concept.name_credit_category.14374461-bf01-43c1-b3b7-da298b97880d": "intimacy_coordinator",
    "amzn1.imdb.concept.name_credit_category.95338d09-b2a1-4188-ac9f-55f5255bb437": "location_management",
    "amzn1.imdb.concept.name_credit_category.6d7dae61-5a76-4127-82db-acbbb5ecd768": "make_up_artist",
    "amzn1.imdb.concept.name_credit_category.c3f25a53-cdb2-4260-ab78-1ef0a6052ee1": "make_up_department",
    "amzn1.imdb.concept.name_credit_category.a7c2d410-e513-4bd7-85d5-73060ec46a84": "miscellaneous",
    "amzn1.imdb.concept.name_credit_category.aad1533c-6974-45a4-ba98-5f2f43286cfc": "music_department",
    "amzn1.imdb.concept.name_credit_category.7a3df188-0e65-41f9-a15e-1c363c7093eb": "music_supervisor",
    "amzn1.imdb.concept.name_credit_category.0af123ce-1605-4a51-93cf-7ad477b11832": "producer",
    "amzn1.imdb.concept.name_credit_category.990a90e2-4761-41d9-bfd6-3bd90e122762": "production_department",
    "amzn1.imdb.concept.name_credit_category.ce558628-5755-438c-92d7-757518864a00": "production_designer",
    "amzn1.imdb.concept.name_credit_category.b3eac1a6-a62b-4f46-8b93-5331b94f6af3": "production_manager",
    "amzn1.imdb.concept.name_credit_category.1305c1a1-04bc-4cde-a6ac-dad9c9a6e11d": "property_master",
    "amzn1.imdb.concept.name_credit_category.bf32c344-897c-4e0a-b401-36bfa2c3669e": "script_department",
    "amzn1.imdb.concept.name_credit_category.15403c03-b2d7-46b6-9c57-058f1659fd14": "script_supervisor",
    "amzn1.imdb.concept.name_credit_category.d6017bdb-c3e7-4ca5-944b-68d74b9de6b6": "self",
    "amzn1.imdb.concept.name_credit_category.359a8a76-1c15-4fd1-bd31-26c7e2a046f8": "set_decorator",
    "amzn1.imdb.concept.name_credit_category.4cdb8a99-4f08-4cfe-9db5-ee31f23f7db3": "showrunner",
    "amzn1.imdb.concept.name_credit_category.ce258419-131b-41f0-b2c5-227f5d9b719f": "sound_department",
    "amzn1.imdb.concept.name_credit_category.4df03a1e-b90d-4c4a-8638-29eea26a156b": "soundtrack",
    "amzn1.imdb.concept.name_credit_category.856eb49a-7610-47d5-9a07-c7df3f715075": "special_effects",
    "amzn1.imdb.concept.name_credit_category.15c98c24-1815-4935-a958-ed747aeffee4": "stunt_coordinator",
    "amzn1.imdb.concept.name_credit_category.79cc5241-902a-4d4b-971d-27a3590fa1f4": "stunts",
    "amzn1.imdb.concept.name_credit_category.90de891d-6d5e-4711-9179-3eda18bd18e1": "thanks",
    "amzn1.imdb.concept.name_credit_category.8c952a79-f27c-4e5a-be85-b114b0ecd04e": "transportation_department",
    "amzn1.imdb.concept.name_credit_category.fcb0b804-e618-4044-8a74-79e94d17e3cd": "visual_effects",
    "amzn1.imdb.concept.name_credit_category.c84ecaff-add5-4f2e-81db-102a41881fe3": "writer",
}


def pjmespatch(query, data, post_process=None, *args, **kwargs):
    result = jmespath.search(query, data)
    # logger.debug("Query %s -> %s", query, result)
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


def _parse_creators(result):
    if result is None:
        return []
    return [
        Person.from_creators(a)
        for a in result
        if a.get("name") and a.get("name").get("id")
    ]


def _parse_credits(result) -> dict:
    """feed credits from the page 'name' to the PersonDetail model"""

    if result is None:
        return {}
    res: Dict[str, List[MovieBriefInfo]] = {}
    for itemCast in result:
        # ['writer', 'tt27665778', 'Horizon: An American Saga - Chapter 2', 'Movie', 'https://m.media-amazon.com/images/M/MV5BMDg1OWI3NTYtY2IwMy00NmQ4LTk5YWUtZmViNmU5YTFkNGU5XkEyXkFqcGc@._V1_.jpg', 2024, None]
        category = itemCast[0]
        imdbId = itemCast[1]
        titleOriginal = itemCast[2]
        type = itemCast[3]
        imageUrl = itemCast[4]
        year = itemCast[5]

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


def _parse_credits_v2(result) -> dict:
    """feed credits from the page 'name' to the PersonDetail model"""

    if result is None:
        return {}
    res: Dict[str, List[MovieBriefInfo]] = {}
    for itemCastGroup in result:
        _category_ = itemCastGroup["grouping"]["groupingId"]
        categoryTextLocalized = itemCastGroup["grouping"]["text"]

        # map new category ids to old ones
        category_id = newCreditCategoryIdToOldCategoryIdObject.get(
            _category_, categoryTextLocalized
        )
        res.setdefault(category_id, [])
        for item_ in itemCastGroup["credits"]["edges"]:
            titleData = item_["node"]["title"]
            imdbId = titleData["id"]
            titleOriginal = titleData["originalTitleText"]["text"]
            titleLocalized = titleData["titleText"]["text"]
            title_type = titleData["titleType"]["id"]
            imageUrl = (
                titleData["primaryImage"]["url"]
                if titleData.get("primaryImage")
                else None
            )
            year = (
                titleData["releaseYear"]["year"]
                if titleData.get("releaseYear")
                else None
            )

            res[category_id].append(
                MovieBriefInfo(
                    id=imdbId.replace("tt", ""),
                    imdbId=imdbId,
                    imdb_id=imdbId.replace("tt", ""),
                    title=titleOriginal,
                    title_localized=titleLocalized,
                    kind=title_type,
                    cover_url=imageUrl,
                    url=f"{TITLE_URL}{imdbId}/",
                    year=year,
                )
            )
    return res


def _parse_jobs_v2(raw_jobs) -> List[str]:
    if raw_jobs is None:
        return []
    jobs = []
    for job in raw_jobs:
        job_name = newCreditCategoryIdToOldCategoryIdObject.get(job, job)
        jobs.append(job_name)
    return jobs


def _parse_awards(awards_node) -> AwardInfo:
    if awards_node is None:
        return AwardInfo(wins=0, nominations=0)
    awards_dict = {}
    if len(awards_node) > 2 and awards_node[2]:
        prestigious_award = awards_node[2]
        award_name = prestigious_award.get("award", {}).get("text", "")
        wins = prestigious_award.get("wins", 0)
        nominations = prestigious_award.get("nominations", 0)
        awards_dict["prestigious_award"] = {
            "wins": wins,
            "nominations": nominations,
            "name": award_name,
        }
    awards_dict["wins"] = awards_node[0] if len(awards_node) > 0 else 0
    awards_dict["nominations"] = awards_node[1] if len(awards_node) > 1 else 0
    awards = AwardInfo(**awards_dict)
    return awards


def parse_json_movie(raw_json) -> Optional[MovieDetail]:
    logger.debug("Parsing movie JSON")
    data = {}
    movie: Union[TvSeriesDetail, TvEpisodeDetail, MovieDetail]
    mainColumnData = pjmespatch("props.pageProps.mainColumnData", raw_json)
    if not mainColumnData:
        logger.warning("'mainColumnData' not found in movie JSON")
        return None
    movie_kind = pjmespatch(
        "props.pageProps.mainColumnData.titleType.id", raw_json
    )  # movie/tvSeries/tvEpisode
    data["imdbId"] = pjmespatch(
        "props.pageProps.mainColumnData.id", raw_json
    )  # mainColumnData['id']
    data["imdb_id"] = data["imdbId"].replace("tt", "")  # movie id without 'tt'
    data["id"] = data["imdb_id"]  # same as imdb_id
    data["url"] = f"{TITLE_URL}{data['imdbId']}/"
    data["title"] = pjmespatch(
        "props.pageProps.aboveTheFoldData.originalTitleText.text", raw_json
    )
    data["awards"] = pjmespatch(
        "props.pageProps.mainColumnData.[wins.total,nominationsExcludeWins.total,prestigiousAwardSummary ]",
        raw_json,
        _parse_awards,
    )
    data["title_localized"] = pjmespatch(
        "props.pageProps.aboveTheFoldData.titleText.text", raw_json
    )
    data["title_akas"] = pjmespatch(
        "props.pageProps.mainColumnData.akas.edges[].node.text", raw_json
    )
    data["kind"] = movie_kind
    data["metacritic_rating"] = pjmespatch(
        "props.pageProps.mainColumnData.metacritic.metascore.score", raw_json
    )
    data["cover_url"] = pjmespatch(
        "props.pageProps.aboveTheFoldData.primaryImage.url", raw_json
    )
    data["plot"] = pjmespatch(
        "props.pageProps.mainColumnData.plot.plotText.plainText", raw_json
    )
    # TODO release_date format with datetime...
    data["release_date"] = pjmespatch(
        "props.pageProps.mainColumnData.releaseDate", raw_json, _release_date
    )
    data["year"] = pjmespatch(
        "props.pageProps.aboveTheFoldData.releaseYear.year", raw_json
    )
    data["year_end"] = pjmespatch(
        "props.pageProps.aboveTheFoldData.releaseYear.endYear", raw_json
    )
    data["duration"] = pjmespatch(
        "props.pageProps.aboveTheFoldData.runtime.seconds",
        raw_json,
        lambda x: x / 60 if x else None,
    )
    data["rating"] = pjmespatch(
        "props.pageProps.mainColumnData.ratingsSummary.aggregateRating", raw_json
    )
    data["votes"] = pjmespatch(
        "props.pageProps.mainColumnData.ratingsSummary.voteCount", raw_json
    )
    data["genres"] = pjmespatch(
        "props.pageProps.mainColumnData.genres.genres[].text", raw_json
    )
    data["worldwide_gross"] = pjmespatch(
        "props.pageProps.mainColumnData.worldwideGross.total.[amount,currency]",
        raw_json,
        _join,
    )
    data["production_budget"] = pjmespatch(
        "props.pageProps.mainColumnData.productionBudget.budget.[amount,currency]",
        raw_json,
        _join,
    )
    data["trailers"] = pjmespatch(
        "props.pageProps.mainColumnData.primaryVideos.edges[].node.id",
        raw_json,
        lambda x: [f"{VIDEO_URL}{id}" for id in x if id],
    )
    data["interests"] = pjmespatch(
        "props.pageProps.mainColumnData.interests.edges[].node.primaryText.text",
        raw_json,
    )
    data["certificates"] = pjmespatch(
        "props.pageProps.mainColumnData.certificates.edges[].node.[id,country.id,country.text,rating,ratingReason,attributes[].text]",
        raw_json,
        _certificates_to_dict,
    )
    # TODO is not working 100% need deeper check
    data["mpaa"] = pjmespatch(
        "props.pageProps.mainColumnData.certificates.edges[?node.ratingsBody.id=='MPAA']",
        raw_json,
        _parse_mpaa,
    )
    data["stars"] = pjmespatch(
        "props.pageProps.aboveTheFoldData.castPageTitle.edges[]",
        raw_json,
        lambda x: [Person.from_cast(a) for a in x],
    )
    data["directors"] = pjmespatch(
        "props.pageProps.mainColumnData.directorsPageTitle[0].credits[]",
        raw_json,
        _parse_directors,
    )
    data["filming_locations"] = pjmespatch(
        "props.pageProps.mainColumnData.filmingLocations.edges[].node.text", raw_json
    )
    data["country_codes"] = pjmespatch(
        "props.pageProps.mainColumnData.countriesDetails.countries[].id", raw_json
    )
    data["countries"] = pjmespatch(
        "props.pageProps.mainColumnData.countriesDetails.countries[].text", raw_json
    )
    data["storyline_keywords"] = pjmespatch(
        "props.pageProps.mainColumnData.storylineKeywords.edges[].node.text", raw_json
    )
    data["production"] = pjmespatch(
        "props.pageProps.mainColumnData.production.edges[].node.company.companyText.text",
        raw_json,
    )
    data["summaries"] = pjmespatch(
        "props.pageProps.mainColumnData.summaries.edges[].node.plotText.plaidHtml",
        raw_json,
    )
    data["synopses"] = pjmespatch(
        "props.pageProps.mainColumnData.synopses.edges[].node.plotText.plaidHtml",
        raw_json,
    )
    data["sound_mixes"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.soundMixes.items[].text",
        raw_json,
    )
    data["processes"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.processes.items[].process",
        raw_json,
    )
    data["printed_formats"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.printedFormats.items[].printedFormat",
        raw_json,
    )
    data["negative_formats"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.negativeFormats.items[].negativeFormat",
        raw_json,
    )
    data["laboratories"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.laboratories.items[].laboratory",
        raw_json,
    )
    data["colorations"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.colorations.items[].text",
        raw_json,
    )
    data["cameras"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.cameras.items[].camera",
        raw_json,
    )
    data["aspect_ratios"] = pjmespatch(
        "props.pageProps.mainColumnData.technicalSpecifications.aspectRatios.items[].[aspectRatio,attributes[0].text]",
        raw_json,
        _none_to_string_in_list,
    )
    data["languages"] = pjmespatch(
        "props.pageProps.mainColumnData.spokenLanguages.spokenLanguages[].id", raw_json
    )
    data["languages_text"] = pjmespatch(
        "props.pageProps.mainColumnData.spokenLanguages.spokenLanguages[].text",
        raw_json,
    )
    # categories

    data["categories"] = {"cast": []}  # init with cast to avoid keyerror
    # ensure all categories are present
    [
        data["categories"].setdefault(c, [])
        for c in newCreditCategoryIdToOldCategoryIdObject.values()
    ]

    for category in (
        pjmespatch("props.pageProps.mainColumnData.categories[]", raw_json) or []
    ):
        jobtitle = category["name"]
        _category_id_ = category["id"]

        category_id = newCreditCategoryIdToOldCategoryIdObject.get(
            _category_id_, _category_id_
        )
        for category_person in category["section"]["items"]:
            if category_person.get("isCast", False):
                # cast is a special case, it has character and order
                person = CastMember.from_cast(category_person)
                category_id = "cast"  # override category to 'cast'
            else:
                category_person["jobTitle"] = jobtitle
                person = Person.from_category(category_person)
            person = person

            data["categories"].setdefault(category_id, [])
            data["categories"][category_id].append(person)

    # company_credits [ distributors , production_companies, special_effects_companies, etc ]
    data["company_credits"] = {}
    for company_credits_category in pjmespatch(
        "props.pageProps.mainColumnData.companyCreditCategories[]", raw_json
    ):
        cat_id = company_credits_category.get("category").get("id")
        if not cat_id:  # sometimes there is no id, skip those
            continue
        data["company_credits"].setdefault(cat_id, [])
        for company in company_credits_category["companyCredits"]["edges"]:
            company_node = company.get("node", {})
            company_data = {
                "id": company_node.get("company", {}).get("id", "").replace("co", ""),
                "imdb_id": company_node.get("company", {})
                .get("id", "")
                .replace("co", ""),
                "imdbId": company_node.get("company", {}).get("id", ""),
                "name": company_node.get("displayableProperty", {})
                .get("value", {})
                .get("plainText", ""),
                "url": f"{COMPANY_URL}{company_node.get('company', {}).get('id', '')}/",
                "attributes": pjmespatch("[].text", company_node.get("attributes")),
                "countries": pjmespatch("[].text", company_node.get("countries")),
            }
            data["company_credits"][cat_id].append(CompanyInfo(**company_data))

    # If Series/Episode kind
    # tvMovie,short,movie,tvEpisode,tvMiniseries,tvSpecial,tvShort,videoGame,video,musicVideo,podcastEpisode,podcastSeries
    if movie_kind in SERIES_IDENTIFIERS:
        data["info_series"] = InfoSeries(
            display_years=pjmespatch(
                "props.pageProps.mainColumnData.episodes.displayableYears.edges[].node.year",
                raw_json,
            )
            or [],
            display_seasons=pjmespatch(
                "props.pageProps.mainColumnData.episodes.displayableSeasons.edges[].node.season",
                raw_json,
            )
            or [],
            creators=pjmespatch(
                "props.pageProps.mainColumnData.principalCreditsV2[0].credits[]",
                raw_json,
                _parse_creators,
            ),
        )
        logger.info("Parsed series %s", data["imdbId"])
        movie = TvSeriesDetail.model_validate(data)

    elif movie_kind in EPISODE_IDENTIFIERS:
        data["info_episode"] = InfoEpisode(
            season_n=pjmespatch(
                "props.pageProps.mainColumnData.series.episodeNumber.seasonNumber",
                raw_json,
            ),
            episode_n=pjmespatch(
                "props.pageProps.mainColumnData.series.episodeNumber.episodeNumber",
                raw_json,
            ),
            series_imdbId=pjmespatch(
                "props.pageProps.mainColumnData.series.series.id", raw_json
            ),
            series_title=pjmespatch(
                "props.pageProps.mainColumnData.series.series.originalTitleText.text",
                raw_json,
            ),
            series_title_localized=pjmespatch(
                "props.pageProps.mainColumnData.series.series.titleText.text", raw_json
            ),
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
    for title_data in pjmespatch(
        "props.pageProps.titleResults.results[].listItem", raw_json
    ):
        title.append(MovieBriefInfo.from_movie_search(title_data))
    people = []
    for person_data in pjmespatch(
        "props.pageProps.nameResults.results[].listItem", raw_json
    ):
        people.append(Person.from_search(person_data))

    res = SearchResult(titles=title, names=people)
    logger.info("Parsed search results: %s titles, %s names", len(title), len(people))
    return res


def parse_json_person_detail(raw_json) -> PersonDetail:
    logger.debug("Parsing person detail JSON")

    data = dict()
    data["imdbId"] = pjmespatch(
        "props.pageProps.aboveTheFold.id", raw_json
    )  # mainColumnData['id']
    data["id"] = pjmespatch("props.pageProps.mainColumnData.id", raw_json).replace(
        "nm", ""
    )
    data["imdb_id"] = data["id"]  # same as imdb_id
    data["name"] = pjmespatch("props.pageProps.aboveTheFold.nameText.text", raw_json)
    data["url"] = f"https://www.imdb.com/name/{data['imdbId']}/"
    data["knownfor"] = pjmespatch(
        "props.pageProps.mainColumnData.knownForFeatureV2.credits[*].title.titleText.text",
        raw_json,
    )

    if not data["knownfor"]:
        # fallback to old knownForFeature if knownForFeatureV2 is empty
        logger.debug("******** Falling back to old  knownForFeature path")
        data["knownfor"] = pjmespatch(
            "props.pageProps.mainColumnData.knownForFeature.edges[].node.title.titleText.text",
            raw_json,
        )

    data["knownfor2"] = pjmespatch(
        "props.pageProps.mainColumnData.knownForFeatureV2.credits[].[title.id,title.titleText.text,creditedRoles.edges[].node.text]",
        raw_json,
    )

    if not data["knownfor2"]:
        # fallback to old knownForFeature if knownForFeatureV2 is empty
        logger.debug("******** Falling back to old  knownForFeature2 path")
        data["knownfor2"] = pjmespatch(
            "props.pageProps.mainColumnData.knownForFeature.edges[].node.[title.id,title.titleText.text,credit.characters[].name]",
            raw_json,
        )

    data["image_url"] = pjmespatch(
        "props.pageProps.aboveTheFold.primaryImage.url", raw_json
    )
    data["bio"] = pjmespatch(
        "props.pageProps.aboveTheFold.bio.text.plainText", raw_json
    )
    data["height"] = pjmespatch(
        "props.pageProps.mainColumnData.height.displayableProperty.value.plainText",
        raw_json,
    )
    data["primary_profession"] = pjmespatch(
        "props.pageProps.aboveTheFold.primaryProfessions[].category.id", raw_json
    )
    data["birth_date"] = pjmespatch(
        "props.pageProps.aboveTheFold.birthDate.date", raw_json
    )
    data["birth_place"] = pjmespatch(
        "props.pageProps.mainColumnData.birthLocation.text", raw_json
    )
    data["death_date"] = pjmespatch(
        "props.pageProps.aboveTheFold.deathDate.date", raw_json
    )
    data["death_place"] = pjmespatch(
        "props.pageProps.mainColumnData.deathLocation.text", raw_json
    )
    data["death_reason"] = pjmespatch(
        "props.pageProps.mainColumnData.deathReason.text", raw_json
    )
    data["jobs"] = pjmespatch(
        "props.pageProps.mainColumnData.professions[*].professionCategory.linkedCreditCategory.categoryId",
        raw_json,
        _parse_jobs_v2,
    )

    if data["jobs"] is None:
        # fallback to old jobs path if professions is empty
        logger.debug("******** Falling back to old  jobs path")
        data["jobs"] = pjmespatch(
            "props.pageProps.mainColumnData.jobs[].category.id", raw_json
        )

    # Released credits v2
    data["credits"] = pjmespatch(
        "props.pageProps.mainColumnData.released.edges[].node",
        raw_json,
        _parse_credits_v2,
    )

    if not data["credits"]:
        # fallback to old credits path if released is empty
        logger.debug("******** Falling back to old  credits path")
        data["credits"] = pjmespatch(
            "props.pageProps.mainColumnData.releasedPrimaryCredits[].credits[].edges[].node[].[category.id,title.id,title.originalTitleText.text,title.titleType.id,title.primaryImage.url,title.releaseYear.year,titleGenres.genres[].genre.text]",
            raw_json,
            _parse_credits,
        )

    # Unreleased credits v2
    data["unreleased_credits"] = pjmespatch(
        "props.pageProps.mainColumnData.unreleased.edges[].node",
        raw_json,
        _parse_credits_v2,
    )

    if not data["unreleased_credits"]:
        # fallback to old unreleased credits path if unreleased is empty
        logger.debug("******** Falling back to old  unreleased credits path")
        data["credits"] = pjmespatch(
            "props.pageProps.mainColumnData.releasedPrimaryCredits[].credits[].edges[].node[].[category.id,title.id,title.originalTitleText.text,title.titleType.id,title.primaryImage.url,title.releaseYear.year,titleGenres.genres[].genre.text]",
            raw_json,
            _parse_credits,
        )

    person = PersonDetail.model_validate(data)
    logger.info("Parsed person %s", person.name)
    return person


def parse_json_season_episodes(raw_json) -> SeasonEpisodesList:
    series_imdbId = pjmespatch("props.pageProps.contentData.data.title.id", raw_json)
    current_season = pjmespatch(
        "props.pageProps.contentData.section.currentSeason", raw_json
    )
    top_rated_episode = pjmespatch(
        "props.pageProps.contentData.data.title.episodes.topRated.edges[0].node.ratingsSummary.aggregateRating",
        raw_json,
    )
    total_series_episodes = pjmespatch(
        "props.pageProps.contentData.data.title.episodes.totalEpisodes.total", raw_json
    )
    total_series_seasons = len(
        pjmespatch("props.pageProps.contentData.data.title.episodes.seasons", raw_json)
    )
    top_ten_episodes = pjmespatch(
        "props.pageProps.contentData.data.title.episodes.topTenEpisodes.edges[].[node.id,node.ratingsSummary.aggregateRating,node.ratingsSummary.voteCount]",
        raw_json,
        _dict_votes_,
    )
    logger.debug("Parsing episodes JSON")
    season_episodes = []
    for episode_data in pjmespatch(
        "props.pageProps.contentData.section.episodes.items", raw_json
    ):
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
    for episode_data in pjmespatch(
        "props.pageProps.searchResults.titleResults.titleListItems", raw_json
    ):
        all_episodes.append(BulkedEpisode.from_bulked_episode_data(episode_data))
    logger.info("Parsed %d bulked episodes", len(all_episodes))
    return all_episodes


def parse_json_akas(raw_json) -> AkasData:
    logger.debug("Parsing akas JSON")
    imdb_id = pjmespatch("id", raw_json)
    akas = [
        AkaInfo.from_data(*a)
        for a in pjmespatch(
            "akas.edges[].node[].[title, country.code,country.name, language.code, language.name]",
            raw_json,
        )
    ]
    return AkasData(imdbId=imdb_id, akas=akas)


def parse_json_trivia(raw_json: dict) -> List[Any]:
    trivia_edges = pjmespatch("trivia.edges[]", raw_json)
    trivia_list = []
    for node in [edge.get("node", {}) for edge in trivia_edges]:
        trivia_item = {
            # "id": node.get("id"),
            "body": node.get("displayableArticle", {}).get("body", {}).get("plaidHtml"),
            "interestScore": node.get("interestScore", {}),
        }
        trivia_list.append(trivia_item)
    return trivia_list


def parse_json_reviews(raw_json: dict) -> List[Any]:
    reviews_edges = pjmespatch("reviews.edges[]", raw_json)
    reviews_list = []
    for edge in reviews_edges:
        review_item = {
            "spoiler": pjmespatch("node.spoiler", edge),
            "summary": pjmespatch("node.summary.originalText", edge),
            "text": pjmespatch("node.text.originalText.plaidHtml", edge),
            "authorRating": pjmespatch("node.authorRating", edge),
            "downVotes": pjmespatch("node.helpfulness.downVotes", edge),
            "upVotes": pjmespatch("node.helpfulness.upVotes", edge),
        }
        reviews_list.append(review_item)
    return reviews_list


def parse_json_filmography(raw_json) -> Dict[str, List[MovieBriefInfo]]:
    filmography_edges = pjmespatch("credits.edges[].node", raw_json)
    if not filmography_edges:
        return {}
    credits_by_job = {}
    for edge in filmography_edges:
        jobid = pjmespatch("category.id", edge)
        credits_by_job.setdefault(jobid, []).append(
            MovieBriefInfo.from_filmography(pjmespatch("title", edge))
        )
    return credits_by_job
