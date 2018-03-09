"""Tests the script that retrieves user information.

The script is tested on the live instance through retrieving actual data. Tests
can hence easily break, whenever (1) there is no internet connection, (2) the
forum is unavailable, (3) test data on the server has changed. In the latter
case, update the TEST_USERS data manually to match the information on the server.
"""
from collections import namedtuple

import pytest
import requests

import attendees

User = namedtuple("User", "username,name,location,website,bio,affiliation")


TEST_USERS = [
    User(
        username="timtroendle",
        name="Tim Tröndle",
        location="Zürich",
        website="http://www.rep.ethz.ch/people/person-detail.html?persid=240778",
        bio="PhD researcher in the Renewable Energy Policy group at ETH Zürich",
        affiliation="ETH Zürich"
    ),
    User(
        username="tom_brown",
        name="Tom Brown",
        location="",
        website="https://www.nworbmot.org/",
        bio="",
        affiliation=""
    )
]

VALID_IMAGE_MIME_TYPES = ["image/png", "image/jpeg"]


@pytest.fixture(params=TEST_USERS)
def user(request):
    return request.param


def test_returns_username_as_index(variables, user):
    users = attendees.attendee_list(
        usernames=[user.username],
        api_username=variables["api_username"],
        api_key=variables["api_key"]
    )
    assert user.username in users.index


@pytest.mark.parametrize("parameter", [
    "name",
    "location",
    "website",
    "bio",
    "affiliation"
])
def test_returns_parameter(variables, user, parameter):
    users = attendees.attendee_list(
        usernames=[user.username],
        api_username=variables["api_username"],
        api_key=variables["api_key"]
    )
    assert users.loc[user.username, parameter] == user.__getattribute__(parameter)


def test_returns_avatar_url(variables, user):
    users = attendees.attendee_list(
        usernames=[user.username],
        api_username=variables["api_username"],
        api_key=variables["api_key"]
    )
    avatar_url = users.loc[user.username, "avatar_url"]
    assert _valid_image_url(avatar_url)
    assert user.username in avatar_url


def _valid_image_url(url):
    r = requests.get(url)
    return r.status_code == 200 and r.headers['content-type'] in VALID_IMAGE_MIME_TYPES
