from collections import namedtuple

import pytest
import requests

import attendees

User = namedtuple("User", "username,name")


TEST_USERS = [
    User(username="timtroendle", name="Tim Tröndle"),
    User(username="tom_brown", name="Tom Brown")
]

VALID_IMAGE_MIME_TYPES = ["image/png", "image/jpeg"]


@pytest.fixture(params=TEST_USERS)
def user(request):
    return request.param


def test_returns_name(variables, user):
    users = attendees.attendee_list(
        usernames=[user.username],
        api_username=variables["api_username"],
        api_key=variables["api_key"]
    )
    assert users.loc[user.username, "name"] == user.name


def test_returns_username_as_index(variables, user):
    users = attendees.attendee_list(
        usernames=[user.username],
        api_username=variables["api_username"],
        api_key=variables["api_key"]
    )
    assert user.username in users.index


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
