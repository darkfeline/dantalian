"""
This module contains stuff used for managing FUSE virtual space.  The
protocol for nodes is as follows.

FSNodes are purely virtual.  Their children are other nodes.

BorderNodes bridge into real file system space.  They may have also have
strings as children, which are absolute paths into real file system
space.

Node behavior
-------------

Nodes implement the methods for a mapping data model (i.e., __getitem__,
__setitem__, __delitem__).

The keys are strings with file names (like in file systems/directory
tables).

The values are strings with the paths to files and directories on the
actual file system, and node objects for nodes.

"""

import os
import logging
import stat
import abc
from time import time
from itertools import chain

from dantalian import path as libpath

__all__ = ['FSNode', 'TagNode', 'BorderNode', 'RootNode', 'fs2tag', 'split']
logger = logging.getLogger(__name__)
UMASK = 0o007


class FSNode:

    """
    Mock directory.  FSNode works like a dictionary mapping names to
    nodes and keeps some internal file attributes.

    Implements:

    * __iter__
    * __getitem__
    * __setitem__
    * __delitem__

    File Attributes:

    atime, ctime, mtime
        Defaults to current time
    uid, gid
        Defaults to process's uid, gid
    mode
        Set directory bit, and permission bits 0o777 minus umask
    nlinks
        Only keeps track of nodes, not TagNode directories
    size
        constant 4096

    """

    def __init__(self):
        self.children = {}
        now = time()
        self.attr = dict(
            st_atime=now,
            st_ctime=now,
            st_mtime=now,
            st_uid=os.getuid(),
            st_gid=os.getgid(),
            st_mode=stat.S_IFDIR | 0o770 & ~UMASK,
            st_nlink=2,
            st_size=4096)

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, key):
        return self.children[key]

    def __setitem__(self, key, value):
        self.children[key] = value
        self.attr['st_nlink'] += 1

    def __delitem__(self, key):
        del self.children[key]
        self.attr['st_nlink'] -= 1


class BorderNode(FSNode, metaclass=abc.ABCMeta):
    """
    BorderNode is an abstract class for subclasses of FSNode which reach
    outsie of the virtual space

    """


class TagNode(BorderNode):

    """
    TagNode adds a method, tagged(), which returns a generated dict
    mapping names to files that satisfy the TagNode's tags criteria, and
    adds these to __iter__ and __getitem__

    """

    def __init__(self, root, tags):
        """
        tags is list of tags.  root is a library.
        """
        super().__init__()
        self.root = root
        self.tags = tags

    def __iter__(self):
        return chain(super().__iter__(), self._tagged().keys())

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return self._tagged()[key]

    def _tagged(self):
        return _uniqmap(self.root.find(self.tags))


class RootNode(BorderNode):

    """
    A special Node that doesn't actually look for tags, merely
    projecting the library root into virtual space.

    """

    def __init__(self, root):
        super().__init__()
        assert not isinstance(root, str)
        self.root = root
        self[libpath.fuserootdir('')] = libpath.rootdir(root.root)

    def __iter__(self):
        return chain(super().__iter__(), self._files())

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError as e:
            if key in self.files():
                return os.path.join(self.root.root, key)
            else:
                raise KeyError("{!r} not found".format(key)) from e

    def _files(self):
        return os.listdir(self.root.root)


def fs2tag(node, root, tags):
    """Convert a FSNode instance to a TagNode instance"""
    x = TagNode(root, tags)
    x.children.update(dict(node.children))
    return x


def split(tree, path):
    """Get node and path components

    Args:
        tree (RootNode): Root node.
        path (str): Path.

    Returns:
        (cur, path), where `cur` is the furthest node along the path,
        and `path` is a list of strings indicating the path from the
        given node.  If node is the last file in the path, path is an
        empty list.

        If path is broken, returns None instead.

    """
    assert len(path) > 0
    assert path[0] == "/"
    logger.debug("resolving path %r", path)
    path = [x for x in path.lstrip('/').split('/') if x != ""]
    logger.debug("path list %r", path)
    cur = tree
    while path:
        logger.debug("resolving %r", path[0])
        try:
            a = cur[path[0]]
        except KeyError:
            logger.warn("path broken")
            return None
        if isinstance(a, str):
            logger.debug("BorderNode found, %r, %r", cur, path)
            return (cur, path)
        else:
            logger.debug("next node")
            cur = a
            del path[0]
    logger.debug("found node %r", cur)
    return (cur, [])


def _uniqmap(files):
    """Create a mapping of unique names to paths.

    Args:
        files (list): List of path strings.

    Returns:
        dict

    """
    logger.debug("_uniqmap(%r)", files)
    map = {}
    names_seen = []
    while files:
        f = files.pop(0)
        logger.debug("doing %r", f)
        name = os.path.basename(f)
        if name not in names_seen:
            logger.debug("no collision; adding")
            names_seen.append(name)
            map[name] = f
        else:
            logger.debug("collision; changing")
            new = libpath.fuse_resolve(f)
            if new in map:
                logger.debug("redoing %r", map[new])
                files.append(map[new])
            names_seen.append(new)
            map[new] = f
    return map
