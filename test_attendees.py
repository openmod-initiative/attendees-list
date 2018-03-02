from collections import namedtuple

import pytest

import attendees

User = namedtuple("User", "username,name")


TEST_USERS = [
    User(username="timtroendle", name="Tim Tröndle"),
    User(username="tom_brown", name="Tom Brown")
]


@pytest.fixture(params=TEST_USERS)
def user(request):
    return request.param


def test_returns_name(variables, user):
    users = attendees.attendee_list(
        usernames=[user.username],
        api_username=variables["api_username"],
        api_key=variables["api_key"]
    )
    assert user.name in users["name"].values


def test_returns_username(variables, user):
    users = attendees.attendee_list(
        usernames=[user.username],
        api_username=variables["api_username"],
        api_key=variables["api_key"]
    )
    assert user.username in users["username"].values
