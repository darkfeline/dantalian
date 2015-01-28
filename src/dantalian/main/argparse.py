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

"""
Entry point.
"""

import argparse

from . import commands


def make_parser():

    """Make argument parser.

    Argument parser is reusable, so keep the parser around instead of remaking
    it.

    You can use it to parse and run an argument list like so:

        >>> parser = make_parser()
        >>> args = parser.parse_args(['tag', 'foo', 'bar'])
        >>> args.func(args)
    """

    top_parser = argparse.ArgumentParser()
    top_parser.add_argument('--debug', action='store_true')
    subparsers = top_parser.add_subparsers(title='Commands')

    parser = subparsers.add_parser(
        'tag',
        usage='%(prog)s -f FILE [FILE ...] -- TAG [TAG ...]')
    parser.add_argument('--root', metavar='ROOT', default='.')
    parser.add_argument('-f', nargs='+', dest='files', required=True,
                        metavar='FILE')
    parser.add_argument('tags', nargs='+')
    parser.set_defaults(func=commands.tag)

    parser = subparsers.add_parser(
        'untag',
        usage='%(prog)s -f FILE [FILE ...] -- TAG [TAG ...]')
    parser.add_argument('--root', metavar='ROOT', default='.')
    parser.add_argument('-f', nargs='+', dest='files', required=True,
                        metavar='FILE')
    parser.add_argument('tags', nargs='+')
    parser.set_defaults(func=commands.untag)

    parser = subparsers.add_parser(
        'unlink',
        usage='%(prog)s FILE [FILE ...]')
    parser.add_argument('--root', metavar='ROOT', default='.')
    parser.add_argument('files', nargs='+')
    parser.set_defaults(func=commands.untag)

    parser = subparsers.add_parser('search', usage='%(prog)s QUERY')
    parser.add_argument('--root', metavar='ROOT', default='.')
    parser.add_argument('query', nargs='+')
    parser.set_defaults(func=commands.search)

    parser = subparsers.add_parser('init_library', usage='%(prog)s [PATH]')
    parser.add_argument('path', nargs='?', default='.')
    parser.set_defaults(func=commands.init_library)

    parser = subparsers.add_parser('list', usage='%(prog)s PATH')
    parser.add_argument('--root', metavar='ROOT', default='.')
    parser.add_argument('--external', action='store_true')
    parser.add_argument('path')
    parser.set_defaults(func=commands.list_tags)

    # TODO rename
    # TODO swap
    # TODO rename_all
    # TODO unlink_all
    # TODO save
    # TODO load
    # TODO unload
    # TODO clean
    # TODO import
    # TODO export

    return top_parser
