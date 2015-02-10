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

"""This module implements searching and queries."""

# pylint: disable=too-few-public-methods

import abc
from collections import deque
import functools
import logging
import os
import shlex

from dantalian import pathlib
from dantalian import tagnames

_LOGGER = logging.getLogger(__name__)


def search(search_node):
    """Return paths by tag query.

    Args:
        search_node: Root Node of search query tree

    Returns:
        List of paths.
    """
    return list(search_node.get_results().values())


class SearchNode(metaclass=abc.ABCMeta):

    """Abstract interface for search query nodes.

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
    DirNode returns the inodes and paths of the contents of its directory.
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


def parse_query(rootpath, query):
    r"""Parse query string into query node tree.

    Parent node syntax:

        NODE foo [bar...] END

    where NODE is AND, OR, or MINUS

    Tokens beginning with a backslash are used directly in DirNodes.
    Everything else parses to a DirNode, but with tagname conversion.

    Query strings look like:

        'AND foo bar OR spam eggs END AND \AND \OR \END \\\END ) )'

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
                DirNode('END'),
                DirNode('\\END'))

    Args:
        rootpath: Rootpath for tag conversions.
        query: Search query string.

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
        elif token == 'MINUS':
            parse_stack.append(parse_list)
            parse_stack.append(MinusNode)
            parse_list = []
        elif token == 'END':
            node_type = parse_stack.pop()
            node = node_type(parse_list)
            parse_list = parse_stack.pop()
            parse_list.append(node)
        else:
            token = tagnames.path(rootpath, token)
            parse_list.append(DirNode(token))
    if len(parse_list) != 1:
        raise ParseError(parse_stack, parse_list,
                         "Not exactly one node at top of parse")
    return parse_list[0]


class ParseError(Exception):

    """Error parsing query."""

    def __init__(self, parse_stack, parse_list, msg=''):
        super().__init__()
        self.parse_stack = parse_stack
        self.parse_list = parse_list
        self.msg = msg

    def __str__(self):
        return "{}\nstack={}\nlist={}".format(
            self.msg, self.parse_stack, self.parse_list)

    def __repr__(self):
        return "ParseError({!r}, {!r}, {!r})".format(
            self.parse_stack, self.parse_list, self.msg)
