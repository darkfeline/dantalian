"""
This module contains functions implementing commands for the main script.
"""

import abc
import logging

from dantalian import library

_LOGGER = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods

COMMANDS = []


def _add_command(cls):
    """Add command to COMMANDS list."""
    COMMANDS.append(cls.__name__)
    return cls


class Args:

    """Used for packing arguments."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class CommandBuilder(metaclass=abc.ABCMeta):

    """CommandBuilder for building command parsers for a subparser.

    Subclass and implement command_func(), and set the class attributes, then
    call add_parser() on the subparsers object.

    Class Attributes:
        parser_args: Args for constructing the parser.
        params_args: List of Args for adding arguments to parser.

    """

    parser_args = Args()
    params_args = []

    @classmethod
    def add_parser(cls, subparsers):
        """Add a subparser for this command."""
        args = cls.parser_args
        tmp_parser = subparsers.add_parser(*args.args, **args.kwargs)
        for args in cls.params_args:
            tmp_parser.add_argument(*args.args, **args.kwargs)
        tmp_parser.set_defaults(func=cls.command_func)

    @staticmethod
    @abc.abstractmethod
    def command_func(args):
        """Function which this command should call."""


@_add_command
class Tag(CommandBuilder):

    # pylint: disable=missing-docstring

    parser_args = Args(
        'tag',
        usage='''%(prog)s -f FILE [FILE ...] -- TAG [TAG ...]
            %(prog)s --help''')

    params_args = [
        Args('--root', metavar='ROOT', default=''),
        Args('-f', nargs='+', dest='files', required=True, metavar='FILE'),
        Args('tags', nargs='+'),
    ]

    @staticmethod
    def command_func(args):
        root = library.find_library(args.root)
        for current_file in args.files:
            for current_tag in args.tags:
                try:
                    library.tag(root, current_file, current_tag)
                except OSError as err:
                    _LOGGER.error(err)


@_add_command
class Untag(CommandBuilder):

    # pylint: disable=missing-docstring

    parser_args = Args(
        'untag',
        usage='''%(prog)s -f FILE [FILE ...] -- TAG [TAG ...]
            %(prog)s --help''')

    params_args = [
        Args('--root', metavar='ROOT', default=''),
        Args('-f', nargs='+', dest='files', required=True, metavar='FILE'),
        Args('tags', nargs='+'),
    ]

    @staticmethod
    def command_func(args):
        root = library.find_library(args.root)
        for current_file in args.files:
            for current_tag in args.tags:
                try:
                    library.untag(root, current_file, current_tag)
                except OSError as err:
                    _LOGGER.error(err)


@_add_command
class Search(CommandBuilder):

    # pylint: disable=missing-docstring

    parser_args = Args(
        'search',
        usage='''%(prog)s QUERY
            %(prog)s --help''')

    params_args = [
        Args('--root', metavar='ROOT', default=''),
        Args('query', nargs='+'),
    ]

    @staticmethod
    def command_func(args):
        root = library.find_library(args.root)
        query_tree = library.parse_query(root, args.query)
        results = library.search(query_tree)
        for entry in results:
            print(entry)
