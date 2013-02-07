import os.path
import json
import logging

__all__ = ['FSNode', 'TagNode', 'maketree', 'fs2tag']
logger = logging.getLogger(__name__)


class FSNode:

    """
    Basically works like a dictionary mapping names to nodes.

    Implements:

    - __iter__
    - __getitem__
    - __setitem__
    """

    def __init__(self):
        self.children = {}

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, key):
        return self.children[key]

    def __setitem__(self, key, value):
        self.children[key] = value


class TagNode(FSNode):

    """
    TagNode subclasses FSNode.  TagNode adds a method, tagged(), which returns
    a generated dict mapping names to files that satisfy the TagNode's tags
    criteria, and adds these to __iter__ and __getitem__
    """

    def __init__(self, fs_root, tags):
        """
        tags is list of tags.  fs_root is a HitagiFS instance.
        """
        super().__init__()
        self.root = fs_root
        self.tags = tags

    def __iter__(self):
        files = list(super().__iter__(self.children))
        files.add(self.tagged().keys())
        return iter(files)

    def __getitem__(self, key):
        try:
            super().__getitem__(key)
        except KeyError:
            return self.tagged()[key]

    def tagged(self):
        return _uniqmap(self.root.find(self.tags))


def fs2tag(node, root, tags):
    x = TagNode(root, tags)
    x.children = dict(node.children)


def maketree(root, config):
    """Make a FSNode tree

    root is a HitagiFS instance.  config is file path.
    """
    logger.debug("maketree(%r, %r)", root, config)
    with open(config) as f:
        dat = json.load(f)
    r = FSNode()
    for x in dat:
        mount, tags = x['mount'], x['tags']
        logger.debug("doing %r, %r", mount, tags)
        mount = mount.lstrip('/').split('/')
        y = r
        for x in mount[:-1]:
            logger.debug("trying %r", x)
            try:
                y = y[x]
            except KeyError:
                logger.debug("making FSNode at %r", x)
                y[x] = FSNode()
        x = mount[-1]
        if x not in y:
            logger.debug("making TagNode at %r", x)
            y[x] = TagNode(root, tags)
        else:
            logger.debug("replacing node at %r", x)
            y[x] = fs2tag(y[x])
    return r


def _uniqmap(files):
    logger.debug("_uniqmap(%r)", files)
    map = {}
    unique = set(os.path.basename(f) for f in files)
    files = dict((f, os.path.basename(f)) for f in files)
    for f in unique:
        map[f] = files.pop(f)
    for f in files:
        file, ext = os.path.splitext(f)
        new = ''.join([file, ".{}", ext])
        i = 1
        while True:
            newi = new.format(i)
            if newi in map:
                i += 1
                continue
            else:
                map[newi] = files[f]
    logger.debug("calculated %r", files)
    return map
