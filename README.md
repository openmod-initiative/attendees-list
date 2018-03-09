# attendee-list

A simple script to create a list of workshop attendees based on Discourse user profiles.

## User Guide

### Installation

Install the requirements with `conda`.

    $ conda install --file requirements.txt

### Retrieve users from Discourse

First you will need a credentials file with Discourse credentials.

```yaml
# credentials.yaml
api_username: "<your-username>"
api_key: "<api_key>"
```

Second, you will need to create a text file containing the list of usernames like so:

```
# usernames.txt
user1
user2
user14
```

Then you can retrieve the user details with:

    $ python attendees.py <path-to-usernames> <path-to-output>

## Developer Guide

### Installation

Install the test requirements with `conda`.

    $ conda install --file test-requirements.txt

### Run the test suite

Make sure you have the credentials file as described above.

Then, run the test suite with py.test:

    $ py.test --variables credentials.yaml

Tests are accessing the live instance and are asserting certain data to be available on that instance. They can hence fail for three reasons unrelated to this script:

1) no internet connection available,
2) the forum is unavailable for other reasons,
3) data assumed on the forum has changed.

Should tests fail, make sure these are not the reasons.
