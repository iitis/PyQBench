def pytest_addoption(parser):
    parser.addoption(
        "--rigetti",
        action="store_true",
        dest="rigetti",
        default=False,
        help=(
            "Enable validation tests on actual Rigetti devices. "
            "Note that to run these tests you need to have AWS CLI configured."
        ),
    )
