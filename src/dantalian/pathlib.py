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
This module contains shared path-related functionality.
"""

from itertools import count
import os
import posixpath


def readlink(path):
    """Follow all symlinks and return the target of the last link."""
    while posixpath.islink(path):
        path = os.readlink(path)
    return path


def listdirpaths(path):
    """Like os.listdir(), except return pathnames instead of filenames.

    Returns:
      A generator yielding paths.

    """
    for entry in os.listdir(path):
        yield posixpath.join(path, entry)


def free_name(dirpath, name):
    """Find a free filename in the given directory.

    Given a desired filename, this function attempts to find a filename
    that is not currently being used in the given directory, adding an
    incrementing index to the filename as necessary.

    Note that the returned filename might not work due to race
    conditions.  Program accordingly.

    Args:
        dirpath: Pathname of directory to look in.
        name: Desired filename.

    Returns:
        Filename.

    """
    files = os.listdir(dirpath)
    if name not in files:
        return name
    base, ext = posixpath.splitext(name)
    i = count(1)
    while True:
        name = ''.join((base, '.', str(next(i)), ext))
        if name not in files:
            return name


def free_name_do(dirpath, name, callback):
    """Repeatedly attempt to do something while finding a free filename.

    Returns:
        Path of successful new name.
    """
    while True:
        dst = posixpath.join(dirpath, free_name(dirpath, name))
        try:
            callback(dst)
        except FileExistsError:
            continue
        else:
            return dst
