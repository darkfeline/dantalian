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

def _add_root(parser):
    """Add rootpath argument."""
    parser.add_argument('--root', metavar='ROOT')

def _make_base(subparsers):
    """Add base command parsers."""
    # link
    parser = subparsers.add_parser('link', usage='%(prog)s SRC DST')
    _add_root(parser)
    parser.add_argument('src')
    parser.add_argument('dst')
    parser.set_defaults(func=commands.link)

    # unlink
    parser = subparsers.add_parser('unlink', usage='%(prog)s SRC DST')
    _add_root(parser)
    parser.add_argument('files', nargs='+')
    parser.set_defaults(func=commands.unlink)

    # rename
    parser = subparsers.add_parser('rename', usage='%(prog)s SRC DST')
    _add_root(parser)
    parser.add_argument('src')
    parser.add_argument('dst')
    parser.set_defaults(func=commands.rename)

    # swap
    parser = subparsers.add_parser('swap', usage='%(prog)s DIR')
    _add_root(parser)
    parser.add_argument('dir')
    parser.set_defaults(func=commands.swap)

    # save
    parser = subparsers.add_parser('save', usage='%(prog)s DIR')
    _add_root(parser)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('dir')
    parser.set_defaults(func=commands.save)

    # load
    parser = subparsers.add_parser('load', usage='%(prog)s DIR')
    _add_root(parser)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('dir')
    parser.set_defaults(func=commands.load)

    # unload
    parser = subparsers.add_parser('unload', usage='%(prog)s DIR')
    _add_root(parser)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('dir')
    parser.set_defaults(func=commands.unload)


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

    ###########################################################################
    # base
    _make_base(subparsers)

    ###########################################################################
    # magic list
    parser = subparsers.add_parser('list', usage='%(prog)s PATH')
    _add_root(parser)
    parser.add_argument('--tags', action='store_true')
    parser.add_argument('path')
    parser.set_defaults(func=commands.magic_list)

    ###########################################################################
    # search
    parser = subparsers.add_parser('search', usage='%(prog)s QUERY')
    _add_root(parser)
    parser.add_argument('query', nargs='+')
    parser.set_defaults(func=commands.search)

    ###########################################################################
    # library
    parser = subparsers.add_parser('init_library', usage='%(prog)s [PATH]')
    parser.add_argument('path', nargs='?', default='.')
    parser.set_defaults(func=commands.init_library)

    ###########################################################################
    # tagging
    # tag
    parser = subparsers.add_parser(
        'tag',
        usage='%(prog)s -f FILE [FILE ...] -- TAG [TAG ...]')
    _add_root(parser)
    parser.add_argument('-f', nargs='+', dest='files', required=True,
                        metavar='FILE')
    parser.add_argument('tags', nargs='+')
    parser.set_defaults(func=commands.tag)

    # untag
    parser = subparsers.add_parser(
        'untag',
        usage='%(prog)s -f FILE [FILE ...] -- TAG [TAG ...]')
    _add_root(parser)
    parser.add_argument('-f', nargs='+', dest='files', required=True,
                        metavar='FILE')
    parser.add_argument('tags', nargs='+')
    parser.set_defaults(func=commands.untag)

    ###########################################################################
    # bulk
    # clean
    parser = subparsers.add_parser('clean', usage='%(prog)s [DIR]')
    parser.add_argument('dir', default='.')
    parser.set_defaults(func=commands.clean)

    # rename_all
    parser = subparsers.add_parser('rename_all', usage='%(prog)s PATH NAME')
    _add_root(parser)
    parser.add_argument('path')
    parser.add_argument('name')
    parser.set_defaults(func=commands.rename_all)

    # unlink_all
    parser = subparsers.add_parser('unlink_all', usage='%(prog)s PATH')
    _add_root(parser)
    parser.add_argument('path')
    parser.set_defaults(func=commands.unlink_all)

    # import
    parser = subparsers.add_parser('import', usage='%(prog)s')
    _add_root(parser)
    parser.set_defaults(func=commands.import_tags)

    # export
    parser = subparsers.add_parser('export', usage='%(prog)s DIR')
    _add_root(parser)
    parser.add_argument('dir')
    parser.add_argument('--full', action='store_true')
    parser.set_defaults(func=commands.export_tags)

    return top_parser
