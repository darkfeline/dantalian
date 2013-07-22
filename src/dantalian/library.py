import abc
import os
import subprocess
import logging
import json
import importlib
import functools
import re
import shutil
import shlex
import threading
import socket

from dantalian import operations as ops
from dantalian import tree
from dantalian import path as libpath
from dantalian.errors import DependencyError

__all__ = [
    'init_library', 'open_library', 'BaseLibrary', 'BaseFSLibrary', 'Library',
    'ProxyLibrary', 'SocketOperations', 'LibraryError']
logger = logging.getLogger(__name__)


def init_library(root):

    """Initialize a library at `root`

    Calling :meth:`init` on an existing library does no harm.  Returns an
    instance of :class:`Library`.

    """

    logger.debug('init(%r)', root)
    root = os.path.abspath(root)

    root_dir = libpath.rootdir(root)
    logger.debug('mkdir %r', root_dir)
    try:
        os.mkdir(root_dir)
    except FileExistsError:
        logger.debug('skipping %r; exists', root_dir)

    root_file = libpath.rootfile(root)
    if not os.path.exists(root_file):
        logger.debug('writing %r', root_file)
        with open(root_file, 'w') as f:
            f.write(root)

    dirs_dir = libpath.dirsdir(root)
    logger.debug('mkdir %r', dirs_dir)
    try:
        os.mkdir(dirs_dir)
    except FileExistsError:
        logger.debug('skipping %r; exists', dirs_dir)

    return Library(root)


def open_library(root=None):
    """
    If `root` is :data:`None`, search up the directory tree for the
    first library (a directory that contains ``.dantalian``) we find and
    use that.  If none are found, raises :exc:`LibraryError`.
    Otherwise, `root` will be used.  Return a Library or subclass.
    """
    if root is None:
        logger.debug("Finding library...")
        root = _find_root(os.getcwd())
        logger.debug("Found %r", root)
    if os.path.isdir(libpath.fuserootdir(root)):
        return ProxyLibrary(root)
    else:
        return Library(root)


class BaseLibrary(metaclass=abc.ABCMeta):

    """
    BaseLibrary is the fundamental abstract library class.  It requires
    the following methods and invariants:

    tag(file, tag)
        `file` should be tagged with `tag` after call, regardless of
        whether it was before.
    untag(file, tag)
        `file` should not be tagged with `tag` after call, regardless of
        whether it was before.
    listtags(file)
        Return a list of all of the tags of `file`.
    find(tags)
        Return a list of files that have all of the given tags in `tags`.
    mount(path, tree)
        Mount a virtual representation of the library representation
        `tree` at `path`.  This may be left unimplemented or with a
        dummy implementation.
    """

    @abc.abstractmethod
    def tag(self, file, tag):
        raise NotImplementedError

    @abc.abstractmethod
    def untag(self, file, tag):
        raise NotImplementedError

    @abc.abstractmethod
    def listtags(self, file):
        raise NotImplementedError

    @abc.abstractmethod
    def find(self, tags):
        raise NotImplementedError

    @abc.abstractmethod
    def mount(self, path, tree):
        pass


class BaseFSLibrary(BaseLibrary, metaclass=abc.ABCMeta):

    """
    BaseFSLibrary is the abstract class for libraries implemented on a
    file system.  It requires the following methods and invariants in
    addition to those described in BaseLibrary:

    tag(file, tag)
        If `file` does not have a hard link under the `tag` directory,
        make one.  `file` has at least one hard link under the `tag`
        directory after call.
    untag(file, tag)
        `file` has no hard links under the `tag` directory after call,
        regardless of whether it did before.
    """


