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

"""This module contains tagging functions, i.e. tagging with a directory."""

import logging
import posixpath

from dantalian import base
from dantalian import pathlib

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
