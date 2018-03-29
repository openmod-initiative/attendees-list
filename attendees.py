from pathlib import Path
import yaml

import click
import pandas as pd
import requests

PATH_TO_CREDENTIALS = Path("./credentials.yaml")

URL = "https://forum.openmod-initiative.org/"
AVATAR_URL = "https://forum.openmod-initiative.org/user_avatar/forum.openmod-initiative.org/{}/120/8_1.png"
USER_FIELD_AFFILIATION = '3' # user fields don't have names in the api, but only numbers

USER_REQUEST = URL + "users/{}.json?"
ALL_USERS_REQUEST = URL + "admin/users/list/active.json?show_emails=true&api_key={}&api_username={}"


@click.group()
def attendees():
    pass # this defines the top level click command


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


@attendees.command()
@click.argument("usernames", type=Usernames())
@click.argument("output", type=click.Path(exists=False, file_okay=True, dir_okay=False))
@click.option('--emails/--no-emails', default=False,
              help="retrieve email addresses (credentials necessary and access will be logged)")
def retrieve(usernames, output, emails):
    """Retrieves user details from the openmod Discourse forum.

    To retrieve emails, a credential file with your api_username and api_key must exist
    in the same folder having the name 'credentials.yaml'.

    \b
    The following parameters are read:
    * name
    * avatar_url
    * location
    * website
    * bio
    * affiliation

    \b
    Parameters:
        * USERNAMES: path to a text file with Discourse usernames, one username per line
        * OUTPUT: path to a file into which the user details will be written.
    """
    if emails:
        credentials = _read_credentials()
    else:
        credentials = {"api_key": None, "api_username": None}
    attendees = attendee_list(
        usernames=usernames,
        api_username=credentials["api_username"],
        api_key=credentials["api_key"],
        retrieve_emails=emails
    )
    attendees.to_csv(output)


def attendee_list(usernames, api_username=None, api_key=None, retrieve_emails=False):
    if retrieve_emails and not (api_username and api_key):
        raise ValueError("To retrieve emails, 'api_username' and 'api_key' must be provided.")
    users = [_get_user(username) for username in usernames]
    users = pd.DataFrame(
        index=[user["user"]["username"] for user in users],
        data={
            "name": [user["user"]["name"] for user in users],
            "avatar_url": [AVATAR_URL.format(username) for username in usernames],
            "location": [user["user"]["location"] if "location" in user["user"].keys() else ""
                         for user in users],
            "website": [user["user"]["website"] if "website" in user["user"].keys() else ""
                        for user in users],
            "bio": [user["user"]["bio_raw"] if "bio_raw" in user["user"].keys() else ""
                    for user in users],
            "affiliation": [user["user"]["user_fields"][USER_FIELD_AFFILIATION]
                            for user in users]
        }
    ).fillna("")
    if retrieve_emails:
        users["email"] = _retrieve_emails(usernames, api_username, api_key)
    return users


def _get_user(username):
    r = requests.get(USER_REQUEST.format(username))
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


def _retrieve_emails(usernames, api_username, api_key):
    assert api_username
    assert api_key
    r = requests.get(ALL_USERS_REQUEST.format(api_key, api_username))
    r.raise_for_status()
    all_users = r.json()
    all_addresses = pd.Series(
        index=[user["username"] for user in all_users],
        data=[user["email"] for user in all_users]
    )
    return all_addresses.reindex(usernames)


if __name__ == "__main__":
    attendees()
