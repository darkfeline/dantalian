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
from dantalian.search import search
from dantalian.search import parse_query
from dantalian.library import init_library
from dantalian.library import find_library

_LOGGER = logging.getLogger(__name__)


def tag(rootpath, target, name):
    """Tag target file-or-directory with given name.

    Args:
        rootpath: Rootpath to resolve tagnames.
        target: Tagname or path to target.
        name: Tagname or path.
    """
    _LOGGER.debug('tag(%r, %r, %r)', rootpath, target, name)
    target = tagnames.path(rootpath, target)
    dstpath = tagnames.path(rootpath, name)
    if posixpath.isdir(dstpath):
        pathlib.free_name_do(dstpath, posixpath.basename(target),
                             lambda dst: base.link(rootpath, target, dst))
    else:
        base.link(rootpath, target, dstpath)


def unlink(rootpath, target):
    """Unlink target file-or-directory.

    Args:
        rootpath: Rootpath to resolve tagnames.
        target: Tagname or path to target.
        name: Tagname or path.
    """
    target = tagnames.path(rootpath, target)
    base.unlink(rootpath, target)


def untag(rootpath, target, name):
    """Remove tag with given name from target file-or-directory.

    Args:
        rootpath: Rootpath to resolve tagnames.
        target: Tagname or path to target.
        name: Tagname or path.
    """
    target = tagnames.path(rootpath, target)
    dstpath = tagnames.path(rootpath, name)
    if posixpath.samefile(target, dstpath):
        base.unlink(rootpath, dstpath)
    elif posixpath.isdir(dstpath):
        for filepath in pathlib.listdirpaths(dstpath):
            if posixpath.samefile(target, filepath):
                base.unlink(rootpath, filepath)
    else:
        raise ValueError("Invalid arguments {} and {}".format(target, dstpath))


def list_links(rootpath, target):
    """List all links to the target file.

    Args:
        rootpath: Rootpath for tag conversions and finding links.
        target: Tagname or path to target.

    Returns:
        Generator yielding paths.
    """
    target = tagnames.path(rootpath, target)
    return base.list_links(rootpath, target)


def list_tags(rootpath, target):
    """List all tags of the target directory.

    Args:
        rootpath: Rootpath for tag conversions and finding links.
        target: Tagname or path to target.

    Returns:
        Generator yielding tagnames.
    """
    target = tagnames.path(rootpath, target)
    return dtags.list_tags(target)


def rename(rootpath, src, dst):
    """Rename src to dst and fix tags for directories.

    Args:
        rootpath: Rootpath for tag conversions.
        src: Source tagname or pathname.
        dst: Destination tagname or pathname.
    """
    src = tagnames.path(rootpath, src)
    dst = tagnames.path(rootpath, dst)
    base.link(rootpath, src, dst)
    base.unlink(rootpath, src)


def swap(rootpath, target):
    """Swap a symlink with its target directory.

    Args:
        rootpath: Rootpath for tag conversions.
        target: Target symlink tagname or pathname.

    """
    target = tagnames.path(rootpath, target)
    base.swap_dir(rootpath, target)


def rename_all(rootpath, target, name):
    """Rename all links to the target file-or-directory.

    Attempt to rename all links to the target under the rootpath to the given
    name, finding a name as necessary.  If there are multiple links in a
    directory, the first will be renamed and the rest unlinked.

    Args:
        rootpath: Base path for tag conversions and search.
        target: Tag or path to target.
        name: New filename.

    """
    target = tagnames.path(rootpath, target)
    newname = name
    seen = set()
    for filepath in base.list_links(rootpath, target):
        dirname = posixpath.dirname(filepath)
        if dirname in seen:
            unlink(rootpath, filepath)
            continue
        # pylint: disable=cell-var-from-loop
        pathlib.free_name_do(dirname, newname,
                             lambda dst: _rename_safe(rootpath, filepath, dst))
        seen.add(dirname)


def _rename_safe(rootpath, src, dst):
    """Safe version of rename.

    Raises FileExistsError if dst exists, but subject to race conditions.

    Args:
        rootpath: Rootpath for tag conversions.
        src: Source path.
        dst: Destination path.

    """
    if posixpath.exists(dst):
        raise oserrors.file_exists(src, dst)
    rename(rootpath, src, dst)


def unlink_all(rootpath, target):
    """Unlink all links to the target file-or-directory.

    Unlink all links to the target under the rootpath.

    Args:
        rootpath: Base path for tag conversions and search.
        target: Tag or path to target.

    """
    target = tagnames.path(rootpath, target)
    if posixpath.isdir(target):
        target = pathlib.readlink(target)
        base.unload_dtags(rootpath, target)
        shutil.rmtree(target)
    else:
        for path in base.list_links(rootpath, target):
            base.unlink(rootpath, path)


def save(rootpath, target):
    """Load symlinks from a directory's internal tags.

    Args:
        rootpath: Base path for tag conversions.
        target: Tag or path to target.

    """
    target = tagnames.path(rootpath, target)
    base.save_dtags(rootpath, target)


def load(rootpath, target):
    """Load symlinks from a directory's internal tags.

    Args:
        rootpath: Base path for tag conversions.
        target: Tag or path to target.

    """
    target = tagnames.path(rootpath, target)
    base.load_dtags(rootpath, target)


def unload(rootpath, target):
    """Unload symlinks from a directory's internal tags.

    Args:
        rootpath: Base path for tag conversions.
        target: Tag or path to target.

    """
    target = tagnames.path(rootpath, target)
    base.unload_dtags(rootpath, target)


def load_all(rootpath, top):
    """Load all directories.

    Args:
        rootpath: Base path for tag conversions.
        top: Top of directory tree to search.

    """
    top = tagnames.path(rootpath, top)
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
    top = tagnames.path(rootpath, top)
    for (dirpath, dirnames, _) in os.walk(top):
        for dirname in dirnames:
            path = posixpath.join(dirpath, dirname)
            base.unload_dtags(rootpath, path)


def clean(rootpath, top):
    """Clean broken symlink.

    Args:
        rootpath: Base path for tag conversions.
        top: Top of directory tree to search.

    """
    top = tagnames.path(rootpath, top)
    base.clean_symlinks(top)


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
    top = tagnames.path(rootpath, top)
    stat_tag_map = defaultdict(set)
    for dirpath, dirnames, filenames in os.walk(top):
        for filename in chain(dirnames, filenames):
            path = posixpath.join(dirpath, filename)
            stat = os.stat(path)
            tagname = tagnames.path2tag(rootpath, path)
            stat_tag_map[stat].add(tagname)
    return stat_tag_map
