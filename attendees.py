from pathlib import Path
import yaml

import click
import pandas as pd
import requests

PATH_TO_CREDENTIALS = Path("./credentials.yaml")

URL = "https://forum.openmod-initiative.org/"
AVATAR_URL = "https://forum.openmod-initiative.org/user_avatar/forum.openmod-initiative.org/{}/120/8_1.png"

USER_REQUEST = URL + "users/{}.json?"


class Usernames(click.Path):
    """A username file parameter on the command line."""
    name = "usernames"

    def __init__(self):
        super().__init__(dir_okay=False, exists=True)

    def convert(self, value, param, ctx):
        path_to_file = Path(super().convert(value, param, ctx))
        if not path_to_file.exists():
            raise ValueError("Username list {} does not exist.".format(path_to_file))
        with path_to_file.open('r') as f_username:
            usernames = [username.strip() for username in f_username.readlines()]
        if not all(" " not in username for username in usernames):
            raise ValueError("Usernames cannot contain spaces.")
        return usernames


@click.command()
@click.argument("usernames", type=Usernames())
@click.argument("output", type=click.Path(exists=False, file_okay=True, dir_okay=False))
def retrieve_attendees(usernames, output):
    """Retrieves user details from the openmod Discourse forum.

    A credential file with your api_username and api_key must exist in the same folder
    having the name 'credentials.yaml'.

    \b
    Parameters:
        * USERNAMES: path to a text file with Discourse usernames, one username per line
        * OUTPUT: path to a file into which the user details will be written.
    """
    credentials = _read_credentials()
    attendees = attendee_list(
        usernames=usernames,
        api_username=credentials["api_username"],
        api_key=credentials["api_key"]
    )
    attendees.to_csv(output)


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


def _read_credentials():
    if not PATH_TO_CREDENTIALS.exists():
        msg = "{} file does not exist.".format(PATH_TO_CREDENTIALS.absolute())
        raise IOError(msg)
    with PATH_TO_CREDENTIALS.open('r') as credentials_file:
        credentials = yaml.load(credentials_file)
    if "api_key" not in credentials.keys() or "api_username" not in credentials.keys():
        msg = "Credentials file must contain 'api_key' and 'api_username'."
        raise IOError(msg)
    return credentials


if __name__ == "__main__":
    retrieve_attendees()
