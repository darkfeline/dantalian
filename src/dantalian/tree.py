"""
tree.py
=======

This module contains stuff used for managing FUSE virtual space.  The protocol
for nodes is as follows.

Nodes map strings to items.  The key strings are file names (similar to file
systems).

FSNodes are purely virtual.  Their children are other nodes.

BorderNodes bridge into real file system space.  They may have also have
strings as children, which are absolute paths into real file system space.

"""

import os
import logging
import stat
import abc
from time import time

from dantalian import path as libpath

__all__ = ['FSNode', 'TagNode', 'BorderNode', 'RootNode', 'fs2tag']
logger = logging.getLogger(__name__)
UMASK = 0o007


class FSNode:

    """
    Mock directory.  FSNode works like a dictionary mapping names to nodes and
    keeps some internal file attributes.

    Implements:

    - __iter__
    - __getitem__
    - __setitem__

    File Attributes:

    atime, ctime, mtime
        Defaults to current time
    uid, gid
        Defaults to process's uid, gid
    mode
        Set directory, 0o777 minus umask
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


class BorderNode(FSNode, metaclass=abc.ABCMeta):
    """
    BorderNode is an abstract class for subclasses of FSNode which reach outsie
    of the virtual space"""


class TagNode(BorderNode):

    """
    TagNode adds a method, tagged(), which returns a generated dict mapping
    names to files that satisfy the TagNode's tags criteria, and adds these to
    __iter__ and __getitem__
    """

    def __init__(self, root, tags):
        """
        tags is list of tags.  root is a library.
        """
        super().__init__()
        self.root = root
        self.tags = tags

    def __iter__(self):
        files = list(super().__iter__())
        files.extend(self.tagged().keys())
        return iter(files)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return self.tagged()[key]

    def tagged(self):
        return _uniqmap(self.root.find(self.tags))


class RootNode(BorderNode):

    """
    A special TagNode that doesn't actually look for tags, merely projecting
    the library root into virtual space
    """

    def __init__(self, root):
        super().__init__()
        assert not isinstance(root, str)
        self.root = root
        self[libpath.fuserootdir('')] = libpath.rootdir(root.root)

    def __iter__(self):
        files = list(super().__iter__())
        files.extend(self.files())
        return iter(files)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            if key in self.files():
                return os.path.join(self.root.root, key)
            else:
                raise KeyError("{!r} not found".format(key))

    def files(self):
        return os.listdir(self.root.root)


def fs2tag(node, root, tags):
    """Convert a FSNode instance to a TagNode instance"""
    x = TagNode(root, tags)
    x.children.update(dict(node.children))
    return x


def _uniqmap(files):
    """Create a unique map from an iterator of files.

    Given a list of files, map unique basename strings to each file and return
    a dictionary."""
    logger.debug("_uniqmap(%r)", files)
    files = list(files)
    map = {}
    uniqmap = {}
    while len(files) > 0:
        f = files[0]
        logger.debug("doing %r", f)
        base = os.path.basename(f)
        if base not in map and base not in uniqmap:
            logger.debug("no collision; adding")
            map[base] = f
            del files[0]
        else:
            logger.debug("collision; changing")
            new = _makeuniq(f)
            assert new not in uniqmap
            uniqmap[new] = f
            del files[0]
            if new in map:
                logger.debug("collision with unchanged name; redoing later")
                files.append(map[new])
                del map[new]
    return map


def _makeuniq(path):
    """Return the base file name with inode added."""
    base = os.path.basename(path)
    file, ext = os.path.splitext(base)
    inode = os.lstat(path).st_ino
    return ''.join([base, '.', inode, ext])
