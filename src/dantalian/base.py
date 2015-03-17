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

"""This module defines basic interaction with a semantic filesystem.

This module primarily extends link(), unlink(), and rename() to work as though
they support directory linking.  The rest of the functions exist as
implementation details to manage directory linking with symlinks and dtags.

"""

from itertools import chain
import os
import posixpath

from dantalian import dtags
from dantalian import oserrors
from dantalian import pathlib
from dantalian import tagnames


def link(rootpath, src, dst):
    """Link src to dst.

    Args:
        rootpath: Path for tagname conversions.
        src: Source path.
        dst: Destination path.

    """
    if posixpath.isdir(src):
        src = pathlib.readlink(src)
        os.symlink(posixpath.abspath(src), dst)
        dtags.add_tag(src, tagnames.path2tag(rootpath, dst))
    else:
        os.link(src, dst)


def unlink(rootpath, path):
    """Unlink given path.

    If the target is a directory without any other links, raise OSError.

    """
    target = path
    # We unlink the target.  However, if it is a directory, we want to swap it
    # out for one of its symlinks, then unlink the symlink.  If the directory
    # doesn't have any tags, then we fail.
    if posixpath.isdir(target):
        if not posixpath.islink(target):
            tags = dtags.list_tags(target)
            if not tags:
                raise oserrors.is_a_directory(target)
            swap_candidate = tagnames.tag2path(rootpath, tags[0])
            swap_dir(rootpath, swap_candidate)
            assert posixpath.islink(target)
        dtags.remove_tag(target, tagnames.path2tag(rootpath, target))
    os.unlink(target)


def rename(rootpath, src, dst):
    """Rename src to dst and fix tags for directories.

    Doesn't overwrite an existing file at dst.

    Args:
        rootpath: Rootpath for tagname conversions.
        src: Source path.
        dst: Destination path.
    """
    link(rootpath, src, dst)
    unlink(rootpath, src)


def swap_dir(rootpath, path):
    """Swap a symlink with its target directory.

    Args:
        rootpath: Rootpath for tag conversions.
        path: Path of target symlink.

    """
    target = path
    if posixpath.islink(target) and posixpath.isdir(target):
        here = target
        there = pathlib.readlink(target)
        # here is the symlink
        # there is the dir
        here_tag = tagnames.path2tag(rootpath, here)
        there_tag = tagnames.path2tag(rootpath, there)
        dtags.remove_tag(here, here_tag)
        dtags.add_tag(here, there_tag)
        os.unlink(here)
        # here is now nothing
        # there is now the dir
        os.rename(there, here)
        # here is now the dir
        # there is now nothing
        os.symlink(here, there)
    else:
        raise ValueError('{} is not a symlink to a directory'.format(target))


def list_links(top, path):
    """List all links to the target file.

    Args:
        top: Path to top of directory tree to search.
        path: Path of file.

    Returns:
        Generator yielding paths.
    """
    target = path
    for (dirpath, dirnames, filenames) in os.walk(top):
        for name in chain(dirnames, filenames):
            filepath = posixpath.join(dirpath, name)
            if posixpath.samefile(target, filepath):
                yield filepath


def save_dtags(rootpath, top, dirpath):
    """Save symlinks to a directory's dtags, overwriting it.

    Args:
        rootpath: Path for tag conversions.
        top: Path of directory in which to search.
        dirpath: Path of directory whose dtags to update.

    """
    dirpath = pathlib.readlink(dirpath)
    tags = [tagnames.path2tag(rootpath, path)
            for path in list_links(top, dirpath)]
    dir_tagname = tagnames.path2tag(rootpath, dirpath)
    tags = [tagname
            for tagname in tags
            if tagname != dir_tagname]
    dtags.set_tags(dirpath, tags)


def load_dtags(rootpath, dirpath):
    """Create symlinks for a directory using its dtags."""
    tags = dtags.list_tags(dirpath)
    dirpath = pathlib.readlink(dirpath)
    target = posixpath.abspath(dirpath)
    for tagname in tags:
        dstpath = tagnames.tag2path(rootpath, tagname)
        os.symlink(target, dstpath)


def unload_dtags(rootpath, dirpath):
    """Remove symlinks using a directory's dtags."""
    tags = dtags.list_tags(dirpath)
    dirpath = pathlib.readlink(dirpath)
    for tagname in tags:
        tagpath = tagnames.tag2path(rootpath, tagname)
        if posixpath.samefile(dirpath, tagpath):
            os.unlink(tagpath)
