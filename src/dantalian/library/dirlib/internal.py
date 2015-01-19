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

"""This module contains library operations for directory internal tagging."""

import os
import posixpath

from dantalian import pathlib

_DTAGS_FILE = '.dtags'


def _dtags_file(dirpath):
    """Get the path of a directory's dtags file."""
    return posixpath.join(dirpath, _DTAGS_FILE)


class _DummyFile:

    """Dummy empty file."""

    # pylint: disable=missing-docstring
    # pylint: disable=no-self-use
    # pylint: disable=too-few-public-methods

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def read(self):
        return ''


def _open_dtags(dirpath, mode='r'):
    """Open dtags file of directory with given mode.

    If mode is 'r+', make file if it doesn't exist.
    If mode is 'r', return dummy file if it doesn't exist.

    """
    tags_file = _dtags_file(dirpath)
    while True:
        try:
            return open(tags_file, mode)
        except FileNotFoundError:
            if mode == 'r':
                return _DummyFile()
            else:  # mode == 'r+' (other modes will make file)
                os.mknod(tags_file)


def _write_tags(file, tags):
    """Write tags to a file object."""
    file.seek()
    file.writelines(tag + '\n' for tag in tags)
    file.truncate()


def _read_tags(file):
    """Read tags from file object, leaving position at end.

    Returns:
        List of tagnames.

    """
    return file.read().splitlines()


def _append_tag(file, tagname):
    """Write tag to file at current position."""
    file.write(tagname + '\n')


def tag(target, tagname):
    """Tag target directory with the given tagname.

    Args:
        target: Path of directory to tag.
        tagname: Tagname.

    If the directory is already tagged internally, nothing happens.

    """
    target = posixpath.abspath(target)
    tagname = tagname.rstrip('/')  # can't tag into a directory
    with _open_dtags(target, 'r+') as duplex:
        tags = _read_tags(duplex)
        if tagname in tags:
            return
        _append_tag(duplex, tagname)


def _filter_tags(target, func):
    """Remove all tags from target directory that satisfies the filter.

    Args:
        root: Rootpath.
        target: Path of directory to untag.
        func: Filter function.
    Return:
        List of removed tagnames.

    """
    keep = []
    discard = []
    with _open_dtags(target, 'r+') as duplex:
        tags = _read_tags(duplex)
        for tagname in tags:
            if func(tagname):
                discard.append(tagname)
            else:
                keep.append(tagname)
        if discard:
            _write_tags(duplex, keep)
    return discard


def untag(target, tagname):
    """Remove tag from target directory.

    If the directory is not tagged internally, nothing happens.

    Args:
        target: Path of directory to untag.
        tagname: Tagname.

    """
    tagname = tagname.rstrip('/')  # can't tag into a directory
    _filter_tags(target, lambda tag: tag == tagname)


def untag_dirname(target, tagname):
    """Remove all tags with the given dirname from target directory.

    Args:
        target: Path of directory to untag.
        tagname: Tagname, purge all tags whose dirname equals this.

    """
    tagname = tagname.rstrip('/')  # dirname doesn't have trailing slashes
    _filter_tags(target, lambda tag: posixpath.dirname(tag) == tagname)


def list_tags(dirpath):
    """Return a list of tagnames of a directory."""
    with _open_dtags(dirpath) as rfile:
        tags = _read_tags(rfile)
    return tags


def is_tagged(dirpath, tagname):
    """Return if directory is tagged with tagname.

    Args:
        dirpath: Path of directory.
        tagname: Tagname.

    """
    return tagname in list_tags(dirpath)


def rename_all(target, newname):
    """Rename a directory.

    Rename the directory and the basenames of all of its tagnames.

    Args:
        target: Path of directory to rename.
        newname: New name.

    """
    parent_dir = posixpath.dirname(target.rstrip('/'))
    target = pathlib.free_name_do(
        parent_dir, newname, lambda dst: pathlib.rename_safe(target, dst))
    with _open_dtags(target, 'r+') as duplex:
        tags = _read_tags(duplex)
        tags = [posixpath.join(posixpath.dirname(tag), newname) for tag in tags]
        _write_tags(duplex, tags)


def replace_tag(dirpath, oldtag, newtag):
    """Remove oldtag and add newtag to directory.

    If oldtag does not exist, this function won't raise an error and will
    continue to add the supplied newtag, as removal is done as a filter.

    """
    with _open_dtags(dirpath, 'r+') as duplex:
        tags = _read_tags(duplex)
        tags = [tag for tag in tags if tag != oldtag]
        tags.append(newtag)
        _write_tags(duplex, tags)
