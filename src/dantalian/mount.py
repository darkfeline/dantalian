from dantalian.fuse import FUSE, Operations, FuseOSError, LoggingMixIn

from errno import ENOENT, EPERM, EINVAL
import os
import tempfile
import logging
from time import time

from dantalian import tree

__all__ = ['TagOperations', 'mount']
ATTRS = ('st_atime', 'st_ctime', 'st_mtime', 'st_uid', 'st_gid', 'st_mode',
         'st_nlink', 'st_size')
logger = logging.getLogger(__name__)


class TagOperations(LoggingMixIn, Operations):

    def __init__(self, root, tree):
        """
        root is Library instance
        """
        self.root = root
        self.tree = tree

    def chmod(self, path, mode):
        """chmod

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Otherwise the operation is invalid and raises
        EINVAL.
        """
        logger.debug("chmod(%r, %r)", mode)
        node, path = self._getnode(path)
        if path:
            os.chmod(_getpath(node, path), mode)
        else:
            logger.warn("is node")
            raise FuseOSError(EINVAL)

    def chown(self, path, uid, gid):
        """chown

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Otherwise the operation is invalid and raises
        EINVAL.
        """
        logger.debug("chown(%r, %r, %r)", path, uid, gid)
        node, path = self._getnode(path)
        if path:
            os.chown(_getpath(node, path), uid, gid)
        else:
            logger.warn("is node")
            raise FuseOSError(EINVAL)

    def create(self, path, mode):
        """create

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Once a file is created, it is tagged with all of
        the tags of the furthest node and return the file's file descriptor.
        Otherwise the operation is invalid and raises EINVAL.
        """
        logger.debug("create(%r, %r)", path, mode)
        node, path = self._getnode(path)
        if path:
            t = list(node.tags)
            path = os.path.join(self.root.tagpath(t.pop(0)), *path)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT, mode)
            for tag in t:
                self.root.tag(path, tag)
            return fd
        else:
            raise FuseOSError(EINVAL)

    def getattr(self, path, fh=None):
        """getattr

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Otherwise if path is a node, return the node's
        tracked attributes.
        """
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

    def mkdir(self, path, mode):
        """mkdir

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Once a directory is created, it is converted and
        tagged with all of the tags of the furthest node.  Otherwise the
        operation is invalid and raises EINVAL.
        """
        logger.debug("mkdir(%r, %r)", path, mode)
        node, path = self._getnode(path)
        if path:
            t = list(node.tags)
            path = os.path.join(self.root.tagpath(t.pop(0)), *path)
            fd = os.mkdir(path, mode)
            self.root.convert(path)
            for tag in t:
                self.root.tag(path, tag)
            return fd
        else:
            raise FuseOSError(EINVAL)

    def open(self, path, flags):
        """open

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Otherwise the operation is invalid and raises
        EINVAL.
        """
        logger.debug("open(%r, %r)", path, flags)
        node, path = self._getnode(path)
        if path:
            return os.open(_getpath(node, path), flags)
        else:
            raise FuseOSError(EINVAL)

    def read(self, path, size, offset, fh):
        """read

        `path` is ignored.  Forward the request to the OS (via built-in os
        module) with the file descriptor.
        """
        logger.debug("read(%r, %r, %r, %r)", path, size, offset, fh)
        os.lseek(fh, offset, 0)
        return os.read(fh, size)

    def readdir(self, path, fh):
        """readdir

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Otherwise the result is generated as an empty
        directory plus others depending on the type of the furthest node.  If
        it is an FSNode, its children nodes are added.  If it is additionally a
        TagNode, its files are calculated according to its rules and added.
        """
        logger.debug("readdir(%r, %r)", path, fh)
        node, path = self._getnode(path)
        contents = ['.', '..']
        if path:
            contents += os.lsdir(_getpath(node, path))
        else:
            node.attr['st_atime'] = time()
            contents += [x for x in iter(node)]
        return contents

    def readlink(self, path):
        """readlink

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Otherwise the operation is invalid and raises
        EINVAL.
        """
        logger.debug("readlink(%r)", path)
        node, path = self._getnode(path)
        if path:
            return os.readlink(_getpath(node, path))
        else:
            raise FuseOSError(EINVAL)

    removexattr = None

    def rename(self, old, new):
        """rename

        This one is tricky.  If either path points to a node, raise EINVAL.  If
        `old` points only and not more than one directory deep beyond a node,
        all of that node's tags are removed from `old`.  If `new` points to a
        path not more than one directory deep beyond a node, all of that node's
        tags are added to `old`.  Whichever combination of the above, `old` is
        then renamed to `new` via built-in os module.
        """
        logger.debug("rename(%r, %r)", old, new)
        onode, opath = self._getnode(old)
        nnode, npath = self._getnode(new)
        if opath is None or npath is None:
            raise FuseOSError(EINVAL)
        ofpath = _getpath(onode, opath)
        nfpath = _getpath(nnode, npath)
        if len(opath) > 1:
            pass
        else:
            ofpath = _tmplink(ofpath)
            for tag in list(onode.tags):
                self.root.untag(ofpath, tag)
        if len(npath) > 1:
            os.rename(ofpath, nfpath)
        else:
            for tag in list(nnode.tags):
                self.root.tag(ofpath, tag)
            os.rm(ofpath)

    def rmdir(self, path):
        """rmdir

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Otherwise the operation is invalid and raises
        EINVAL.
        """
        logger.debug("rmdir(%r)", path)
        node, path = self._getnode(path)
        if path:
            os.rmdir(_getpath(node, path))
        else:
            raise FuseOSError(EINVAL)

    setxattr = None

    def statfs(self, path):
        """statfs

        Forward the request to the OS (via built-in os module).
        """
        logger.debug("statfs(%r)", path)
        stv = os.statvfs(path)
        return dict((key, getattr(stv, key)) for key in (
            'f_bavail', 'f_bfree', 'f_blocks', 'f_bsize', 'f_favail',
            'f_ffree', 'f_files', 'f_flag', 'f_frsize', 'f_namemax'))

    def symlink(self, source, target):
        """symlink

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  If `path` points not more than one directory deep
        beyond the node, add all of the node's tags to it.  Otherwise the
        operation is invalid and raises EINVAL.
        """
        logger.debug("symlink(%r, %r)", source, target)
        node, path = self._getnode(target)
        if path:
            os.symlink(source, _getpath(node, path))
            if len(path) == 1:
                t = list(node.tags)
                for tag in t:
                    self.root.tag(_getpath(node, path), tag)
        else:
            raise FuseOSError(EINVAL)

    def truncate(self, path, length, fh=None):
        """truncate

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Otherwise the operation is invalid and raises
        EINVAL.  `path` is used; `fh` is ignored.
        """
        logger.debug("truncate(%r, %r, %r)", path, length, fh)
        node, path = self._getnode(path)
        if path:
            with open(_getpath(node, path), 'r+') as f:
                f.truncate(length)
        else:
            raise FuseOSError(EINVAL)

    def unlink(self, path):
        """unlink

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Otherwise the operation is invalid and raises
        EINVAL.
        """
        logger.debug("unlink(%r)", path)
        node, path = self._getnode(path)
        if path:
            os.unlink(_getpath(node, path))
        else:
            raise FuseOSError(EINVAL)

    def utimens(self, path, times=None):
        """utimens

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Otherwise the operation is invalid and raises
        EINVAL.
        """
        logger.debug("utimens(%r, %r)", path, times)
        node, path = self._getnode(path)
        if path:
            os.utime(_getpath(node, path), times)
        else:
            raise FuseOSError(EINVAL)

    def write(self, path, data, offset, fh):
        """write

        If `path` points beyond a node, forward the request to the OS (via
        built-in os module).  Otherwise the operation is invalid and raises
        EINVAL.  `fh` is used; `path` is ignored.
        """
        logger.debug("write(%r, %r, %r, %r)", path, data, offset, fh)
        node, path = self._getnode(path)
        if path:
            os.lseek(fh, offset, 0)
            return os.write(fh, data)
        else:
            raise FuseOSError(EINVAL)

    def _getnode(self, path):
        """Get node and path components

        path is a string pointing to a path under the FUSE vfs.  If path is
        broken, raise FuseOSError(ENOENT).

        Returns a tuple (cur, path).  cur is the furthest FSNode along the
        path.  path is a list of strings indicating the path from the given
        node.  If node is the last file in the path, path is None.
        """
        assert len(path) > 0
        assert path[0] == "/"
        logger.debug("resolving path %r", path)
        path = [x for x in path.lstrip('/').split('/') if x != ""]
        logger.debug("path list %r", path)
        cur = self.tree
        while path:
            logger.debug("resolving %r", path[0])
            try:
                a = cur[path[0]]
            except KeyError:
                logger.warn("path broken")
                raise FuseOSError(ENOENT)
            if isinstance(a, str):
                logger.debug("leaf TagNode found, %r, %r", cur, path)
                return (cur, path)
            else:
                logger.debug("next node")
                cur = a
                del path[0]
        logger.debug("found node %r", cur)
        return (cur, None)


def _getpath(node, path):
    """Get real path

    Calculate and return the real path given TagNode `node` and list of strings
    `path`.  If `node` is not a TagNode, raise FuseOSError(EINVAL).
    """
    if not isinstance(node, tree.TagNode):
        raise FuseOSError(EINVAL)
    return os.path.join(node[path[0]], *path[1:])


def _tmplink(target):
    logger.debug("_tmplink(%r)", target)
    while True:
        fh, path = tempfile.mkstemp()
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


def mount(path, root, tree):
    return FUSE(TagOperations(root, tree), path, foreground=True)
