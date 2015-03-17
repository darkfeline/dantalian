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

"""This module contains functions that work on multiple files and whole
directory trees.

"""

from collections import defaultdict
from itertools import chain
import logging
import os
import posixpath
import shutil

from dantalian import base
from dantalian import oserrors
from dantalian import pathlib
from dantalian import tagging
from dantalian import tagnames

_LOGGER = logging.getLogger(__name__)


def clean_symlinks(dirpath):
    """Remove all broken symlinks under the given directory."""
    # Broken symlinks appear as files, so we skip directories.
    for dirpath, _, filenames in os.walk(dirpath):
        for filename in filenames:
            path = posixpath.join(dirpath, filename)
            if posixpath.islink(path) and not posixpath.exists(path):
                os.unlink(path)


def rename_all(rootpath, top, path, name):
    """Rename all links to the file or directory.

    Attempt to rename all links to the target under the rootpath to the given
    name, finding a name as necessary.  If there are multiple links in a
    directory, the first will be renamed and the rest unlinked.

    Args:
        rootpath: Base path for tag conversions.
        top: Path of search directory.
        path: Path to target.
        name: New filename.

    """
    target = path
    newname = name
    seen = set()
    for filepath in base.list_links(top, target):
        dirname = posixpath.dirname(filepath)
        if dirname in seen:
            base.unlink(rootpath, filepath)
            continue
        # pylint: disable=cell-var-from-loop
        pathlib.free_name_do(dirname, newname,
                             lambda dst: base.rename(rootpath, filepath, dst))
        seen.add(dirname)


def unlink_all(rootpath, top, path):
    """Unlink all links to the target file-or-directory.

    Unlink all links to the target under top.

    Args:
        rootpath: Base path for tag conversions and search.
        top: Path of search directory.
        path: Path to target.

    """
    target = path
    if posixpath.isdir(target):
        target = pathlib.readlink(target)
        base.unload_dtags(rootpath, target)
        shutil.rmtree(target)
    else:
        for path in base.list_links(top, target):
            base.unlink(rootpath, path)


def import_tags(rootpath, path_tag_map):
    """Import tags.

    Essentially runs tag() for all paths for all tagnames.

    Args:
        rootpath: Base path for tag conversions.
        path_tag_map: Mapping of paths to lists of tagnames.

    """
    for (path, tags) in path_tag_map.items():
        for tagname in tags:
            tagging.tag(rootpath, path, tagname)


def export_tags(rootpath, top, full=False):
    """Export tags.

    Returns a dictionary that maps pathnames to lists of tagnames.

    Each file will only have one key path mapping to a list of tags.  If
    full=True, each file will have one key path for each one of that file's
    links, all mapping to the same list of tags.

    Args:
        rootpath: Base path for tag conversions.
        top: Top of directory tree to export.
        full: Whether to include all paths to a file.  Defaults to False.
    Returns:
        Dictionary mapping pathnames to lists of tagnames.

    """
    stat_tag_map = _export_stat_map(rootpath, top)
    results = dict()
    if full:
        for tags in stat_tag_map.values():
            tags = list(tags)
            for tagname in tags:
                path = tagnames.tag2path(rootpath, tagname)
                results[path] = tags
    else:
        for tags in stat_tag_map.values():
            tags = list(tags)
            path = tagnames.tag2path(rootpath, tags[0])
            results[path] = tags
    return results


def _export_stat_map(rootpath, top):
    """Export a map of stat objects to sets of tags.

    Args:
        rootpath: Base path for tag conversions.
        top: Top of directory tree to export.
    Returns:
        Dictionary mapping stat objects to sets of tagnames.

    """
    stat_tag_map = defaultdict(set)
    for dirpath, dirnames, filenames in os.walk(top):
        for filename in chain(dirnames, filenames):
            path = posixpath.join(dirpath, filename)
            stat = os.stat(path)
            tagname = tagnames.path2tag(rootpath, path)
            stat_tag_map[stat].add(tagname)
    return stat_tag_map