class Library(BaseFSLibrary):

    """
    Implementation of methods that work directly with library on the file
    system.
    """

    @property
    def _moved(self):
        with open(libpath.rootfile(self.root)) as f:
            old_root = f.read()
        if old_root == self.root:
            return None
        else:
            return old_root

    def __init__(self, root):
        """If `root` is not a library, raise LibraryError."""
        logger.debug("open library root %r", root)
        if not os.path.isdir(root) or not os.path.isdir(libpath.rootdir(root)):
            raise LibraryError("{} isn't a library".format(root))
        self.root = os.path.abspath(root)
        logger.info('Library initialized')
        logger.debug('root is %r', self.root)

    def tag(self, file, tag):
        """Tag `file` with `tag`

        `file` is relative to current dir. `tag` is relative to library
        root.  If `file` is already tagged, nothing happens.  This
        includes if the file is hardlinked under another name.
        """

        if os.path.isdir(file) and not os.path.islink(file):
            raise IsADirectoryError(
                '{} is a directory; convert it first'.format(file))
        destdir = self.tagpath(tag)
        logger.info(
            'Checking if %r is already tagged with %r', file, tag)
        for f in libpath.listdir(destdir):
            if libpath.samefile(f, file):
                return
        logger.info('Check okay')
        name = os.path.basename(file)
        while True:
            dest = os.path.join(destdir, libpath.resolve_name(destdir, name))
            logger.debug('linking %r %r', file, dest)
            try:
                os.link(file, dest)
            except FileExistsError:
                continue
            else:
                break

    def untag(self, file, tag):
        """Remove `tag` from `file`.

        `file` is relative to current dir. `tag` is relative to library
        root.  If file is not tagged, nothing happens.  Removes *all*
        hard links to `file` with `tag`.
        """
        logger.debug('untag(%r, %r)', file, tag)
        assert isinstance(file, str)
        assert isinstance(tag, str)
        dest = self.tagpath(tag)
        inode = os.lstat(file)
        logger.debug('file inode is %r', inode)
        for f in libpath.listdir(dest):
            logger.debug('checking %r', f)
            st = os.lstat(f)
            logger.debug('inode is %r', st)
            if os.path.samestat(inode, st):
                logger.debug('unlinking %r', f)
                try:
                    os.unlink(f)
                except OSError as e:
                    logger.warn('Caught OSError: %s', e)

    def _listpaths(self, file):
        """Return a list of paths to all hard links to `file`

        This descends into symbolic links and trims ``.dantalian/dirs``.
        Specifically, returns all paths that would account for `file`'s
        tags.

        Relies on 'find' utility, for sheer simplicity and speed.  If it
        cannot be found, :exc:`DependencyError` is raised.  Output paths
        are absolute.
        """
        assert isinstance(file, str)
        try:
            output = subprocess.check_output([
                'find', '-L', self.root, '-path',
                libpath.rootdir(self.root), '-prune', '-o', '-samefile', file,
                '-print'])
        except FileNotFoundError:
            raise DependencyError("find could not be found; \
                probably findutils is not installed")
        output = output.decode().rstrip().split('\n')
        return output

    def _liststrictpaths(self, file):
        """Return a list of paths to all hard links to `file`

        This does not descend into symbolic links.  Thus, returns all
        unique hard links.

        Relies on 'find' utility, for sheer simplicity and speed.  If it
        cannot be found, :exc:`DependencyError` is raised.  Output paths
        are absolute.
        """
        assert isinstance(file, str)
        try:
            output = subprocess.check_output([
                'find', self.root, '-samefile', file])
        except FileNotFoundError:
            raise DependencyError("find could not be found; \
                probably findutils is not installed")
        output = output.decode().rstrip().split('\n')
        return output

    def listtags(self, file):
        """Return a list of all tags of `file`"""
        assert isinstance(file, str)
        files = self._listpaths(file)
        return [
            os.path.dirname(f).replace(self.root + '/', '', 1) for f in
            files]

    def convert(self, dir):
        """Convert a directory to a symlink.

        If `dir` is in ``.dantalian/dirs`` (smartassery),
        convert raises LibraryError.  If `dir` is a
        symlink (probably already converted), convert returns
        without doing anything.  If `dir` is not a directory,
        NotADirectoryError will be raised.  If `alt` is given, the
        alternate name will be used for the copy kept in
        ``.dantalian/dirs``.
        """
        logger.debug('convert(%r, %r)', dir)
        _convertto(dir, libpath.dirsdir(self.root))

    def cleandirs(self):
        """Clean converted directories

        Remove directories in the library's converted directories
        directory which do not have a symlink in the library that
        references them.  Nuke them with shutil.rmtree
        """
        _cleandirs(self.root)

    def find(self, tags):
        """Return a list of files with all of the given tags.

        `tags` is a list. `tags` is left unchanged.  Returns a list.
        File paths are absolute and are paths to the hard link under the
        first tag given.
        """
        logger.debug("find(%r)", tags)
        assert len(tags) > 0
        inodes = functools.reduce(
            set.intersection,
            (set(os.lstat(x) for x in libpath.listdir(y)) for y in tags))
        logger.debug("found unique inodes %r", inodes)
        map = dict((os.lstat(x), x) for x in libpath.listdir(tags[0]))
        logger.debug("using map %r", map)
        return [map[x] for x in inodes]

    def rm(self, file):
        """Removes all tags from `file`.

        `file` is a path relative to the current dir.  If `file` is not
        tagged, nothing happens.  If a file cannot be removed (for
        whatever reason), it is skipped, a warning is logged, and
        rm() returns ``1``.  Otherwise, returns ``0``.

        This removes all hard links in the library to `file`!  If no
        other hard links exist, `file` is deleted.
        """
        assert isinstance(file, str)
        error = 0
        for file in self._liststrictpaths(file):
            logger.debug('unlinking %r', file)
            try:
                os.unlink(file)
            except OSError as e:
                logger.warn('Encountered OSError: %s', e)
                error = 1
        return error

    def rename(self, file, new):
        """Rename tracked file.

        Rename all hard links in the library of `file` to `new`.  If
        `file` is not tagged, nothing happens.  If a file cannot be
        renamed, log an error and continue.
        """
        assert isinstance(file, str)
        assert isinstance(new, str)
        files = self._liststrictpaths(file)
        logger.debug('Found to rename: %r', files)
        for file in files:
            dir = os.path.dirname(file)
            while True:
                dest = os.path.join(dir, libpath.resolve_name(dir, new))
                logger.debug('Moving %r to %r', file, dest)
                try:
                    os.rename(file, dest)
                except FileExistsError:
                    continue
                else:
                    break

    def tagpath(self, tag):
        """Get absolute path of `tag`.

        Raise TagError if tag doesn't exist
        :rtype: :class:`str`

        """
        path = os.path.join(self.root, tag)
        assert path == os.path.abspath(path)
        if not os.path.isdir(path):
            raise TagError(
                "Tag {} doesn't exist (or isn't a directory)".format(tag))
        return path

    def fix(self):
        logger.info('Checking if moved')
        if not self._moved:
            logger.info('Not moved so doing nothing')
            return
        logger.info('Move detected; fixing')
        files = libpath.findsymlinks(self.root)
        logger.debug('Found symlinks %r', files)
        olddir = libpath.dirsdir(self._moved)
        newdir = libpath.dirsdir(self.root)
        libpath.fixsymlinks(files, olddir, newdir)
        logger.debug('Writing %r', libpath.rootfile(self.root))
        with open(libpath.rootfile(self.root), 'w') as f:
            f.write(self.root)
        logger.info('Finished fixing')

    def maketree(self):
        logger.info("making tree")
        if os.path.exists(libpath.ctreefile(self.root)):
            logger.info("using custom")
            name = 'custom'
            path = libpath.ctreefile(self.root)
            custom = importlib.SourceFileLoader(name, path).load_module(name)
            return custom.maketree(self.root)
        else:
            logger.info("using config")
            return self._maketree(libpath.treefile(self.root))

    def _maketree(self, config):
        """Make a FSNode tree

        config is file path.
        """
        logger.debug("_maketree(%r, %r)", self, config)
        with open(config) as f:
            dat = json.load(f)
        r = tree.RootNode(self)
        for x in dat:
            mount_, tags = x['mount'], x['tags']
            logger.debug("doing %r, %r", mount_, tags)
            mount_ = mount_.lstrip('/').split('/')
            y = r
            for x in mount_[:-1]:
                logger.debug("trying %r", x)
                try:
                    if not isinstance(y[x], str):
                        y = y[x]
                    else:
                        raise KeyError
                except KeyError:
                    logger.debug("making FSNode at %r[%r]", y, x)
                    y[x] = tree.FSNode()
                    y = y[x]
            x = mount_[-1]
            if x not in y:
                logger.debug("making TagNode at %r[%r]", y, x)
                y[x] = tree.TagNode(self, tags)
            else:
                logger.debug("replacing node at %r[%r]", y, x)
                y[x] = tree.fs2tag(y[x])
        return r

    def mount(self, path, tree):
        addr = libpath.fusesock(self.root)
        try:
            os.unlink(addr)
            logger.debug("Removed old socket")
        except OSError:
            if os.path.exists(addr):
                raise
        sock = socket.socket(socket.AF_UNIX)
        sock.bind(addr)
        sock.listen(1)
        logger.debug("Socket bound and listening to %r", addr)
        thread = SocketOperations(sock, self, tree)
        thread.start()
        logger.debug("Started socket listening thread")
        logger.debug("Mounting fuse at %r with %r", path, tree)
        ops.mount(path, self, tree)
        thread.stop()


