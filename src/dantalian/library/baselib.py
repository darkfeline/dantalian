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

"""This module contains basic library operations.

The functions in this module define basic library operations for files.  Only
tagging of files (not directories) are supported, and only pathnames (not
tagnames) are supported.

Specification
-------------

A file is tagged with a directory if and only if there exists at least one hard
link to the file in that directory.

A file A is tagged at a path B if and only if B refers to a link that
points to A.

"""

# pylint: disable=too-few-public-methods

import abc
import functools
import logging
import os
import posixpath

from dantalian import pathlib

_LOGGER = logging.getLogger(__name__)


def is_tagged_with(target, dirpath):
    """Return if target is tagged with dirpath."""
    for entry in pathlib.listdirpaths(dirpath):
        if posixpath.samefile(entry, target):
            return True
    return False


def tag_with(target, dirpath):
    """Tag target file with given directory.

    If file is already tagged, nothing happens.  This includes if the file is
    hardlinked in the directory under another name.

    Args:
        target: Path of file to tag.
        dirpath: Path of directory.

    """
    _LOGGER.debug('tag_with(%r, %r)', target, dirpath)
    if is_tagged_with(target, dirpath):
        return
    name = posixpath.basename(target)
    pathlib.free_name_do(dirpath, name, lambda dst: os.link(target, dst))


def untag_with(target, dirpath):
    """Remove tag from target file.

    If file is not tagged, nothing happens.  Remove *all* hard links to the
    file in the directory.

    Args:
        target: Path to target file.
        dirpath: Path to directory.

    """
    inode = os.lstat(target)
    for candidate in pathlib.listdirpaths(dirpath):
        candidate_inode = os.lstat(candidate)
        if posixpath.samestat(inode, candidate_inode):
            os.unlink(candidate)


def rename_all(basepath, target, newname):
    """Rename all links to the target file.

    Attempt to rename all links to the target file under the basepath to
    newname, finding a name as necessary.  If there are multiple links to the
    file in a given directory, the first will be renamed and the extras will be
    removed.

    Args:
        basepath: Base path for finding links.
        target: Path of file to rename.
        newname: New filename.

    """
    seen = set()
    for filepath in list_links(basepath, target):
        dirpath, _ = posixpath.split(filepath)
        if dirpath in seen:
            os.unlink(filepath)
            continue
        # pylint: disable=cell-var-from-loop
        pathlib.free_name_do(dirpath, newname,
                             lambda dst: pathlib.rename_safe(filepath, dst))
        seen.add(dirpath)


def remove_all(basepath, target):
    """Remove all links to the target file.

    Remove all links to the target file under the basepath.

    Args:
        basepath: Base path for finding links.
        target: Path of file to remove.

    """
    for filepath in list_links(basepath, target):
        os.unlink(filepath)


def list_links(basepath, target):
    """List paths for all links to the target file.

    Args:
        basepath: Base path for finding links.
        target: Path of file whose links to list.

    Returns:
        Generator yielding paths.
    """
    inode = os.lstat(target)
    for (dirpath, _, filenames) in os.walk(basepath):
        for name in filenames:
            filepath = posixpath.join(dirpath, name)
            if posixpath.samestat(inode, os.lstat(filepath)):
                yield filepath


def search(search_node):
    """Return paths by tag query.

    Args:
        search_node: Root Node of search query tree

    Returns:
        List of paths.
    """
    return list(search_node.get_results().values())


class SearchNode(metaclass=abc.ABCMeta):

    """Abstract class interface for search query node.

    Methods:
        get_results(): Get results of node query.
    """

    # pylint: disable=no-init

    @abc.abstractmethod
    def get_results(self):
        """Return a dictionary mapping inode objects to paths."""


class GroupNode(SearchNode, metaclass=abc.ABCMeta):

    """Abstract class for nodes that have a list of child nodes."""

    # pylint: disable=abstract-method

    def __init__(self, children):
        self.children = children

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                len(self.children) == len(other.children) and
                all(ours == theirs
                    for (ours, theirs) in zip(self.children, other.children)))


class AndNode(GroupNode):

    """
    AndNode merges the results of its children nodes by set intersection.
    """

    def get_results(self):
        results = self.children[0].get_results()
        inodes = (set(node.get_results()) for node in self.children)
        inodes = functools.reduce(set.intersection, inodes)
        return dict((inode, results[inode]) for inode in inodes)


class OrNode(GroupNode):

    """
    OrNode merges the results of its children nodes by set union.
    """

    def get_results(self):
        results = {}
        for node in self.children:
            pathmap = node.get_results()
            for inode in pathmap:
                if inode not in results:
                    results[inode] = pathmap[inode]
        return results


class MinusNode(GroupNode):

    """
    MinusNode returns the results of its first child minus the results of the
    rest of its children.
    """

    def get_results(self):
        results = self.children[0].get_results()
        for node in self.children[1:]:
            pathmap = node.get_results()
            for inode in pathmap:
                if inode in results:
                    del results[inode]
        return results


class DirNode(SearchNode):

    """
    DirNode returns the inodes and paths of the contents of the directory at
    its dirpath.
    """

    def __init__(self, dirpath):
        self.dirpath = dirpath

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.dirpath == other.dirpath)

    @staticmethod
    def _get_inode(filepath):
        """Return inode and path pair."""
        return (os.stat(filepath), filepath)

    def get_results(self):
        return dict(self._get_inode(filepath)
                    for filepath in pathlib.listdirpaths(self.dirpath))
