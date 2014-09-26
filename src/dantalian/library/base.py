"""
This module contains basic library operations.
"""

import abc
import functools
import itertools
import os

from dantalian import pathlib


def tag(target, tagpath):
    """Tag target with given tag.

    Args:
        target: Path of file to tag.
        tagpath: Path of tag.

    If file is already tagged, nothing happens.  This includes if
    the file is hardlinked in the respective directory under
    another name.
    """
    for entry in pathlib.listdirpaths(tagpath):
        if os.path.samefile(entry, target):
            return
    name = os.path.basename(target)
    while True:
        dest = os.path.join(tagpath, pathlib.resolve_name(tagpath, name))
        try:
            os.link(target, dest)
        except FileExistsError:
            continue
        else:
            break


def untag(target, tagpath):
    """Remove tag from target.

    Args:
        target: Path to target file.
        tagpath: Path to tag.

    If file is not tagged, nothing happens.  Remove *all* hard
    links to the file in the directory corresponding to the given
    tag.
    """
    inode = os.lstat(target)
    for candidate in pathlib.listdirpaths(tagpath):
        candidate_inode = os.lstat(candidate)
        if os.path.samestat(inode, candidate_inode):
            os.unlink(candidate)


def query(search_node):
    """Return files by tag query.

    Args:
        search_node: Root Node of search query tree

    Returns:
        Files by path.
    """
    return list(search_node.get_results().values())


class SearchNode(metaclass=abc.ABCMeta):

    """Abstract class interface of search query node.

    Methods:
        get_results(): Get results of node query.
    """

    @abc.abstractmethod
    def get_results(self):
        """Return a dictionary mapping inode objects to paths."""


class AndNode(SearchNode):

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


class TagNode(SearchNode):

    def __init__(self, tagpath):
        self.tagpath = tagpath

    def get_results(self):
        return dict((os.lstat(filepath), filepath)
                    for filepath in pathlib.listdirpaths(self.tagpath))
