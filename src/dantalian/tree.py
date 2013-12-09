import os
import logging
import stat
import abc
from time import time
from itertools import chain

from dantalian import path as dpath

__all__ = []
logger = logging.getLogger(__name__)
UMASK = 0o007


def _public(f):
    __all__.append(f.__name__)
    return f


@_public
class BaseNode(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __iter__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def __setitem__(self, key, value):
        raise NotImplementedError

    @abc.abstractmethod
    def __delitem__(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def dump(self):
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def load(root, node):
        raise NotImplementedError

    def _dump_recur(self):
        """Recursive dump of children

        Values in children dict can be str (path), so won't have dump method.

        """
        return dict((x, self[x].dump()) for x in self.children if
                    hasattr(self[x], 'dump'))

    def get(self, path):
        """Get node and path components

        Parameters
        ----------
        path : str
            Path.

        Returns
        -------
        (cur, path, ret) : tuple
            `cur` is the furthest node along the path, and `path` is a
            list of strings indicating the path from the given node (the
            same list object that was passed in).  If node is the last
            file in the path, path is an empty list.

            `ret` is the return code.  0 means successful, 1 means path
            is broken, in which case `cur` goes up to the furthest node
            where the path broke and `path` contains the remaining path
            components.

        """
        assert len(path) > 0
        assert path[0] == "/"
        path = [x for x in path.lstrip('/').split('/') if x != ""]
        return self._get(path)

    def _get(self, path_list):
        logger.debug("path list %r", path_list)
        try:
            next = path_list[0]
        except IndexError:  # case done
            return (self, path_list, 0)
        try:
            next = self[next]
        except KeyError:  # case broken path
            return (self, path_list, 1)
        if isinstance(next, str):  # case no more nodes
            return (self, path_list, 0)
        else:  # case more nodes
            path_list.pop(0)
            return next._get(path_list)


_load_map = {}


def _add_map(name):
    def adder(f):
        _load_map[name] = f
        return f
    return adder


@_public
def load(root, nodes):
    """
    Parameters
    ----------
    root : Library
        Library instance to use for RootNode
    nodes : list
        JSON dump of node tree

    """
    return _load_map[nodes[0]](root, nodes)


@_public
class Node(BaseNode):

    """
    Mock directory.  Node works like a dictionary mapping names to
    nodes and keeps some internal file attributes.

    File Attributes
    ---------------
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

    def dump(self):
        """Dump object.

        Dumps the node in the following format::

            ['Node', {name: child}]

        """
        return ['Node', self._dump_recur()]

    @staticmethod
    @_add_map('Node')
    def load(root, node):
        x = Node()
        for k in node[-1]:
            x[k] = load(root, node[-1][k])
        return x


@_public
class BorderNode(Node, metaclass=abc.ABCMeta):
    """Abstract class for nodes that bridge the file system"""


@_public
class RootNode(BorderNode):

    """
    A special Node that doesn't actually look for tags, merely
    projecting the library root into virtual space.

    """

    def __init__(self, root):
        """
        Parameters
        ----------
        root : Library
            Library for root

        """
        super().__init__()
        assert not isinstance(root, str)
        self.root = root
        self[root.fuserootdir('')] = root.rootdir(root.root)

    def __iter__(self):
        return chain(super().__iter__(), self._files())

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError as e:
            if key in self._files():
                return os.path.join(self.root.root, key)
            else:
                raise KeyError("{!r} not found".format(key)) from e

    def _files(self):
        return os.listdir(self.root.root)

    def dump(self):
        """Dump object.

        Dumps the node in the following format::

            ['RootNode', {name: child}]

        """
        return ['RootNode', self._dump_recur()]

    @staticmethod
    @_add_map('RootNode')
    def load(root, node):
        x = RootNode(root)
        for k in node[-1]:
            x[k] = load(root, node[-1][k])
        return x


@_public
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

    def dump(self):
        """Dump object.

        Dumps the node in the following format::

            ['TagNode', [tag], {name: child}]

        """
        return ['TagNode', self.tags, self._dump_recur()]

    @staticmethod
    @_add_map('TagNode')
    def load(root, node):
        x = TagNode(root, node[1])
        for k in node[-1]:
            x[k] = load(root, node[-1][k])
        return x


@_public
def fs2tag(node, root, tags):
    """Convert a Node instance to a TagNode instance"""
    x = TagNode(root, tags)
    x.children.update(node.children)
    return x


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
            # TODO check this logic here
            new = dpath.fuse_resolve(f)
            if new in map:
                logger.debug("redoing %r", map[new])
                files.append(map[new])
            names_seen.append(new)
            map[new] = f
    return map
