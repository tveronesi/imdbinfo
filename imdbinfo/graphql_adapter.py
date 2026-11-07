"""Adapt a GraphQL ``title`` payload to the ``__NEXT_DATA__`` shape read by ``parse_json_movie``."""

from typing import Any, Dict, List

from .parsers import OldCategoryIdToNewCategoryIdObject

_CAST_CATEGORIES = {"actor", "actress", "self", "archive_footage", "archive_sound"}


def _edges(node: Any) -> List[dict]:
    return [e["node"] for e in ((node or {}).get("edges") or []) if e.get("node")]


def _credit_sections(credits: Any) -> List[dict]:
    """Group flat GraphQL credits into the ``categories`` sections of the HTML page."""
    sections: Dict[str, dict] = {}
    for node in _edges(credits):
        name = node.get("name") or {}
        category = node.get("category") or {}
        if not name.get("id") or not category.get("id"):
            continue
        is_cast = node.get("__typename") == "Cast" or category["id"] in _CAST_CATEGORIES
        attributes = [a["text"] for a in (node.get("attributes") or []) if a.get("text")]
        jobs = [j["text"] for j in (node.get("jobs") or []) if j.get("text")]
        item = {
            "id": name["id"],
            "rowTitle": (name.get("nameText") or {}).get("text", ""),
            "isCast": is_cast,
            "characters": [c["name"] for c in (node.get("characters") or []) if c.get("name")],
            "attributes": f"({', '.join(attributes)})" if attributes else None,
            "jobs": jobs,
        }
        section = sections.setdefault(
            category["id"],
            {"id": category["id"], "name": category.get("text", ""), "section": {"items": []}},
        )
        section["section"]["items"].append(item)
    return list(sections.values())


def _directors_group(credits: Any) -> List[dict]:
    seen, people = set(), []
    for node in _edges(credits):
        name = node.get("name") or {}
        if (node.get("category") or {}).get("id") == "director" and name.get("id") not in seen:
            seen.add(name.get("id"))
            people.append({"name": name})
    if not people:
        return []
    return [
        {
            "grouping": {"groupingId": OldCategoryIdToNewCategoryIdObject["director"]},
            "credits": people,
        }
    ]


def _company_categories(company_credits: Any) -> List[dict]:
    grouped: Dict[str, dict] = {}
    for node in _edges(company_credits):
        category = node.get("category") or {}
        if not category.get("id"):
            continue
        group = grouped.setdefault(
            category["id"],
            {"category": {"id": category["id"], "text": category.get("text")}, "companyCredits": {"edges": []}},
        )
        group["companyCredits"]["edges"].append({"node": node})
    return list(grouped.values())


def _prestigious_award(summary: Any):
    if not summary:
        return None
    award = ((summary.get("awardNomination") or {}).get("award")) or {}
    return {
        "wins": summary.get("wins", 0),
        "nominations": summary.get("nominations", 0),
        "award": {"text": award.get("text", "")},
    }


def graphql_title_to_next_data(title: dict) -> dict:
    """Return ``{"props": {"pageProps": {...}}}`` built from a GraphQL ``title`` object."""
    company_categories = _company_categories(title.get("companyCredits"))
    production = [
        {"node": n}
        for n in _edges(title.get("companyCredits"))
        if (n.get("category") or {}).get("id") == "production"
    ]
    keywords = [
        {"node": {"text": ((n.get("keyword") or {}).get("text") or {}).get("text")}}
        for n in _edges(title.get("keywords"))
    ]

    main = {"akas": {"edges": []}, "filmingLocations": {"edges": []}, **title}
    episodes = dict(title.get("episodes") or {})
    for key in ("displayableYears", "displayableSeasons"):
        if episodes.get(key):
            episodes[key] = {"edges": list(reversed(episodes[key].get("edges") or []))}
    main["episodes"] = episodes or None
    main.update(
        {
            "countriesDetails": title.get("countriesOfOrigin"),
            "storylineKeywords": {"edges": keywords},
            "production": {"edges": production},
            "companyCreditCategories": company_categories,
            "categories": _credit_sections(title.get("credits")),
            "crewV2": _directors_group(title.get("credits")),
            "prestigiousAwardSummary": _prestigious_award(title.get("prestigiousAwardSummary")),
        }
    )
    above = {
        "originalTitleText": title.get("originalTitleText"),
        "titleText": title.get("titleText"),
        "primaryImage": title.get("primaryImage"),
        "releaseYear": title.get("releaseYear"),
        "runtime": title.get("runtime"),
    }
    return {"props": {"pageProps": {"mainColumnData": main, "aboveTheFoldData": above}}}
