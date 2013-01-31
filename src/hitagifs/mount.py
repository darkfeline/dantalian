#!/usr/bin/env python

from fuse3 import FUSE, Operations

from errno import ENOENT, EPERM, EINVAL
from stat import S_IFLNK
from sys import argv, exit
from time import time

import logging
import os
import tempfile

from hitagifs import tree

ATTRS = ('st_atime', 'st_ctime', 'st_mtime', 'st_uid', 'st_gid', 'st_mode',
         'st_nlink', 'st_size')


class HitagiMount(Operations):

    def __init__(self, root, tree):
        self.root = root
        self.tree = tree

    def chmod(self, path, mode):
        node, path = self._getnode(path)
        if path:
            os.chmod(_getpath(node, path), mode)
        else:
            raise OSError(EINVAL)

    def chown(self, path, uid, gid):
        node, path = self._getnode(path)
        if path:
            os.chown(_getpath(node, path), uid, gid)
        else:
            raise OSError(EINVAL)

    def create(self, path, mode):
        node, path = self._getnode(path)
        if path:
            t = list(node.tags)
            path = os.path.join(self.root.tagpath(t.pop(0)), *path)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT, mode)
            for tag in t:
                self.root.tag(path, tag)
            return fd
        else:
            raise OSError(EINVAL)

    def getattr(self, path, fh=None):
        node, path = self._getnode(path)
        if path:
            st = os.lstat(path)
            return dict((key, getattr(st, key)) for key in ATTRS)
        else:
            #st = os.stat(self.root.root)
            #    return dict(
            #        st_atime,
            #        st_ctime,
            #        st_mtime,
            #        st_uid=st.st_uid,
            #        st_gid=st.st_gid,
            #        st_mode=st.st_mode,
            #        st_nlink,
            #        st_size=st.st_size)
            raise OSError(EINVAL)

    def getxattr(self, path, name, position=0):
        #attrs = self.files[path].get('attrs', {})
        #try:
        #    return attrs[name]
        #except KeyError:
        #    return ''       # Should return ENOATTR
        raise OSError(EPERM)

    def listxattr(self, path):
        #attrs = self.files[path].get('attrs', {})
        #return attrs.keys()
        raise OSError(EPERM)

    def mkdir(self, path, mode):
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
            raise OSError(EINVAL)

    def open(self, path, flags):
        node, path = self._getnode(path)
        if path:
            return os.open(_getpath(node, path), flags)
        else:
            raise OSError(EINVAL)

    def read(self, path, size, offset, fh):
        os.lseek(fh, offset, 0)
        return os.read(fh, size)

    def readdir(self, path, fh):
        node, path = self._getnode(path)
        if path:
            return ['.', '..'] + os.lsdir(_getpath(node, path))
        else:
            return ['.', '..'] + [node[x] for x in iter(node)]

    def readlink(self, path):
        node, path = self._getnode(path)
        if path:
            return ['.', '..'] + os.lsdir(_getpath(node, path))
        else:
            raise OSError(EINVAL)

    def removexattr(self, path, name):
        #attrs = self.files[path].get('attrs', {})
        #try:
        #    del attrs[name]
        #except KeyError:
        #    pass        # Should return ENOATTR
        raise OSError(EPERM)

    def rename(self, old, new):
        onode, opath = self._getnode(old)
        nnode, npath = self._getnode(new)
        if opath is None or npath is None:
            raise OSError(EINVAL)
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
        node, path = self._getnode(path)
        if path:
            os.rmdir(_getpath(node, path))
        else:
            raise OSError(EINVAL)

    def setxattr(self, path, name, value, options, position=0):
        ## Ignore options
        #attrs = self.files[path].setdefault('attrs', {})
        #attrs[name] = value
        raise OSError(EPERM)

    # not done
    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    # not done
    def symlink(self, target, source):
        target = target.encode('utf-8')
        self.files[source] = dict(st_mode=(S_IFLNK | 0o777), st_nlink=1,
            st_size=len(target))
        self.data[source] = bytearray(target)

    # not done
    def truncate(self, path, length, fh=None):
        del self.data[path][length:]
        self.files[path]['st_size'] = length

    # not done
    def unlink(self, path):
        self.files.pop(path)

    # not done
    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime

    # not done
    def write(self, path, data, offset, fh):
        del self.data[path][offset:]
        self.data[path].extend(data)
        self.files[path]['st_size'] = len(self.data[path])
        return len(data)

    def _getnode(self, path):
        """Get node and path components

        node is the furthest FSNode along the path.  path is a list.  If path
        is not empty, the first item maps to a string under node.  If path is
        broken, raise OSError(ENOENT).
        """
        assert len(path) > 0
        path = _splitpath(path)
        cur = self.tree[path.pop(0)]
        while path:
            try:
                a = self.tree[path[0]]
            except KeyError:
                raise OSError(ENOENT)
            if isinstance(a, str):
                return (cur, path)
            else:
                cur = a
                del path[0]
        return (cur, None)


def _getpath(node, path):
    """Get real path"""
    assert isinstance(node, tree.TagNode)
    return os.path.join(node[path[0]], *path[1:])


def _splitpath(path):
    """Split path into list"""
    return os.path.split(path.lstrip('/'))


def _tmplink(target):
    while True:
        fh, path = tempfile.mkstemp()
        os.close(fh)
        os.remove(path)
        try:
            os.link(target, path)
        except FileExistsError:
            continue
        else:
            return path


if __name__ == "__main__":
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)
    logging.getLogger().setLevel(logging.DEBUG)
    fuse = FUSE(Memory(), argv[1], foreground=True)
