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
    tmp_parser.add_argument('--root', metavar='ROOT', default='')
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
    tmp_parser.add_argument('--root', metavar='ROOT', default='')
    tmp_parser.add_argument('-f', nargs='+', metavar='FILE')
    tmp_parser.add_argument('-t', nargs='+', metavar='TAG')
    tmp_parser.add_argument('args', nargs='*')
    tmp_parser.set_defaults(func=commands.untag)

    # search
    tmp_parser = subparsers.add_parser(
        'search',
        usage='''%(prog)s QUERY
            %(prog)s --help''')
    tmp_parser.add_argument('--root', metavar='ROOT', default='')
    tmp_parser.add_argument('query', nargs='+')
    tmp_parser.set_defaults(func=commands.search)

    return parser
