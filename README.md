# attendee-list

A simple script to create a list of workshop attendees based on Discourse user profiles.

## User Guide

### Installation

Install the requirements with `conda`.

    $ conda install --file requirements.txt

You can now see what you can do:

    $ python attendees.py --help

### Retrieve users from Discourse

First, you will need to create a text file containing the list of usernames like so:

```
# usernames.txt
user1
user2
user14
```

Then you can retrieve the user details with:

    $ python attendees.py retrieve <path-to-usernames> <path-to-output>


### Retrieve users including email addresses from Discourse

In addition to the username list you will need a credentials file with Discourse credentials.

```yaml
# credentials.yaml
api_username: "<your-username>"
api_key: "<api_key>"
```

Then you can retrieve the user details including email addresses with the following command. Your access will be logged on the server side.

    $ python attendees.py retrieve --emails <path-to-usernames> <path-to-output>

## Developer Guide

### Installation

Install the test requirements with `conda`.

    $ conda install --file requirements-test.txt

### Run the test suite

To run all test, you will need the credential file as described above. Then run them like so:

    $ py.test --variables credentials.yaml

Some tests will retrieve email addresses from the forum, an activity that is logged online. To run these tests as well, type:

    $ py.test --emails --variables credentials.yaml

Tests are accessing the live instance and are asserting certain data to be available on that instance. They can hence fail for three reasons unrelated to this script:

1) no internet connection available,
2) the forum is unavailable for other reasons,
3) data assumed on the forum has changed.

Should tests fail, make sure these are not the reasons.
