"""
This module contains basic library operations.
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
    """Tag target with given directory.

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
    while True:
        dest = os.path.join(dirpath, pathlib.resolve_name(dirpath, name))
        try:
            os.link(target, dest)
        except FileExistsError:
            continue
        else:
            break


def untag(target, dirpath):
    """Remove tag from target.

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


def search(search_node):
    """Return files by tag query.

    Args:
        search_node: Root Node of search query tree

    Returns:
        Files by path.
    """
    return list(search_node.get_results().values())


def parse_query(query):
    """Parse query string into query node tree."""
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


class AndNode(SearchNode):

    """
    AndNode merges the results of its children nodes by intersection.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, children):
        self.children = children

    def get_results(self):
        if not self.children:
            return dict()
        pathmap = self.children[0].get_results()
        inodes = (set(node.get_results()) for node in self.children)
        inodes = functools.reduce(set.intersection, inodes)
        return dict((inode, pathmap[inode]) for inode in inodes)


class OrNode(SearchNode):

    """
    OrNode merges the results of its children nodes by union.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, children):
        self.children = children

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

    def get_results(self):
        return dict((os.lstat(filepath), filepath)
                    for filepath in pathlib.listdirpaths(self.dirpath))
