"""Command line interface for qbench package."""
from argparse import ArgumentParser

from .fourier import add_fourier_parser
from .logging import configure_logging

PARSERS_TO_ADD = [add_fourier_parser]


def main(args=None):
    """Entry point of the CLI."""
    configure_logging()
    parser = ArgumentParser(description="Script for running various qbench subcommands.")

    commands = parser.add_subparsers()

    for add_parser in PARSERS_TO_ADD:
        add_parser(commands)

    args = parser.parse_args(args)  # noqa

    args.func(args)
