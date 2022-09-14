from argparse import ArgumentParser

from .fourier import add_fourier_parser

PARSERS_TO_ADD = [add_fourier_parser]


def main():
    parser = ArgumentParser(description="Script for running various qbench subcommands.")

    commands = parser.add_subparsers()

    for add_parser in PARSERS_TO_ADD:
        add_parser(commands)

    args = parser.parse_args()  # noqa

    # Do something with parsed args
