# attendee-list

A simple script to create a list of workshop attendees based on Discourse user profiles.

## User Guide

### Installation

Install the requirements with `conda` or `pip`.

    $ conda install --file requirements

or

    $ pip install requirements

## Developer Guide

### Installation

Install the test requirements with `conda` or `pip`.

    $ conda install --file test-requirements

or

    $ pip install test-requirements

### Run the test suite

First you will need a credentials file with Discourse credentials.

```yaml
# credentials.yaml
api_username: "<your-username>"
api_key: "<api_key>"
```

Then, run the test suite with py.test:

    $ py.test --variables credentials.yaml