def _cleandirs(root):
    if not shutil.rmtree.avoids_symlink_attacks:
        logger.warning('Vulnerable to symlink attacks')
    dirsdir = libpath.dirsdir(root)
    prefix = re.compile(re.escape(dirsdir))
    symlinks = libpath.findsymlinks(root)
    symlinks = filter(prefix.match, symlinks)
    linkedto = [os.readlink(x[0]) for x in symlinks]
    dirs = libpath.listdir(dirsdir)
    for x in linkedto:
        try:
            dirs.remove(x)
        except ValueError:
            logger.warn("Broken link %r", x)
    logger.debug("Found unreferenced dirs %r", dirs)
    for x in dirs:
        logger.debug("Nuking %r", x)
        shutil.rmtree(x)


def _convertto(dir, target):

    """
    dir: directory to convert
    target: dantalian dirs directory
    """

    dir = os.path.abspath(dir)

    logger.info("Checking %r is a dir", dir)
    if not os.path.isdir(dir):
        raise NotADirectoryError("{} is not a directory".format(dir))
    logger.info("Check okay")

    logger.info("Checking %r is not a symlink", dir)
    if os.path.islink(dir):
        logger.info("%r is symlink; skipping", dir)
        return
    logger.info("Check okay")

    logger.info("Checking %r is not in dirs", dir)
    dirname, basename = os.path.split(os.path.abspath(dir))
    if libpath.samefile(dirname, target):
        raise LibraryError("{} is in special directory".format(dirname))
    logger.info("Check okay")

    while True:
        target = os.path.join(target, libpath.resolve_name(basename))
        logger.debug("moving %r to %r", dir, target)
        try:
            os.rename(dir, target)
        except FileExistsError:
            continue
        else:
            logger.debug("linking %r to %r", dir, target)
            os.symlink(target, dir)
            break


