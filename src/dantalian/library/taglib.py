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

"""This module contains functions for working with tagnames and libraries."""

import os
import posixpath


def is_tag(name):
    """Check if name is a tagname."""
    return name.startswith('//')


def path2tag(rootpath, pathname):
    """Convert a pathname to a tagname."""
    return '//' + posixpath.relpath(pathname, rootpath)


def tag2path(rootpath, tagname):
    """Convert a tagname to a pathname."""
    return posixpath.join(rootpath, tagname.lstrip('/'))


def path(rootpath, name):
    """Return tagname or pathname as a pathname."""
    if is_tag(name):
        name = tag2path(rootpath, name)
    return name


def tag(rootpath, name):
    """Return tagname or pathname as a tagname."""
    if not is_tag(name):
        name = path2tag(rootpath, name)
    return name


_ROOTDIR = '.dantalian'

def is_library(dirpath):
    """Return whether dirpath refers to a library."""
    return posixpath.isdir(posixpath.join(dirpath, _ROOTDIR))


def find_library(dirpath=''):
    """Find library.

    Return the path of the first library found above the given path.  Return
    None if no library is found.

    An empty string means to use the current directory.

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
    os.mkdir(posixpath.join(dirpath, _ROOTDIR))


def get_resource(dirpath, resource_path):
    """Get the path of a resource for a library."""
    return posixpath.join(dirpath, _ROOTDIR, resource_path)
