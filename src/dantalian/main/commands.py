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

"""This module contains command implementations."""

import logging
import posixpath

from dantalian import library

_LOGGER = logging.getLogger(__name__)


def tag(args):
    root = library.find_library(args.root)
    for current_file in args.files:
        for current_tag in args.tags:
            try:
                library.tag(root, current_file, current_tag)
            except OSError as err:
                _LOGGER.error(err)

def untag(args):
    root = library.find_library(args.root)
    for current_file in args.files:
        for current_tag in args.tags:
            try:
                library.untag(root, current_file, current_tag)
            except OSError as err:
                _LOGGER.error(err)


def search(args):
    root = library.find_library(args.root)
    query = ' '.join(args.query)
    query_tree = library.parse_query(root, query)
    results = library.search(query_tree)
    for entry in results:
        print(entry)


def init_library(args):
    library.init_library(args.path)


def list(args):
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
