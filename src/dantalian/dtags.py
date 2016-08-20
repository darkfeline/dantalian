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

"""This module defines interaction with directory dtags.

A function that has any side effects other than manipulating dtags files does
not belong in here.

"""

import os
import posixpath

_DTAGS_FILE = '.dtags'


def _dtags_file(dirpath):
    """Get the path of a directory's dtags file."""
    return posixpath.join(dirpath, _DTAGS_FILE)


def open_dtags(dirpath, mode='r'):
    """Open dtags file of directory with given mode."""
    tags_file = _dtags_file(dirpath)
    try:
        return open(tags_file, mode)
    except FileNotFoundError:
        os.mknod(tags_file)
        return open(tags_file, mode)


def write_tag(file, tagname):
    """Write tag to file at current position."""
    file.write(tagname + '\n')


def write_tags(file, tags):
    """Write a list of tags to a file object."""
    file.seek(0)
    for tag in tags:
        write_tag(file, tag)
    file.truncate()


def read_tags(file):
    """Read tags from file object, leaving position at end.

    Returns:
        List of tagnames.

    """
    return file.read().splitlines()


def add_tag(dirpath, tagname):
    """Add tag to directory's dtags if not already added."""
    with open_dtags(dirpath, 'r+') as file:
        tags = read_tags(file)
        if tagname in tags:
            return
        write_tag(file, tagname)


def remove_tag(dirpath, tagname):
    """Remove tag from directory's dtags if it exists."""
    with open_dtags(dirpath, 'r+') as file:
        tags = read_tags(file)
        if tagname not in tags:
            return
        tags = [tag
                for tag in tags
                if tag != tagname]
        write_tags(file, tags)


def list_tags(dirpath):
    """Return a list of a directory's dtags."""
    with open_dtags(dirpath, 'r+') as file:
        return read_tags(file)


def set_tags(dirpath, tags):
    """Set a directory's tags to the provided list."""
    with open_dtags(dirpath, 'r+') as file:
        write_tags(file, tags)


def rename_all(dirpath, name):
    """Rename all dtags of the given directory.

    Rename all of the dtags' basenames.

    """
    with open_dtags(dirpath, 'r+') as file:
        tags = read_tags(file)
        tags = [posixpath.join(posixpath.dirname(tag), name) for tag in tags]
        write_tags(file, tags)
