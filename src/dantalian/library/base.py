"""
This module contains basic library operations.

These operations are defined only for tagging files with directories, with
the directories indicated by pathnames.
"""

import abc
from collections import deque
import functools
import logging
import os
import shlex

from dantalian import pathlib
from dantalian import errors

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

    Attempt to rename all links to the target file under the basepath to
    newname, finding a name as necessary.
    """
    for filepath in list_tags(basepath, target):
        # pylint: disable=cell-var-from-loop
        dirpath, _ = os.path.split(filepath)
        pathlib.free_name_do(dirpath, newname,
                             lambda dest: os.rename(filepath, dest))


def remove(basepath, target):
    """Remove all links to the target file.

    Remove all links to the target file under the basepath.
    """
    for filepath in list_tags(basepath, target):
        try:
            os.unlink(filepath)
        except OSError as err:
            _LOGGER.error("Could not remove {}: {}".format(filepath, err))


def list_tags(basepath, target):
    """List all links to the target file."""
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
        Files by path.
    """
    return list(search_node.get_results().values())


def parse_query(query):
    r"""Parse query string into query node tree.

    Query strings look like:

        'AND foo bar OR spam eggs ) AND \AND \OR \) \\\) ) )'

    which parses to:

        AndNode(
            DirNode('foo'),
            DirNode('bar'),
            OrNode(
                DirNode('spam'),
                DirNode('eggs')),
            AndNode(
                DirNode('AND'),
                DirNode('OR')),
                DirNode(')'),
                DirNode('\\)'))
    """
    tokens = deque(shlex.split(query))
    parse_stack = []
    parse_list = []
    while tokens:
        token = tokens.popleft()
        _LOGGER.debug("Parsing token %s", token)
        if token[0] == '\\':
            token = token[1:]
            parse_list.append(DirNode(token))
        elif token == 'AND':
            parse_stack.append(parse_list)
            parse_stack.append(AndNode)
            parse_list = []
        elif token == 'OR':
            parse_stack.append(parse_list)
            parse_stack.append(OrNode)
            parse_list = []
        elif token == ')':
            node_type = parse_stack.pop()
            node = node_type(parse_list)
            parse_list = parse_stack.pop()
            parse_list.append(node)
        else:
            parse_list.append(DirNode(token))
    if len(parse_list) != 1:
        raise errors.ParseError(parse_stack, parse_list,
                                "Not exactly one node at top of parse")
    return parse_list[0]


class SearchNode(metaclass=abc.ABCMeta):

    """Abstract class interface of search query node.

    Methods:
        get_results(): Get results of node query.
    """

    # pylint: disable=no-init,too-few-public-methods

    @abc.abstractmethod
    def get_results(self):
        """Return a dictionary mapping inode objects to paths."""


class GroupNode(SearchNode, metaclass=abc.ABCMeta):

    """Abstract class for nodes that have a list of child nodes."""

    # pylint: disable=too-few-public-methods,abstract-method

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

    # pylint: disable=too-few-public-methods

    def get_results(self):
        if not self.children:
            return dict()
        pathmap = self.children[0].get_results()
        inodes = (set(node.get_results()) for node in self.children)
        inodes = functools.reduce(set.intersection, inodes)
        return dict((inode, pathmap[inode]) for inode in inodes)


class OrNode(GroupNode):

    """
    OrNode merges the results of its children nodes by union.
    """

    # pylint: disable=too-few-public-methods

    def get_results(self):
        results = {}
        for node in self.children:
            pathmap = node.get_results()
            for inode in pathmap:
                if inode not in results:
                    results[inode] = pathmap[inode]
        return results


class DirNode(SearchNode):

    """
    DirNode gets the inodes and paths of the directory at its dirpath.
    """

    # pylint: disable=too-few-public-methods

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
