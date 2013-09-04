"""
This module defines the FUSE operations dantalian uses.  Thus, how FUSE
behaves is defined here.

"""

from dantalian.fuse import FUSE, Operations, FuseOSError, LoggingMixIn

from errno import ENOENT, EINVAL
import os
import tempfile
import logging
from time import time

from dantalian import tree

__all__ = ['TagOperations', 'mount']
ATTRS = ('st_atime', 'st_ctime', 'st_mtime', 'st_uid', 'st_gid', 'st_mode',
         'st_nlink', 'st_size', 'st_ino')
logger = logging.getLogger(__name__)


class TagOperations(LoggingMixIn, Operations):

    def __init__(self, root, tree):
        """Initialize TagOperations instance.

        Args:
            root (BaseLibrary): Library instance.
            tree (RootNode): RootNode of node tree.

        """
        self.root = root
        self.tree = tree

    def chmod(self, path, mode):
        logger.debug("chmod(%r, %r)", mode)
        node, path = self._getnode(path)
        os.chmod(_getpath(node, path), mode)

    def chown(self, path, uid, gid):
        logger.debug("chown(%r, %r, %r)", path, uid, gid)
        node, path = self._getnode(path)
        os.chown(_getpath(node, path), uid, gid)

    def create(self, path, mode):
        logger.debug("create(%r, %r)", path, mode)
        path, file = os.path.split(path)
        node, path = self._getnode(os.path.dirname(path))
        path.append(file)
        if len(path) == 1 and isinstance(node, tree.TagNode):
            t = list(node.tags)
            path = os.path.join(self.root.tagpath(t.pop(0)), file)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT, mode)
            for tag in t:
                self.root.tag(path, tag)
            return fd
        else:
            fd = os.open(_getpath(node, path), os.O_WRONLY | os.O_CREAT, mode)
            return fd

    def getattr(self, path, fh=None):
        logger.debug("getattr(%r, %r)", path, fh)
        node, path = self._getnode(path)
        if path:
            logger.debug("getting from file system")
            st = os.lstat(_getpath(node, path))
            return dict((key, getattr(st, key)) for key in ATTRS)
        else:
            logger.debug("getting from node")
            return node.attr

    getxattr = None
    listxattr = None

    def link(self, source, target):
        logger.debug("link(%r, %r)", source, target)
        source, file = os.path.split(source)
        tnode, tpath = self._getnode(target)
        snode, spath = self._getnode(source)
        spath.append(file)
        target = _getpath(tnode, tpath)
        # to Tag
        if len(spath) == 1 and isinstance(snode, tree.TagNode):
            for tag in list(snode.tags):
                self.root.tag(target, tag)
        # to Outside
        else:
            source = _getpath(snode, spath)
            logger.debug("linking %r to %r", target, source)
            os.link(target, source)

    def mkdir(self, path, mode):
        logger.debug("mkdir(%r, %r)", path, mode)
        node, path = self._getnode(path)
        if len(path) == 1 and isinstance(node, tree.TagNode):
            t = list(node.tags)
            path = os.path.join(self.root.tagpath(t.pop(0)), *path)
            fd = os.mkdir(path, mode)
            self.root.convert(path)
            for tag in t:
                self.root.tag(path, tag)
            return fd
        else:
            fd = os.mkdir(_getpath(node, path), mode)

    def open(self, path, flags):
        logger.debug("open(%r, %r)", path, flags)
        node, path = self._getnode(path)
        return os.open(_getpath(node, path), flags)

    def read(self, path, size, offset, fh):
        logger.debug("read(%r, %r, %r, %r)", path, size, offset, fh)
        os.lseek(fh, offset, 0)
        return os.read(fh, size)

    def readdir(self, path, fh):
        logger.debug("readdir(%r, %r)", path, fh)
        node, path = self._getnode(path)
        contents = ['.', '..']
        if path:
            contents += os.listdir(_getpath(node, path))
        else:
            node.attr['st_atime'] = time()
            contents += [x for x in iter(node)]
        return contents

    def readlink(self, path):
        logger.debug("readlink(%r)", path)
        node, path = self._getnode(path)
        return os.readlink(_getpath(node, path))

    removexattr = None

    def rename(self, old, new):
        logger.debug("rename(%r, %r)", old, new)
        onode, opath = self._getnode(old)
        nnode, npath = self._getnode(new)
        # Nodes raise error here
        old = _getpath(onode, opath)
        new = _getpath(nnode, npath)
        # to Tag
        if len(npath) == 1 and isinstance(nnode, tree.TagNode):
            # from Tag
            if len(opath) == 1 and isinstance(onode, tree.TagNode):
                old = self._tmplink(old)
                for tag in list(onode.tags):
                    self.root.untag(old, tag)
            for tag in list(nnode.tags):
                self.root.tag(old, tag)
            os.remove(old)
        # to Outside
        else:
            os.rename(old, new)
            # from Tag
            if len(opath) == 1 and isinstance(onode, tree.TagNode):
                for tag in list(onode.tags):
                    self.root.untag(new, tag)

    def rmdir(self, path):
        logger.debug("rmdir(%r)", path)
        node, path = self._getnode(path)
        os.rmdir(_getpath(node, path))

    setxattr = None

    def statfs(self, path):
        logger.debug("statfs(%r)", path)
        stv = os.statvfs(path)
        return dict((key, getattr(stv, key)) for key in (
            'f_bavail', 'f_bfree', 'f_blocks', 'f_bsize', 'f_favail',
            'f_ffree', 'f_files', 'f_flag', 'f_frsize', 'f_namemax'))

    def symlink(self, source, target):
        logger.debug("symlink(%r, %r)", source, target)
        source, file = os.path.split(source)
        node, path = self._getnode(source)
        if len(path) == 1 and isinstance(node, tree.TagNode):
            t = list(node.tags)
            source = os.path.join(self.root.tagpath(t.pop(0)), file)
            os.symlink(target, source)
            for tag in t:
                self.root.tag(path, tag)
        else:
            source = _getpath(node, path)
            os.symlink(target, source)

    def truncate(self, path, length, fh=None):
        logger.debug("truncate(%r, %r, %r)", path, length, fh)
        node, path = self._getnode(path)
        if path:
            with open(_getpath(node, path), 'r+') as f:
                f.truncate(length)
        else:
            raise FuseOSError(EINVAL)

    def unlink(self, path):
        logger.debug("unlink(%r)", path)
        node, path = self._getnode(path)
        file = _getpath(node, path)
        if len(path) == 1 and isinstance(node, tree.TagNode):
            file = self._tmplink(file)
            for tag in node.tags:
                self.root.untag(file, tag)
            os.remove(file)
        else:
            logger.debug("outside; unlinking %r", file)
            os.unlink(file)

    def utimens(self, path, times=None):
        logger.debug("utimens(%r, %r)", path, times)
        node, path = self._getnode(path)
        os.utime(_getpath(node, path), times)

    def write(self, path, data, offset, fh):
        logger.debug("write(%r, %r, %r, %r)", path, data, offset, fh)
        node, path = self._getnode(path)
        if path:
            os.lseek(fh, offset, 0)
            return os.write(fh, data)
        else:
            raise FuseOSError(EINVAL)

    def _getnode(self, path):
        x = tree.split(self.tree, path)
        if not x:
            raise FuseOSError(ENOENT)
        else:
            return x

    def _tmplink(self, target):
        logger.debug("_tmplink(%r)", target)
        while True:
            fh, path = tempfile.mkstemp(dir=self.root.root)
            logger.debug("trying %r", path)
            os.close(fh)
            os.remove(path)
            try:
                os.link(target, path)
            except FileExistsError:
                logger.debug("no good")
                continue
            else:
                logger.debug("%r tmpfile works", path)
                return path


def _getpath(node, path):
    """Get real path

    Calculate and return the real path given BorderNode `node` and list
    of strings `path`.  If `node` is not a BorderNode or `path` is
    empty, raise FuseOSError(EINVAL).  This is used internally when
    trying to resolve real, non-virtual, outside paths.

    """
    if not isinstance(node, tree.BorderNode) or len(path) == 0:
        raise FuseOSError(EINVAL)
    return os.path.join(node[path[0]], *path[1:])


def mount(path, root, tree):
    return FUSE(TagOperations(root, tree), path, foreground=True, use_ino=True)
