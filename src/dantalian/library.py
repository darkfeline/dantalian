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

"""This module defines interaction with libraries."""

import os
import posixpath


_ROOTDIR = '.dantalian'

def is_library(dirpath):
    """Return whether dirpath refers to a library."""
    return posixpath.isdir(posixpath.join(dirpath, _ROOTDIR))


def find_library(dirpath='.'):
    """Find library.

    Return the path of the first library found above the given path.  Return
    None if no library is found.

    """
    dirpath = posixpath.abspath(dirpath)
    _, dirpath = posixpath.splitdrive(dirpath)
    while True:
        if is_library(dirpath):
            return dirpath
        elif dirpath in ('/', ''):
            return None
        else:
            dirpath, _ = posixpath.split(dirpath)


def init_library(dirpath):
    """Initialize library."""
    rootdir = posixpath.join(dirpath, _ROOTDIR)
    if not posixpath.isdir(rootdir):
        os.mkdir(rootdir)


def get_resource(dirpath, resource_path):
    """Get the path of a resource for a library."""
    return posixpath.join(dirpath, _ROOTDIR, resource_path)
