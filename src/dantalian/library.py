import os
import subprocess
import logging
import json
import functools
import re
import shutil
import shlex
import threading
import socket
from functools import lru_cache

from dantalian import fuse
from dantalian import tree
from dantalian import path as dpath
from dantalian.errors import DependencyError

__all__ = []
logger = logging.getLogger(__name__)


def _public(f):
    __all__.append(f.__name__)
    return f


@_public
def init_library(root: 'str'):

    """Initialize a library at `root`.

    Args:
        root (str): A path.

    Returns:
        A Library instance for the initialized library.

    """

    logger.debug('init(%r)', root)
    root = os.path.abspath(root)

    root_dir = Library.rootdir(root)
    logger.debug('mkdir %r', root_dir)
    try:
        os.mkdir(root_dir)
    except FileExistsError:
        logger.debug('skipping %r; exists', root_dir)

    root_file = Library.rootfile(root)
    if not os.path.exists(root_file):
        logger.debug('writing %r', root_file)
        with open(root_file, 'w') as f:
            f.write(root)

    dirs_dir = Library.dirsdir(root)
    logger.debug('mkdir %r', dirs_dir)
    try:
        os.mkdir(dirs_dir)
    except FileExistsError:
        logger.debug('skipping %r; exists', dirs_dir)

    return Library(root)


@_public
def open_library(root: 'str or None'=None):
    """Open a library.

    If `root` is None, search up the directory tree for the first
    library (a directory that contains ``.dantalian``) we find and use
    that.  If none are found, raises :exc:`LibraryError`.  Otherwise,
    `root` will be used.

    Args:
        root (str or None): A path.  Default is None.

    Returns:
        A Library instance or suitable subclass.

    """
    if root is None:
        logger.debug("Finding library...")
        root = _find_root(os.getcwd())
        logger.debug("Found %r", root)
    if os.path.isdir(Library.fuserootdir(root)):
        return ProxyLibrary(root)
    else:
        return Library(root)


