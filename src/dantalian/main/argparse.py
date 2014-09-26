"""
Main script argument parser.
"""

import argparse

from . import commands


def make_parser():

    """Make argument parser for main script."""

    parser = argparse.ArgumentParser()
    parser.add_argument('--log', metavar='LOGFILE')
    parser.set_defaults(func=lambda x: parser.print_help())

    subparsers = parser.add_subparsers(title='Commands')

    # tag
    tmp_parser = subparsers.add_parser(
        'tag',
        usage='''%(prog)s FILE TAG
            %(prog)s TAG -f FILE [FILE ...]
            %(prog)s FILE -t TAG [TAG ...]
            %(prog)s -f FILE [FILE ...] -t TAG [TAG ...]
            %(prog)s --help''')
    tmp_parser.add_argument('-f', nargs='+', metavar='FILE')
    tmp_parser.add_argument('-t', nargs='+', metavar='TAG')
    tmp_parser.add_argument('args', nargs='*')
    tmp_parser.set_defaults(func=commands.tag)

    # untag
    tmp_parser = subparsers.add_parser(
        'untag',
        usage='''%(prog)s FILE TAG
            %(prog)s TAG -f FILE [FILE ...]
            %(prog)s FILE -t TAG [TAG ...]
            %(prog)s -f FILE [FILE ...] -t TAG [TAG ...]
            %(prog)s --help''')
    tmp_parser.add_argument('-f', nargs='+', metavar='FILE')
    tmp_parser.add_argument('-t', nargs='+', metavar='TAG')
    tmp_parser.add_argument('args', nargs='*')
    tmp_parser.set_defaults(func=commands.untag)

    return parser
