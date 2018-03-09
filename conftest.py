def pytest_addoption(parser):
    parser.addoption(
        "--emails",
        action="store_true",
        help="run tests retrieving email addresses (access will be logged on the server)"
    )
