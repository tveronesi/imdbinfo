import json
import logging
import re

import pytest

import imdbinfo
from imdbinfo import CreditRole, get_filmography, services
from imdbinfo.exceptions import GraphQLError


@pytest.fixture
def graphql_requests(monkeypatch):
    requests = []
    services._get_extended_name_info.cache_clear()

    def request(headers, person_id, payload, url):
        requests.append((headers, person_id, payload, url))
        match = re.search(r"categories:\s*(\[[^\]]*\])", payload["query"])
        assert match is not None
        roles = json.loads(match.group(1))
        edges = [
            {
                "node": {
                    "category": {"id": role},
                    "title": {
                        "id": "tt0133093",
                        "titleText": {"text": "The Matrix"},
                        "originalTitleText": {"text": "The Matrix"},
                        "releaseYear": {"year": 1999},
                    },
                }
            }
            for role in roles
        ]
        return {"data": {"name": {"credits": {"edges": edges}}}}

    monkeypatch.setattr(services, "request_graphql_url", request)
    yield requests
    services._get_extended_name_info.cache_clear()


def requested_roles(request):
    match = re.search(r"categories:\s*(\[[^\]]*\])", request[2]["query"])
    assert match is not None
    return json.loads(match.group(1))


def test_credit_role_is_public():
    assert imdbinfo.CreditRole is CreditRole
    assert "CreditRole" in imdbinfo.__all__
    assert CreditRole.ACTOR.value == "actor"
    assert CreditRole("director") is CreditRole.DIRECTOR


def test_credit_role_defines_supported_categories():
    expected = {
        "production_designer", "casting_department", "director", "composer",
        "casting_director", "executive", "art_director", "actress",
        "costume_designer", "writer", "camera_department", "art_department",
        "publicist", "cinematographer", "location_management", "soundtrack",
        "sound_department", "talent_agent", "set_decorator",
        "animation_department", "make_up_department", "costume_department",
        "script_department", "producer", "stunts", "editor",
        "stunt_coordinator", "special_effects", "assistant_director",
        "editorial_department", "music_department", "transportation_department",
        "actor", "visual_effects", "production_manager",
    }

    assert set(CreditRole.__members__) == {name.upper() for name in expected}
    assert {role.value for role in CreditRole} == expected
    for role in CreditRole:
        assert role.name == role.value.upper()
        assert isinstance(role, str)
        assert CreditRole(role.value) is role
        assert json.loads(json.dumps(role)) == role.value

    with pytest.raises(ValueError):
        CreditRole("not_a_role")


@pytest.mark.parametrize(
    "roles",
    [
        [CreditRole.ACTOR, CreditRole.DIRECTOR],
        ["actor", "director"],
        [CreditRole.ACTOR, "director"],
        ("actor", "director"),
    ],
)
def test_filmography_selected_roles_are_sent_and_parsed(graphql_requests, roles):
    result = get_filmography("nm0000206", locale="es", roles=roles)

    assert requested_roles(graphql_requests[0]) == ["actor", "director"]
    assert graphql_requests[0][0]["x-imdb-user-country"] == "ES"
    assert graphql_requests[0][1] == "nm0000206"
    assert 'name(id: "nm0000206")' in graphql_requests[0][2]["query"]
    assert set(result) == {"actor", "director"}
    assert result["actor"][0].imdbId == "tt0133093"
    assert result["director"][0].year == 1999


def test_filmography_default_roles(graphql_requests):
    result = get_filmography("nm0000206", locale="es")

    assert requested_roles(graphql_requests[0]) == [
        "actor", "actress", "cinematographer", "director", "writer", "composer"
    ]
    assert set(result) == set(requested_roles(graphql_requests[0]))


@pytest.mark.parametrize("role", list(CreditRole))
def test_filmography_accepts_every_credit_role(graphql_requests, role):
    result = get_filmography("nm0000206", roles=[role])

    assert requested_roles(graphql_requests[0]) == [role.value]
    assert set(result) == {role.value}
    assert get_filmography("nm0000206", roles=[role.value]) == result
    assert len(graphql_requests) == 1


@pytest.mark.parametrize(
    ("roles", "warning"),
    [
        ([], "No filmography roles selected"),
        (["not_a_role"], "roles are not valid"),
        ([CreditRole.ACTOR, "invalid"], "roles are not valid"),
    ],
)
def test_filmography_invalid_roles_warn_without_request(
    graphql_requests, caplog, roles, warning
):
    with caplog.at_level(logging.WARNING, logger="imdbinfo.services"):
        assert get_filmography("nm0000206", roles=roles) == {}
    assert warning in caplog.text
    assert graphql_requests == []


def test_filmography_cache_uses_person_locale_and_role_values(graphql_requests):
    first = get_filmography("nm0000206", locale="es", roles=[CreditRole.ACTOR])
    repeated = get_filmography("0000206", locale="es", roles=["actor"])
    assert first["actor"][0].imdbId == repeated["actor"][0].imdbId
    assert len(graphql_requests) == 1

    director = get_filmography("nm0000206", locale="es", roles=[CreditRole.DIRECTOR])
    assert set(director) == {"director"}
    get_filmography("nm0000206", locale="fr", roles=["actor"])
    get_filmography("nm0000207", locale="es", roles=["actor"])
    assert len(graphql_requests) == 4
    assert [requested_roles(request) for request in graphql_requests] == [
        ["actor"], ["director"], ["actor"], ["actor"]
    ]
    assert graphql_requests[2][0]["x-imdb-user-country"] == "FR"
    assert graphql_requests[3][1] == "nm0000207"


def test_filmography_cache_tracks_mutated_role_list(graphql_requests):
    roles = [CreditRole.ACTOR]
    assert set(get_filmography("nm0000206", roles=roles)) == {"actor"}
    roles.append(CreditRole.DIRECTOR)
    assert set(get_filmography("nm0000206", roles=roles)) == {"actor", "director"}
    roles.pop()
    assert set(get_filmography("nm0000206", roles=roles)) == {"actor"}
    assert [requested_roles(request) for request in graphql_requests] == [
        ["actor"], ["actor", "director"]
    ]


def test_filmography_default_and_explicit_main_roles_share_cache(graphql_requests):
    get_filmography("nm0000206")
    get_filmography(
        "nm0000206",
        roles=[
            CreditRole.ACTOR, CreditRole.ACTRESS, CreditRole.CINEMATOGRAPHER,
            CreditRole.DIRECTOR, CreditRole.WRITER, CreditRole.COMPOSER,
        ],
    )
    assert len(graphql_requests) == 1


def test_filmography_graphql_errors_propagate(monkeypatch):
    services._get_extended_name_info.cache_clear()

    def fail(*args):
        raise GraphQLError("GraphQL failure", url=args[3], query_term=args[1])

    monkeypatch.setattr(services, "request_graphql_url", fail)
    with pytest.raises(GraphQLError, match="GraphQL failure"):
        get_filmography("nm0000206", roles=[CreditRole.ACTOR])
    services._get_extended_name_info.cache_clear()
