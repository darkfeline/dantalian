"""
This module contains basic library operations.

The functions in this module define basic library operations for files "tagged"
by links in directories.  Only tagging of files (not directories) are
supported, and only pathnames (not tagnames) are supported.
"""

# pylint: disable=too-few-public-methods

import abc
import functools
import logging
import os

from dantalian import pathlib

_LOGGER = logging.getLogger(__name__)


def tag(target, dirpath):
    """Tag target file with given directory.

    Args:
        target: Path of file to tag.
        dirpath: Path of directory.

    If file is already tagged, nothing happens.  This includes if
    the file is hardlinked in the directory under
    another name.
    """
    for entry in pathlib.listdirpaths(dirpath):
        if os.path.samefile(entry, target):
            return
    name = os.path.basename(target)
    pathlib.free_name_do(dirpath, name, lambda dest: os.link(target, dest))


def untag(target, dirpath):
    """Remove tag from target file.

    Args:
        target: Path to target file.
        dirpath: Path to directory.

    If file is not tagged, nothing happens.  Remove *all* hard
    links to the file in the directory.
    """
    inode = os.lstat(target)
    for candidate in pathlib.listdirpaths(dirpath):
        candidate_inode = os.lstat(candidate)
        if os.path.samestat(inode, candidate_inode):
            os.unlink(candidate)


def rename(basepath, target, newname):
    """Rename all links to the target file.

    Args:
        basepath: Base path for tag conversions.
        target: Path of file to rename.
        newname: New filename.

    Attempt to rename all links to the target file under the basepath to
    newname, finding a name as necessary.
    """
    def func(dst):
        # pylint: disable=missing-docstring
        # pylint: disable=undefined-loop-variable
        pathlib.rename_safe(filepath, dst)
    for filepath in list_tags(basepath, target):
        dirpath, _ = os.path.split(filepath)
        pathlib.free_name_do(dirpath, newname, func)


def remove(basepath, target):
    """Remove all links to the target file.

    Args:
        basepath: Base path for tag conversions.
        target: Path of file to remove.

    Remove all links to the target file under the basepath.
    """
    for filepath in list_tags(basepath, target):
        try:
            os.unlink(filepath)
        except OSError as err:
            _LOGGER.error("Could not remove %s: %s", filepath, err)


def list_tags(basepath, target):
    """List all links to the target file.

    Args:
        basepath: Base path for tag conversions.
        target: Path of file whose tags to list.

    Returns:
        Generator yielding paths.
    """
    inode = os.lstat(target)
    for (dirpath, _, filenames) in os.walk(basepath):
        for name in filenames:
            filepath = os.path.join(dirpath, name)
            if os.path.samestat(inode, os.lstat(filepath)):
                yield filepath


def search(search_node):
    """Return files by tag query.

    Args:
        search_node: Root Node of search query tree

    Returns:
        List of paths.
    """
    return list(search_node.get_results().values())


class SearchNode(metaclass=abc.ABCMeta):

    """Abstract class interface of search query node.

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
    AndNode merges the results of its children nodes by intersection.
    """

    def get_results(self):
        pathmap = self.children[0].get_results()
        inodes = (set(node.get_results()) for node in self.children)
        inodes = functools.reduce(set.intersection, inodes)
        return dict((inode, pathmap[inode]) for inode in inodes)


class OrNode(GroupNode):

    """
    OrNode merges the results of its children nodes by union.
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
    DirNode gets the inodes and paths of the directory at its dirpath.
    """

    def __init__(self, dirpath):
        self.dirpath = dirpath

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.dirpath == other.dirpath)

    @staticmethod
    def _get_inode(filepath):
        """Return inode and path pair."""
        return (os.lstat(filepath), filepath)

    def get_results(self):
        return dict(self._get_inode(filepath)
                    for filepath in pathlib.listdirpaths(self.dirpath))
