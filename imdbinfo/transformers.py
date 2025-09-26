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

import datetime


def _release_date(result: dict):
    """
    given a list of lists, convert it to a string with format 'YYYY-MM-DD'
    """
    if result is None:
        return None
    return datetime.date(
        result.get("year") or 1, result.get("month") or 1, result.get("day") or 1
    ).strftime("%Y-%m-%d")


def _dict_votes_(result):
    """
    given a list of lists, convert it to a dict with imdbId as key and (rating, votes) as value
    """
    if result is None:
        return []
    res = []
    for item in result:
        imdbId = item[0]  # 'tt1234567'
        rating = item[1]  # rating value, e.g. 8.5
        votes = item[2]  # votes count, e.g. 123456
        res.append({"imdbId": imdbId, "rating": rating, "votes": votes})
    return res


def _none_to_string_in_list(result):
    """
    given a list of lists , if a None is found replace with '' recursively
    """
    return [
        [str(item) if item is not None else "" for item in sublist]
        for sublist in result
    ]


def _join(result, separator=" "):
    if result is None:
        return None
    return separator.join(map(str, result)) if isinstance(result, list) else str(result)


def _certificates_to_dict(result):
    """
    given a list of lists, convert it to a dict with country id as key and (country text, rating) as value
    """
    # ['CA', 'Canada', '14', ['New Brunswick', 'Nova Scotia', 'Prince Edward Island']]
    # ['CA', 'Canada', '16', ['Manitoba']]
    if result is None:
        return {}
    res = {}
    for item in result:
        cert_id, country_code, country_name, rating_value, rating_reason, regions = item
        rating = f"{rating_value} " + ", ".join(regions)
        if country_code not in res:
            res[country_code] = [country_name, rating]
        else:
            res[country_code][1] += " :: " + rating
    return res


def _parse_mpaa(mpaa_certificate_node):
    if mpaa_certificate_node is None:
        return ""
    for certificate in mpaa_certificate_node:
        if certificate.get("node", {}).get("ratingsBody", {}).get("id") == "MPAA":
            return certificate.get("node", {}).get("ratingReason", "")
    return ""