def _find_root(dir):
    """Find the first library above `dir`.

    If none are found, raises :exc:`LibraryError`.

    :rtype: :class:`str

    """
    assert os.path.isdir(dir)
    dir = os.path.abspath(dir)
    root_dir = libpath.rootdir('')
    logger.debug("finding root; starting with %r", dir)
    while dir:
        logger.debug("trying %r", dir)
        if root_dir in os.listdir(dir):
            return dir
        else:
            if dir == '/':
                break
            dir = os.path.dirname(dir)
    raise LibraryError('No root found')


class ProxyLibrary(Library):

    def __init__(self, root):
        logger.debug("open fuse library %r", root)
        super().__init__(root)
        with open(libpath.rootfile(self.root)) as f:
            self._realroot = f.read()
        logger.debug("real library is %r", self._realroot)

    def cleandirs(self):
        _cleandirs(self._realroot)

    def fix(self):
        logger.warn("can't fix fuse library")
        return

    def mount(self, root):
        logger.warn("can't mount fuse library")
        return

    def convert(self, dir, alt=None):
        logger.debug('convert(%r, %r)', dir, alt)
        _convertto(*_convertcheck(dir, libpath.dirsdir(self._realroot), alt))


class SocketOperations(threading.Thread):

    def __init__(self, sock, root, tree):
        """
        `sock` is server socket. `root` is library. `tree` is root node.
        """
        super().__init__()
        self.sock = sock
        self.root = root
        self.tree = tree
        self.running = True

    def stop(self):
        self.running = False
        self.sock.shutdown(socket.SHUT_RD)

    def run(self):
        while self.running:
            try:
                sock, addr = self.sock.accept()
            except OSError as e:
                logger.debug(
                    'Got exception listening for socket connection %r', e)
                continue
            msg = ""
            while True:
                m = sock.recv(1024)
                if not m:
                    break
                msg += m.decode()
            logger.debug('recieved from socket %r', msg)
            msg = shlex.split(msg)
            cmd = msg.pop(0)
            try:
                x = getattr(self, 'do_' + cmd)
            except AttributeError:
                logger.warn('received unknown command %r', cmd)
            x(*msg)

    def do_mknode(self, path, *tags):
        name = []
        while True:
            path, x = os.path.split(path)
            name.append(x)
            try:
                node, path = tree.split(self.tree, path)
            except TypeError:
                continue
            else:
                if path:  # tried to make node outside vfs
                    return
                name = list(reversed(name))
                for next in name[:-1]:
                    node[name] = tree.FSNode()
                    node = node[name]
                x = tree.TagNode(self.root, tags)
                node[name[-1]] = x
                break


class LibraryError(Exception): pass
class TagError(LibraryError): pass
