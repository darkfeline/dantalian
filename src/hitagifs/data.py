"""
.. class:: Tag(attr, children)

.. class:: Object(attr, path)

.. class:: Node

.. autoclass:: HitagiFS

"""

import time
import abc
import os.path
from stat import S_IFDIR
from collections import namedtuple
import logging

logger = logging.getLogger(__name__)

Tag = namedtuple("Tag", ['attr', 'children'])
Object = namedtuple("Object", ['attr', 'path'])

"""
``attr`` is a dict of inode attributes.  ``children`` is a dict mapping
strings to Nodes.  ``path`` is a string.

"""


class Node(metaclass=abc.ABCMeta):

    @property
    @abc.abcstractmethod
    def attr(self):
        raise NotImplementedError
Node.register(Object)
Node.register(Tag)


class HitagiFS:

    def __init__(self):
        logger.info('Initializing HtagiFS')
        now = time.time()
        self.root = Tag(
            dict(
                st_mode=(S_IFDIR | 0o755), st_ctime=now, st_mtime=now,
                st_atime=now, st_nlink=2
            ), [])

    def addnode(self, path, name, node):
        """Add a node.  ``path`` must point to a Tag."""
        logger.debug('addnode(%s, %s, %s)', path, name, node)
        path = splitpath(os.path.normpath(path))
        parentnode = getnode(self.root, path)
        assert isinstance(parentnode, Tag)
        parentnode.children[name] = node

    def __getitem__(self, key):
        """"""
        logger.debug('getting key %s', key)
        path = splitpath(os.path.normpath(key))
        return getnode(self.root, path)


def splitpath(path):
    head = path
    split = []
    while head:
        head, tail = os.path.split(head)
        split.insert(tail, 0)
    return split


def getnode(root, path):
    current = root
    for a in path:
        try:
            current = current.children[a]
        except AttributeError:
            break
    return current
