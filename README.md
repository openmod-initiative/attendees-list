# attendee-list

A simple script to create a list of workshop attendees based on Discourse user profiles.

## Developer Guide

### Installation

You will need ``pytest`` and its ``pytest-variables`` extension.

    $ pip install pytest
    $ pip install pytest-variables[yaml]

### Run the test suite

First you will need a credentials file with Discourse credentials.

```yaml
# credentials.yaml
api_username: "<your-username>"
api_key: "<api_key>"
```

Then, run the test suite with py.test:

    $ py.test --variables credentials.yaml
