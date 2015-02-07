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

import dantalian
from dantalian import library
from dantalian import oserrors

_LOGGER = logging.getLogger(__name__)

# pylint: disable=missing-docstring


def tag(args):
    rootpath = library.find_library(args.root)
    for current_file in args.files:
        for current_tag in args.tags:
            try:
                dantalian.tag(rootpath, current_file, current_tag)
            except OSError as err:
                _LOGGER.error(err)


def untag(args):
    rootpath = library.find_library(args.root)
    for current_file in args.files:
        for current_tag in args.tags:
            try:
                dantalian.untag(rootpath, current_file, current_tag)
            except OSError as err:
                _LOGGER.error(err)


def unlink(args):
    rootpath = library.find_library(args.root)
    for file in args.files:
        try:
            dantalian.unlink(rootpath, file)
        except OSError as err:
            _LOGGER.error(err)


# TODO
def search(args):
    rootpath = library.find_library(args.root)
    query = ' '.join(args.query)
    query_tree = dantalian.parse_query(rootpath, query)
    results = dantalian.search(query_tree)
    for entry in results:
        print(entry)


def init_library(args):
    dantalian.init_library(args.path)


def list_tags(args):
    path = args.path
    rootpath = args.root
    if posixpath.isfile(path):
        results = dantalian.list_links(rootpath, path)
    elif posixpath.isdir(path):
        if args.external:
            results = dantalian.list_links(rootpath, path)
        else:
            results = dantalian.list_tags(path)
    else:
        raise oserrors.file_not_found(path)
    for item in results:
        print(item)
