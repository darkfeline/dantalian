#!/usr/bin/env python

from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

from fuse3 import Operations

from hitagifs import data


class HitagiOps(Operations):

    def __init__(self, fs):
        self.fs = fs
        self.fd = 0

    def chmod(self, path, mode):
        self.fs[path].attr['st_mode'] &= 0o770000
        self.fs[path].attr['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        self.fs[path].attr['st_uid'] = uid
        self.fs[path].attr['st_gid'] = gid

    def create(self, path, mode):
        self.fs[path] = dict(
            st_mode=(S_IFREG | mode), st_nlink=1, st_size=0, st_ctime=time(),
            st_mtime=time(), st_atime=time())
        self.fd += 1
        return self.fd

    def getattr(self, path, fh=None):
        if path not in self.fs:
            raise OSError(ENOENT, '')
        st = self.fs[path]
        return st

    def getxattr(self, path, name, position=0):
        attrs = self.fs[path].get('attrs', {})
        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    def listxattr(self, path):
        attrs = self.fs[path].get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
        self.fs[path] = dict(
            st_mode=(S_IFDIR | mode), st_nlink=2, st_size=0, st_ctime=time(),
            st_mtime=time(), st_atime=time())
        self.fs['/']['st_nlink'] += 1

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        return bytes(self.data[path][offset:offset + size])

    def readdir(self, path, fh):
        return ['.', '..'] + [x[1:] for x in self.fs if x != '/']

    def readlink(self, path):
        return self.data[path].decode('utf-8')

    def removexattr(self, path, name):
        attrs = self.fs[path].get('attrs', {})
        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    def rename(self, old, new):
        self.fs[new] = self.fs.pop(old)

    def rmdir(self, path):
        self.fs.pop(path)
        self.fs['/']['st_nlink'] -= 1

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.fs[path].setdefault('attrs', {})
        attrs[name] = value

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        source = source.encode('utf-8')
        self.fs[target] = dict(
            st_mode=(S_IFLNK | 0o777), st_nlink=1, st_size=len(source))
        self.data[target] = bytearray(source)

    def truncate(self, path, length, fh=None):
        del self.data[path][length:]
        self.fs[path]['st_size'] = length

    def unlink(self, path):
        self.fs.pop(path)

    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.fs[path]['st_atime'] = atime
        self.fs[path]['st_mtime'] = mtime

    def write(self, path, data, offset, fh):
        del self.data[path][offset:]
        self.data[path].extend(data)
        self.fs[path]['st_size'] = len(self.data[path])
        return len(data)
