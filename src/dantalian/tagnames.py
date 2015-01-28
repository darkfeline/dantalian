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

"""This module defines interaction with tagnames."""

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
