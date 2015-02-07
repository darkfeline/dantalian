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

"""This is the dantalian package.

The package itself serves as a high level public interface to dantalian
functionality.

"""

from collections import defaultdict
from itertools import chain
import logging
import os
import posixpath
import shutil

from dantalian import base
from dantalian import dtags
from dantalian import oserrors
from dantalian import pathlib
from dantalian import tagnames

# exported as module API
from dantalian.base import link
from dantalian.base import unlink
from dantalian.base import rename
from dantalian.base import list_links
from dantalian.dtags import list_tags
from dantalian.base import swap_dir
from dantalian.base import save_dtags
from dantalian.base import load_dtags
from dantalian.base import unload_dtags
from dantalian.base import clean_symlinks
from dantalian.searching import search
from dantalian.searching import parse_query
from dantalian.library import init_library
from dantalian.library import find_library

_LOGGER = logging.getLogger(__name__)


def tag(rootpath, path, directory):
    """Tag file with a directory.

    Args:
        rootpath: Rootpath to resolve tagnames.
        path: Path of file or directory to tag.
        directory: Directory path.
    """
    pathlib.free_name_do(directory, posixpath.basename(path),
                         lambda dst: base.link(rootpath, path, dst))


def untag(rootpath, path, directory):
    """Untag file from a directory.

    Args:
        rootpath: Rootpath to resolve tagnames.
        path: Path of file or directory to tag.
        directory: Directory path.
    """
    target = path
    for filepath in pathlib.listdirpaths(directory):
        if posixpath.samefile(target, filepath):
            base.unlink(rootpath, filepath)


def rename_all(rootpath, path, name):
    """Rename all links to the file or directory.

    Attempt to rename all links to the target under the rootpath to the given
    name, finding a name as necessary.  If there are multiple links in a
    directory, the first will be renamed and the rest unlinked.

    Args:
        rootpath: Base path for tag conversions and search.
        path: Path to target.
        name: New filename.

    """
    target = path
    newname = name
    seen = set()
    for filepath in base.list_links(rootpath, target):
        dirname = posixpath.dirname(filepath)
        if dirname in seen:
            base.unlink(rootpath, filepath)
            continue
        # pylint: disable=cell-var-from-loop
        pathlib.free_name_do(dirname, newname,
                             lambda dst: _rename_safe(rootpath, filepath, dst))
        seen.add(dirname)


def _rename_safe(rootpath, src, dst):
    """Safe version of rename.

    Raises FileExistsError if dst exists instead of overwriting, but subject to
    race conditions.

    base.rename() implementation does not overwrite, but this function is kept
    in case base.rename() implementation is changed.

    Args:
        rootpath: Rootpath for tag conversions.
        src: Source path.
        dst: Destination path.

    """
    if posixpath.exists(dst):
        raise oserrors.file_exists(src, dst)
    base.rename(rootpath, src, dst)


def unlink_all(rootpath, path):
    """Unlink all links to the target file-or-directory.

    Unlink all links to the target under the rootpath.

    Args:
        rootpath: Base path for tag conversions and search.
        path: Path to target.

    """
    target = path
    if posixpath.isdir(target):
        target = pathlib.readlink(target)
        base.unload_dtags(rootpath, target)
        shutil.rmtree(target)
    else:
        for path in base.list_links(rootpath, target):
            base.unlink(rootpath, path)


def load_all(rootpath, top):
    """Load all directories.

    Args:
        rootpath: Base path for tag conversions.
        top: Top of directory tree to search.

    """
    for (dirpath, dirnames, _) in os.walk(top):
        for dirname in dirnames:
            path = posixpath.join(dirpath, dirname)
            base.load_dtags(rootpath, path)


def unload_all(rootpath, top):
    """Unload all directories.

    Args:
        rootpath: Base path for tag conversions.
        top: Top of directory tree to search.

    """
    for (dirpath, dirnames, _) in os.walk(top):
        for dirname in dirnames:
            path = posixpath.join(dirpath, dirname)
            base.unload_dtags(rootpath, path)


def import_tags(rootpath, path_tag_map):
    """Import tags.

    Essentially runs tag() for all paths for all tagnames.

    Args:
        rootpath: Base path for tag conversions.
        path_tag_map: Mapping of paths to lists of tagnames.

    """
    for (path, tags) in path_tag_map.items():
        for tagname in tags:
            tag(rootpath, path, tagname)


def export_tags(rootpath, top, full=False):
    """Export tags.

    Returns a dictionary that maps pathnames to lists of tagnames.

    Each file will only have one key path mapping to a list of tags.  If
    full=True, Each file will have one key path for each one of that file's
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
