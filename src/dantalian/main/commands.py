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

import json
import logging
import posixpath
import sys

from dantalian import base
from dantalian import bulk
from dantalian import dtags
from dantalian import findlib
from dantalian import library
from dantalian import tagging

_LOGGER = logging.getLogger(__name__)

# pylint: disable=missing-docstring


def _get_rootpath(args):
    """Unpack rootpath argument."""
    if args.root:
        return args.root
    else:
        return library.find_library('.')

# XXX tagname conversions for arguments


##############################################################################
# base
def link(args):
    rootpath = _get_rootpath(args)
    base.link(rootpath, args.src, args.dst)


def unlink(args):
    rootpath = _get_rootpath(args)
    for file in args.files:
        try:
            base.unlink(rootpath, file)
        except OSError as err:
            _LOGGER.error(err)


def rename(args):
    rootpath = _get_rootpath(args)
    base.rename(rootpath, args.src, args.dst)


def swap(args):
    rootpath = _get_rootpath(args)
    base.swap_dir(rootpath, args.dir)


def _do_all_dirs(top, callback):
    """Call function for all directories."""
    for (dirpath, dirnames, _) in os.walk(top):
        for dirname in dirnames:
            path = posixpath.join(dirpath, dirname)
            callback(path)


def save(args):
    rootpath = _get_rootpath(args)
    if args.all:
        _do_all_dirs(top, lambda path: base.save_dtags(rootpath, args.dir))
    else:
        base.save_dtags(rootpath, args.dir)


def load(args):
    rootpath = _get_rootpath(args)
    if args.all:
        _do_all_dirs(top, lambda path: base.load_dtags(rootpath, args.dir))
    else:
        base.load_dtags(rootpath, args.dir)


def unload(args):
    rootpath = _get_rootpath(args)
    if args.all:
        _do_all_dirs(top, lambda path: base.unload_dtags(rootpath, args.dir))
    else:
        t_unload


##############################################################################
def magic_list(args):
    rootpath = _get_rootpath(args)
    path = args.path
    if posixpath.isdir(path) and args.tags:
        results = dtags.list_tags(path)
    else:
        results = base.list_links(rootpath, path)
    for item in results:
        print(item)


##############################################################################
def search(args):
    rootpath = _get_rootpath(args)
    query = ' '.join(args.query)
    query_tree = findlib.parse_query(rootpath, query)
    results = findlib.search(query_tree)
    for entry in results:
        print(entry)


##############################################################################
# library
def init_library(args):
    library.init_library(args.path)


##############################################################################
# tagging
def tag(args):
    rootpath = _get_rootpath(args)
    for current_file in args.files:
        for current_tag in args.tags:
            try:
                tagging.tag(rootpath, current_file, current_tag)
            except OSError as err:
                _LOGGER.error(err)


def untag(args):
    rootpath = _get_rootpath(args)
    for current_file in args.files:
        for current_tag in args.tags:
            try:
                tagging.untag(rootpath, current_file, current_tag)
            except OSError as err:
                _LOGGER.error(err)


###############################################################################
# bulk
def clean(args):
    bulk.clean_symlinks(args.dir)


def rename_all(args):
    rootpath = _get_rootpath(args)
    bulk.rename_all(rootpath, args.path, args.name)


def unlink_all(args):
    rootpath = _get_rootpath(args)
    bulk.unlink_all(rootpath, args.path)


def import_tags(args):
    rootpath = _get_rootpath(args)
    path_tag_map = json.load(sys.stdin)
    bulk.import_tags(rootpath, path_tag_map)


def export_tags(args):
    rootpath = _get_rootpath(args)
    path_tag_map = bulk.export_tags(rootpath, args.dir, args.full)
    json.dump(path_tag_map, sys.stdout)