@_public
class Library:

    """
    Attributes
    ----------
    root: str
        Absolute path to library root.

    """

    @staticmethod
    @lru_cache()
    def rootdir(root):
        return os.path.join(root, '.dantalian')

    @staticmethod
    @lru_cache()
    def fuserootdir(root):
        return os.path.join(root, '.dantalian-fuse')

    @classmethod
    @lru_cache()
    def rootfile(cls, root):
        return os.path.join(cls.rootdir(root), 'root')

    @classmethod
    @lru_cache()
    def dirsdir(cls, root):
        return os.path.join(cls.rootdir(root), 'dirs')

    @classmethod
    @lru_cache()
    def treefile(cls, root):
        return os.path.join(cls.rootdir(root), 'tree')

    @classmethod
    @lru_cache()
    def fusesock(cls, root):
        return os.path.join(cls.rootdir(root), 'fuse.sock')

    @property
    def _moved(self):
        with open(self.rootfile(self.root)) as f:
            old_root = f.read()
        if old_root == self.root:
            return None
        else:
            return old_root

    def __init__(self, root: 'str'):
        """
        Should not be initialized directly; use open_library instead.

        Args:
            root (str): Path to the library.

        Raises:
            LibraryError: root is not a library.

        """
        logger.debug("open library root %r", root)
        if not os.path.isdir(root) or not os.path.isdir(self.rootdir(root)):
            raise LibraryError("{} isn't a library".format(root))
        self.root = os.path.abspath(root)
        logger.info('Library initialized')
        logger.debug('root is %r', self.root)

    def tag(self, file, tag):
        """Tag file with tag.

        If `file` is already tagged, nothing happens.  This includes if
        the file is hardlinked under another name.

        Parameters
        ----------
        file : str
             Path to the file, relative to the working directory.
        tag : str
            Tag, relative to the library root, starting with '/'.

        Raises
        ------
        IsADirectoryError
            file is an unconverted directory.
        NotADirectoryError
            tag is not a directory/tag.

        """

        if os.path.isdir(file) and not os.path.islink(file):
            raise IsADirectoryError(
                '{} is a directory; convert it first'.format(file))
        if dpath.istag(tag):
            p_dest = dpath.pathfromtag(tag, self.root)
        else:
            if not os.path.isdir(tag):
                raise NotADirectoryError(
                    '{} is not a directory/tag'.format(tag))
            p_dest = tag
        logger.info(
            'Checking if %r is already tagged with %r', file, tag)
        for f in dpath.listdir(p_dest):
            if os.path.samefile(f, file):
                return
        logger.info('Check okay')
        name = os.path.basename(file)
        while True:
            dest = os.path.join(p_dest, dpath.resolve_name(p_dest, name))
            logger.debug('linking %r %r', file, dest)
            try:
                os.link(file, dest)
            except FileExistsError:
                continue
            else:
                break

    def untag(self, file, tag):
        """Remove tag from file.

        If file is not tagged, nothing happens.  Remove *all* hard
        links to the file in the directory corresponding to the given
        tag.  Log a warning when an OSError is caught.

        Parameters
        ----------
        file : str
             Path to the file, relative to the working directory.
        tag : str
            Tag, relative to the library root, starting with '/'.

        Raises
        ------
        NotADirectoryError
            tag is not a directory/tag.

        """
        logger.debug('untag(%r, %r)', file, tag)
        assert isinstance(file, str)
        assert isinstance(tag, str)
        if dpath.istag(tag):
            p_dest = dpath.pathfromtag(tag, self.root)
        else:
            if not os.path.isdir(tag):
                raise NotADirectoryError(
                    '{} is not a directory/tag'.format(tag))
            p_dest = tag
        inode = os.lstat(file)
        logger.debug('file inode is %r', inode)
        for f in dpath.listdir(p_dest):
            logger.debug('checking %r', f)
            st = os.lstat(f)
            logger.debug('inode is %r', st)
            if os.path.samestat(inode, st):
                logger.debug('unlinking %r', f)
                try:
                    os.unlink(f)
                except OSError as e:
                    logger.warning('Caught OSError: %s', e)

    def _listpaths(self, file):
        """Return a list of paths to all hard links to `file`.

        This descends into symbolic links and trims ``.dantalian/dirs``.
        Specifically, returns all paths that would account for `file`'s
        tags.

        Relies on 'find' utility, for sheer simplicity and speed.  If it
        cannot be found, :exc:`DependencyError` is raised.

        Args:
            file (str): Path to the file, relative to the working
                directory.

        Returns:
            A list of absolute paths (strings).

        Raises:
            DependencyError: find could not be found.

        """
        assert isinstance(file, str)
        try:
            output = subprocess.check_output([
                'find', '-L', self.root, '-path',
                self.rootdir(self.root), '-prune', '-o', '-samefile', file,
                '-print'])
        except FileNotFoundError:
            raise DependencyError("find could not be found; \
                probably findutils is not installed")
        output = output.decode().rstrip().split('\n')
        return output

    def _liststrictpaths(self, file):
        """Return a list of paths to all hard links to `file`.

        This does not descend into symbolic links, but does descend into
        ``.dantalian``.  Thus, returns all unique hard links.

        Relies on 'find' utility, for sheer simplicity and speed.  If it
        cannot be found, :exc:`DependencyError` is raised.  Output paths
        are absolute.

        Args:
            file (str): Path to the file, relative to the working
                directory.

        Returns:
            A list of absolute paths (strings).

        Raises:
            DependencyError: find could not be found.

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
        return ['//' + os.path.dirname(os.path.relpath(f, self.root))
                for f in files]

    def convert(self, dir):
        """Convert a directory to a symlink.

        If `dir` is in ``.dantalian/dirs`` (smartassery), convert raises
        LibraryError.  If `dir` is a symlink (probably already
        converted), convert returns without doing anything.  If `dir` is
        not a directory, NotADirectoryError will be raised.

        Args:
            dir (str): Path to directory.

        Raises:
            NotADirectoryError: dir is not a directory.
            LibraryError: dir is in the directory for converted
                directories.

        """
        logger.debug('convert(%r)', dir)
        _convertto(dir, self.dirsdir(self.root))

    def cleandirs(self):
        """Clean converted directories.

        Remove directories in the library's converted directories
        directory which do not have a symlink in the library that
        references them.  Nuke them with shutil.rmtree.

        """
        _cleandirs(self.root)

    def find(self, tags):
        """Return a list of files with all of the given tags.

        Parameters
        ----------
        tags : list
            List of tags.  List is not changed.

        Returns
        -------
        list
            List of absolute paths, to the hard link under the first tag
            given.

        """
        logger.debug("find(%r)", tags)
        assert len(tags) > 0
        inodes = functools.reduce(
            set.intersection, (set(
                os.lstat(x) for x in dpath.listdir(
                    dpath.pathfromtag(y, self.root))
            ) for y in tags))
        logger.debug("found unique inodes %r", inodes)
        map = dict((os.lstat(x), x) for x in dpath.listdir(
            dpath.pathfromtag(tags[0], self.root)))
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
                logger.warning('Encountered OSError: %s', e)
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
                dest = os.path.join(dir, new)
                if os.path.exists(dest) and not os.path.samefile(file, dest):
                    dest = os.path.join(dir, dpath.resolve_name(dir, new))
                logger.debug('Moving %r to %r', file, dest)
                try:
                    os.rename(file, dest)
                except FileExistsError:
                    continue
                else:
                    break

    def fix(self):
        logger.info('Checking if moved')
        if not self._moved:
            logger.info('Not moved so doing nothing')
            return
        logger.info('Move detected; fixing')
        files = dpath.findsymlinks(self.root)
        logger.debug('Found symlinks %r', files)
        olddir = self.dirsdir(self._moved)
        newdir = self.dirsdir(self.root)
        dpath.fixsymlinks(files, olddir, newdir)
        logger.debug('Writing %r', self.rootfile(self.root))
        with open(self.rootfile(self.root), 'w') as f:
            f.write(self.root)
        logger.info('Finished fixing')

    def maketree(self):
        logger.info("making tree")
        if os.path.exists(self.treefile(self.root)):
            with open(self.treefile(self.root)) as f:
                return tree.load(self, json.load(f))
        else:
            return RootNode(self)

    def mount(self, path, tree):
        addr = self.fusesock(self.root)
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
        fuse.mount(path, self, tree)
        thread.stop()
        return tree


def _cleandirs(root):
    if not shutil.rmtree.avoids_symlink_attacks:
        logger.warning('Vulnerable to symlink attacks')
    dirsdir = Library.dirsdir(root)
    prefix = re.compile(re.escape(dirsdir))
    symlinks = dpath.findsymlinks(root)
    linkedto = [os.readlink(x[0]) for x in symlinks]
    linkedto = filter(prefix.match, (os.readlink(x[0]) for x in symlinks))
    dirs = dpath.listdir(dirsdir)
    for x in linkedto:
        try:
            dirs.remove(x)
        except ValueError:
            logger.warning("Broken link %r", x)
    logger.debug("Found unreferenced dirs %r", dirs)
    for x in dirs:
        logger.debug("Nuking %r", x)
        shutil.rmtree(x)


def _convertto(dir, target):

    """
    Args:
        dir (str): directory to convert
        target (str): dantalian dirs directory

    Raises:
        NotADirectoryError: dir is not a directory.
        LibraryError: dir is in the directory for converted directories.

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
    if os.path.samefile(dirname, target):
        raise LibraryError("{} is in special directory".format(dirname))
    logger.info("Check okay")

    while True:
        target = os.path.join(target, dpath.resolve_name(dir, basename))
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

    Returns:
        A string of the absolute path to the library.

    Raises:
        LibraryError: No libraries were found.

    """
    assert os.path.isdir(dir)
    dir = os.path.abspath(dir)
    root_dir = Library.rootdir('')
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


@_public
class ProxyLibrary(Library):

    """
    Subclass of Library which overrides a number of methods for a
    FUSE-mounted library.

    """

    def __init__(self, root):
        logger.debug("open fuse library %r", root)
        super().__init__(root)
        with open(self.rootfile(self.root)) as f:
            self._realroot = f.read()
        logger.debug("real library is %r", self._realroot)

    def cleandirs(self):
        _cleandirs(self._realroot)

    def fix(self):
        logger.warning("can't fix fuse library")
        return

    def mount(self, root):
        logger.warning("can't mount fuse library")
        return

    def convert(self, dir):
        logger.debug('convert(%r, %r)', dir)
        _convertto(dir, self.dirsdir(self._realroot))


@_public
class SocketOperations(threading.Thread):

    """
    A Thread that manages a FUSE-mounted library and its socket, reading
    from the socket and processing commands.

    Methods that begin with ``do_`` are commands.  The following input
    to the socket::

        command arg1 arg2 arg3

    will result in the method call::

        do_command(arg1, arg2, arg3)

    """

    def __init__(self, sock, root, tree):
        """
        Parameters
        ----------
        sock : socket
            Server socket.
        root : BaseLibrary
            Library instance.
        tree : RootNode
            RootNode instance.

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
            try:
                cmd = msg.pop(0)
            except IndexError:
                logger.warning('Empty message received')
                continue
            try:
                x = getattr(self, 'do_' + cmd)
            except AttributeError:
                logger.warning('Received unknown command %r', cmd)
                continue
            else:
                x(*msg)

    def do_mknode(self, path, *tags):
        name = []
        while True:
            path, x = os.path.split(path)
            name.append(x)
            node, path, ret = self.tree.getpath(path)
            if ret == 1:
                continue
            else:
                break
        if path:  # tried to make node outside vfs
            return
        name = reversed(name)
        for next in name[:-1]:
            node[name] = tree.Node()
            node = node[name]
        node[name[-1]] = tree.TagNode(self.root, tags)

    def do_rmnode(self, path):
        path, name_node = os.path.split(path)
        node, path, ret = self.tree.getpath(path)
        if path:
            return
        assert ret == 0
        del node[name_node]


@_public
class LibraryError(Exception):
    pass


@_public
class TagError(LibraryError):
    pass
