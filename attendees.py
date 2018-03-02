import pandas as pd
import requests


URL = "https://forum.openmod-initiative.org/"
AVATAR_URL = "https://forum.openmod-initiative.org/user_avatar/forum.openmod-initiative.org/{}/120/8_1.png"

USER_REQUEST = URL + "users/{}.json?"


def attendee_list(usernames, api_username, api_key):
    users = [_get_user(username, api_username, api_key) for username in usernames]
    return pd.DataFrame(
        index=[user["user"]["username"] for user in users],
        data={
            "name": [user["user"]["name"] for user in users],
            "avatar_url": [AVATAR_URL.format(username) for username in usernames]
        }
    )


def _get_user(username, api_username, api_key):
    r = requests.get(USER_REQUEST.format(username), auth=(api_username, api_key))
    r.raise_for_status()
    return r.json()
