# attendees-list

Some scripts to deal with users and groups of users on the [openmod discussion forum](https://forum.openmod-initiative.org/). Can build a workshop booklet with an overview over all attendees of the workshop.

## User Guide

### Installation

Install the requirements with `conda`.

    $ conda install --file requirements.txt

You can now see what you can do:

    $ python attendees.py --help
    $ python booklet.py --help

Here are some things you might want to do:

### Fill group on the forum with users

```text
# usernames.txt
john_doe
jane_doe
```

    $ python attendees.py usernames.txt group-name

### Build conference attendee booklet from a group on the forum

```yaml
# booklet.yml
title: "My amazing workshop"
subtitle: "Date, Location"
```

    $ python attendees.py group <group-name> | python attendees.py retrieve | python booklet.py build booklet.yml > booklet.html


### Randomly allocate conference attendees to rooms

    $ python attendees.py group <group-name> | python attendees.py name | python allocate.py random_allocation room1 room2 | python allocate.py html > allocation.html

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
