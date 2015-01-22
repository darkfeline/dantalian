"""
Main script argument parser.
"""

import argparse

from . import commands


def make_parser():

    """Make argument parser for main script.

    Argument parser is reusable, so keep the parser around instead of remaking
    it.

    You can use it to parse and run an argument list like so:

        >>> parser = make_parser()
        >>> args = parser.parse_args(['tag', 'foo', 'bar'])
        >>> args.func(args)
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')

    subparsers = parser.add_subparsers(title='Commands')

    for cmd in commands.COMMANDS:
        getattr(commands, cmd).add_parser(subparsers)

    return parser
