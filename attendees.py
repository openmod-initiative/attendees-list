from itertools import count
from pathlib import Path
import yaml

import click
import pandas as pd
import requests

PATH_TO_CREDENTIALS = Path("./credentials.yaml")

URL = "https://forum.openmod-initiative.org/"
AVATAR_URL = "https://forum.openmod-initiative.org/user_avatar/forum.openmod-initiative.org/{}/500/8_1.png"
USER_FIELD_AFFILIATION = '3' # user fields don't have names in the api, but only numbers

USER_REQUEST = URL + "users/{}.json?"
ALL_USERS_REQUEST = URL + "directory_items.json?period=all&order=days_visited&page={}"
ALL_USERS_WITH_EMAIL_REQUEST = URL + "admin/users/list/active.json?show_emails=true&api_username={}&api_key={}"
ALL_GROUPS_REQUEST = URL + "groups/search.json?api_username={}&api_key={}"
ADD_USER_REQUEST = URL + "groups/{}/members.json?api_username={}&api_key={}"


@click.group()
def attendees():
    """Tool to handle attendees of openmod workshops managed on the discourse discussion forum."""
    pass # this defines the top level click command


class Usernames(click.Path):
    """A username file parameter on the command line."""
    name = "usernames"

    def __init__(self, invalid_ok=False):
        super().__init__(dir_okay=False, exists=True)
        self.__invalid_ok = invalid_ok

    def convert(self, value, param, ctx):
        path_to_file = Path(super().convert(value, param, ctx))
        with path_to_file.open('r') as f_username:
            usernames = [username.strip() for username in f_username.readlines()]
        if not self.__invalid_ok:
            non_existing_usernames = check_usernames(usernames)
            if non_existing_usernames:
                msg = "Some usernames do not exist.\nInvalid names are:\n"
                self.fail(msg + "\n".join(non_existing_usernames))
        return usernames


class GroupName(click.ParamType):
    """The name of a group on the discussion forum."""
    name = "group_name"

    def convert(self, value, param, ctx):
        if " " in value:
            self.fail("Invalid group name. Discourse group names cannot contain spaces. "
                      "You might have entered the 'full name' of the group.")
        return value


@attendees.command()
@click.argument("usernames", type=Usernames(invalid_ok=True))
def check(usernames):
    """Check a list of usernames.

    Prints a list of non existing usernames.
    """
    non_existing_usernames = check_usernames(usernames)
    if not non_existing_usernames:
        print("All usernames exist.")
    else:
        print("The following usernames do not exist:")
        for username in non_existing_usernames:
            print(username)


@attendees.command()
@click.argument("usernames", type=Usernames(invalid_ok=False))
@click.argument("output", type=click.Path(exists=False, file_okay=True, dir_okay=False))
@click.option('--emails/--no-emails', default=False,
              help="retrieve email addresses (credentials necessary and access will be logged)")
def retrieve(usernames, output, emails):
    """Retrieve user details.

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


@attendees.command()
@click.argument("usernames", type=Usernames(invalid_ok=False))
@click.argument("group_name", type=GroupName())
def add(usernames, group_name):
    """Add users to group.

    To add users, a credential file with your api_username and api_key must exist
    in the same folder having the name 'credentials.yaml'.

    \b
    Parameters:
        * USERNAMES: path to a text file with Discourse usernames, one username per line
        * GROUP_NAME: name of the group to which users shall be added
    """
    credentials = _read_credentials()
    group_id = _group_name_to_id(group_name, credentials["api_username"], credentials["api_key"])
    r = requests.put(
        ADD_USER_REQUEST.format(group_id, credentials["api_username"], credentials["api_key"]),
        data={"usernames": ",".join(usernames)}
    )
    if r.status_code == 422:
        print("Adding users failed. Some of the given users might already exist in the group. You should: ")
        print("(1) delete them in your text file, OR")
        print("(2) delete them in the group online, OR")
        print("(3) give up and try Discourse's bulk add feature instead.")
    else:
        r.raise_for_status()
        print("Added all users.")


def check_usernames(usernames):
    """Returns all usernames that do not exist."""
    items = []
    for page_number in count(start=0): # results are provided in several pages
        r = requests.get(ALL_USERS_REQUEST.format(page_number))
        r.raise_for_status()
        items_on_page = r.json()["directory_items"]
        if not items_on_page:
            break
        else:
            items.extend(items_on_page)
    existing_usernames = [item["user"]["username"].lower() for item in items]
    return [username for username in usernames if username.lower() not in existing_usernames]


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
    r = requests.get(ALL_USERS_WITH_EMAIL_REQUEST.format(api_username, api_key))
    r.raise_for_status()
    all_users = r.json()
    all_addresses = pd.Series(
        index=[user["username"] for user in all_users],
        data=[user["email"] for user in all_users]
    )
    return all_addresses.reindex(usernames)


def _group_name_to_id(group_name, api_username, api_key):
    assert api_username
    assert api_key
    r = requests.get(ALL_GROUPS_REQUEST.format(api_username, api_key))
    r.raise_for_status()
    all_groups = r.json()
    name_to_id = {group["name"]: group["id"] for group in all_groups}
    if group_name not in name_to_id.keys():
        raise ValueError("Group {} does not exist.".format(group_name))
    else:
        return name_to_id[group_name]


if __name__ == "__main__":
    attendees()
