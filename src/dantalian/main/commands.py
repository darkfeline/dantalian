# Copyright (C) 2015  Allen Li
#
# This file is part of Dantalian.
#
# Dantalian is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dantalian is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dantalian.  If not, see <http://www.gnu.org/licenses/>.

# Copyright 2015 Allen Li
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module contains command implementations."""

import abc
import logging

_LOGGER = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods

COMMANDS = []


def add_command(cls):
    """Add command to COMMANDS list."""
    COMMANDS.append(cls)
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


@add_command
class Tag(CommandBuilder):

    # pylint: disable=missing-docstring

    parser_args = Args(
        'tag',
        usage='%(prog)s -f FILE [FILE ...] -- TAG [TAG ...]')

    params_args = [
        Args('--root', metavar='ROOT', default='.'),
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


@add_command
class Untag(CommandBuilder):

    # pylint: disable=missing-docstring

    parser_args = Args(
        'untag',
        usage='%(prog)s -f FILE [FILE ...] -- TAG [TAG ...]')

    params_args = [
        Args('--root', metavar='ROOT', default='.'),
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


@add_command
class Search(CommandBuilder):

    # pylint: disable=missing-docstring

    parser_args = Args(
        'search',
        usage='%(prog)s QUERY')

    params_args = [
        Args('--root', metavar='ROOT', default='.'),
        Args('query', nargs='+'),
    ]

    @staticmethod
    def command_func(args):
        root = library.find_library(args.root)
        query = ' '.join(args.query)
        query_tree = library.parse_query(root, query)
        results = library.search(query_tree)
        for entry in results:
            print(entry)


@add_command
class InitLibrary(CommandBuilder):

    # pylint: disable=missing-docstring

    parser_args = Args(
        'init_library',
        usage='%(prog)s [PATH]')

    params_args = [
        Args('path', nargs='?', default=''),
    ]

    @staticmethod
    def command_func(args):
        library.init_library(args.path)


@add_command
class List(CommandBuilder):

    # pylint: disable=missing-docstring

    parser_args = Args(
        'list',
        usage='%(prog)s PATH')

    params_args = [
        Args('--root', metavar='ROOT', default='.'),
        Args('--external', action='store_true'),
        Args('path'),
    ]

    @staticmethod
    def command_func(args):
        path = args.path
        root = args.root
        if posixpath.isfile(path):
            results = library.list_links(root, path)
        elif posixpath.isdir(path):
            # TODO internal vs external
            results = library.list_tags(root, path)
        else:
            raise oserrors.file_not_found(path)
        for item in results:
            print(item)
