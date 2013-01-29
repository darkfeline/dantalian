#!/usr/bin/env python

from fuse3 import FUSE, Operations

from errno import ENOENT, EPERM
from stat import S_IFDIR, S_IFLNK
from sys import argv, exit
from time import time

import logging
import os

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
            raise OSError(EPERM)

    def chown(self, path, uid, gid):
        node, path = self._getnode(path)
        if path:
            os.chown(_getpath(node, path), uid, gid)
        else:
            raise OSError(EPERM)

    def create(self, path, mode):
        node, path = self._getnode(path)
        if path:
            path = _getpath(node, path)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT, mode)
            for tag in node.tags:
                self.root.tag(path, tag)
            return fd
        else:
            raise OSError(EPERM)

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
            raise OSError(EPERM)

    # not done
    def getxattr(self, path, name, position=0):
        attrs = self.files[path].get('attrs', {})
        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    # not done
    def listxattr(self, path):
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    # not done
    def mkdir(self, path, mode):
        self.files[path] = dict(st_mode=(S_IFDIR | mode), st_nlink=2,
                st_size=0, st_ctime=time(), st_mtime=time(), st_atime=time())
        self.files['/']['st_nlink'] += 1

    # not done
    def open(self, path, flags):
        self.fd += 1
        return self.fd

    # not done
    def read(self, path, size, offset, fh):
        return bytes(self.data[path][offset:offset + size])

    # not done
    def readdir(self, path, fh):
        return ['.', '..'] + [x[1:] for x in self.files if x != '/']

    # not done
    def readlink(self, path):
        return self.data[path].decode('utf-8')

    # not done
    def removexattr(self, path, name):
        attrs = self.files[path].get('attrs', {})
        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    # not done
    def rename(self, old, new):
        self.files[new] = self.files.pop(old)

    # not done
    def rmdir(self, path):
        self.files.pop(path)
        self.files['/']['st_nlink'] -= 1

    # not done
    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

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
    assert isinstance(node, tree.TagNode)
    return os.path.join(node[path[0]], *path[1:])


def _splitpath(path):
    """Split path into list"""
    return os.path.split(path.lstrip('/'))


if __name__ == "__main__":
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)
    logging.getLogger().setLevel(logging.DEBUG)
    fuse = FUSE(Memory(), argv[1], foreground=True)
