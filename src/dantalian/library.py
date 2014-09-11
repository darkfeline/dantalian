"""
This module contains the Library class, which implements the methods for
operating on libraries.

"""

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

from . import fuse
from . import tree as treelib
from . import pathlib as dpath
from .errors import DependencyError

__all__ = []
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def _public(func):
    """Public decorator."""
    __all__.append(func.__name__)
    return func


# init_library {{{1
@_public
def init_library(root):

    """Initialize a library at the given path.

    Args:
        root: path to library

    Returns:
        A Library instance.

    This is safe to call on an existing library.

    """

    logger.debug('init(%r)', root)
    library = Library(root)

    # make dantalian private directory
    root_dir = library.rootdir
    logger.debug('mkdir %r', root_dir)
    try:
        os.mkdir(root_dir)
    except FileExistsError:
        logger.debug('skipping %r; exists', root_dir)

    # make root file
    root_file = library.rootfile
    if not os.path.exists(root_file):
        logger.debug('writing %r', root_file)
        with open(root_file, 'w') as f:  # pylint: disable=invalid-name
            f.write(root)

    # make dirs directory
    dirs_dir = library.dirsdir
    logger.debug('mkdir %r', dirs_dir)
    try:
        os.mkdir(dirs_dir)
    except FileExistsError:
        logger.debug('skipping %r; exists', dirs_dir)

    return library


# open_library {{{1
@_public
def open_library(root=None):
    """Open a library.

    Args:
        root: Path to the library.  Optional.

    Raises:
        LibraryError: No libraries found.

    Returns:
        A Library instance or suitable subclass.

    If root is given, it will be used as the path to the library.
    Otherwise, search up the directory tree using the current
    directory for the first library (a directory that contains a
    .dantalian subdirectory) we find and use that.  If none are
    found, raise LibraryError.

    """
    # find library
    if root is None:
        logger.debug("Finding library...")
        # pylint: disable=protected-access
        root = Library._find_root(os.getcwd())
        logger.debug("Found %r", root)
    # validate library
    library = Library(root)
    if not os.path.isdir(library.root) or not os.path.isdir(library.rootdir):
        raise LibraryError("{} isn't a library".format(root))
    # check for fuse
    if os.path.isdir(library.fuserootdir):
        library = ProxyLibrary(root)
    return library


# Library {{{1
class Library:

    """
    Attributes:
        root: Absolute path to library root.

    """

    __slots__ = ['root']
    ROOT_DIR = '.dantalian'

    # __init__ {{{2
    def __init__(self, root):
        """
        Should not be initialized directly; use open_library() instead.

        Args:
            root: Path to the library.

        Raises:
            LibraryError: root is not a library.

        """
        self.root = os.path.abspath(root)

    # properties {{{2
    # paths {{{3
    @property
    def rootdir(self):
        """Library data directory path."""
        return os.path.join(self.root, self.ROOT_DIR)

    @property
    def fuserootdir(self):
        """Fuse library data virtual directory path."""
        return os.path.join(self.root, '.dantalian-fuse')

    @property
    def rootfile(self):
        """Path of data file containing the path of the library root."""
        return os.path.join(self.rootdir, 'root')

    @property
    def dirsdir(self):
        """Path of directory for converted directories."""
        return os.path.join(self.rootdir, 'dirs')

    @property
    def treefile(self):
        """Path for mount tree file."""
        return os.path.join(self.rootdir, 'tree')

    @property
    def fusesock(self):
        """Path of FUSE socket."""
        return os.path.join(self.rootdir, 'fuse.sock')

    # _realroot {{{3
    @property
    def _realroot(self):
        """Return the root path stored internally."""
        with open(self.rootfile) as f:  # pylint:disable=invalid-name
            return f.read()

    # _moved {{{3
    @property
    def _moved(self):
        """Has the library been moved?"""
        old_root = self._realroot
        return old_root != self.root

    # class methods {{{2
    # _find_root {{{3
    @classmethod
    def _find_root(cls, pathname):
        """Find the first library above the given directory.

        Args:
            pathname: Path to directory.

        Returns:
            A string containing the absolute path to the library.

        Raises:
            LibraryError: No libraries were found.

        """
        assert os.path.isdir(pathname)
        pathname = os.path.abspath(pathname)
        root_dir = cls.ROOT_DIR
        logger.debug("finding root; starting with %r", pathname)
        while pathname:
            logger.debug("trying %r", pathname)
            if root_dir in os.listdir(pathname):
                return pathname
            elif pathname == '/':
                raise LibraryError('No root found')
            else:
                pathname = os.path.dirname(pathname)

    # helper methods {{{2
    # _listpaths {{{3
    def _listpaths(self, file):
        """Return a list of paths to all hard links to file.

        Args:
            file: Path to the file.

        Returns:
            A list of absolute paths.

        Raises:
            DependencyError: find could not be found.

        This follows hard links, but doesn't descend into .dantalian.
        Specifically, it returns all paths that would account for the
        given file's tags.

        Relies on find utility, for sheer simplicity and speed.  If it
        cannot be found, DependencyError is raised.

       """
        assert isinstance(file, str)
        try:
            output = subprocess.check_output([
                'find', '-L', self.root, '-path', self.rootdir, '-prune', '-o',
                '-samefile', file, '-print0'])
        except FileNotFoundError:
            raise DependencyError("find could not be found; \
                probably findutils is not installed")
        output = [x.decode() for x in output.split(b'\0') if x]
        return output

    # _liststrictpaths {{{3
    def _liststrictpaths(self, file):
        """Return a list of paths to all hard links to file.

        Args:
            file: Path to the file.

        Returns:
            A list of absolute paths.

        Raises:
            DependencyError: find could not be found.

        This does not descend into symbolic links, but does descend into
        .dantalian.  Thus, returns all unique hard links.

        Contrast with _listpaths: if a file "foo" is tagged "a", "a" is in the
        library root directory, and "a" is tagged "b", also in the root
        directory, _listpaths would return two paths, "a/foo" and "b/a/foo",
        while _liststrictpaths would only return one, ".dantalian/dirs/a/foo".

        Relies on find utility, for sheer simplicity and speed.  If it
        cannot be found, DependencyError is raised.

        """
        assert isinstance(file, str)
        try:
            output = subprocess.check_output([
                'find', self.root, '-samefile', file, '-print0'])
        except FileNotFoundError:
            raise DependencyError("find could not be found; \
                probably findutils is not installed")
        output = [x.decode() for x in output.split(b'\0') if x]
        return output

    # operations {{{2
    # tag {{{3
    def tag(self, file, tag):
        """Tag file with tag.

        Args:
            file: Path to the file.
            tag: Tag.

        Raises:
            IsADirectoryError: file is an unconverted directory.
            TagError: tag is not a directory/tag.

        If file is already tagged, nothing happens.  This includes if
        the file is hardlinked in the respective directory under
        another name.

        """
        file = os.path.normpath(file)  # get rid of trailing slashes
        if os.path.isdir(file) and not os.path.islink(file):
            raise IsADirectoryError(
                '{} is a directory; convert it first'.format(file))
        if dpath.istag(tag):
            dest_path = dpath.pathfromtag(tag, self.root)
        else:
            if not os.path.isdir(tag):
                raise TagError('{} is not a valid directory/tag'.format(tag))
            dest_path = tag
        logger.info('Checking if %r is already tagged with %r', file, tag)
        for f in dpath.listdir(dest_path):  # pylint: disable=invalid-name
            if os.path.samefile(f, file):
                return
        name = os.path.basename(file)
        while True:
            dest = os.path.join(dest_path, dpath.resolve_name(dest_path, name))
            logger.debug('linking %r %r', file, dest)
            try:
                os.link(file, dest)
            except FileExistsError:
                continue
            else:
                break

    # untag {{{3
    def untag(self, file, tag):
        """Remove tag from file.

        Args:
            file: Path to the file.
            tag: Tag.

        Raises:
            TagError: tag is not a directory/tag.

        If file is not tagged, nothing happens.  Remove *all* hard
        links to the file in the directory corresponding to the given
        tag.

        """
        if dpath.istag(tag):
            dest_path = dpath.pathfromtag(tag, self.root)
        else:
            if not os.path.isdir(tag):
                raise TagError(
                    '{} is not a directory/tag'.format(tag))
            dest_path = tag
        inode = os.lstat(file)
        for candidate in dpath.listdir(dest_path):
            candidate_inode = os.lstat(candidate)
            if os.path.samestat(inode, candidate_inode):
                logger.debug('unlinking %r', candidate)
                os.unlink(candidate)

    # mktag {{{3
    def mktag(self, tag):
        """Make tag.

        Args:
            tag: Tag.  Must be a unique tag qualifier, not a path.

        Raises:
            TagError: tag is not a unique tag qualifier.

        """
        if dpath.istag(tag):
            os.mkdir(dpath.pathfromtag(tag, self.root))
        else:
            raise TagError

    # rmtag {{{3
    def rmtag(self, tag):
        """Remove tag.

        Args:
            tag: Tag.  Must be a unique tag qualifier, not a path.

        Raises:
            TagError: tag is not a unique tag qualifier.

        """
        if dpath.istag(tag):
            shutil.rmtree(dpath.pathfromtag(tag, self.root))
        else:
            raise TagError

    # listtags {{{3
    def listtags(self, file):
        """Return a list of the tags of the file."""
        files = self._listpaths(file)
        return ['//' + os.path.dirname(os.path.relpath(f, self.root))
                for f in files]

    # convert {{{3
    def convert(self, dirpath):
        """Convert a directory to a symlink.

        Args:
            dirpath: Path to directory.

        Raises:
            NotADirectoryError: dirpath is not a directory.
            LibraryError: dirpath is in the directory for converted
                directories.

        If the directory is in .dantalian/dirs (smartassery), convert() raises
        LibraryError.  If the directory is a symlink (probably already
        converted), convert() returns without doing anything.  If the directory
        is not a directory, NotADirectoryError will be raised.

        """

        dirpath = os.path.abspath(dirpath)

        if not os.path.isdir(dirpath):
            raise NotADirectoryError("{} is not a directory".format(dirpath))
        if os.path.islink(dirpath):
            return
        dirname, basename = os.path.split(dirpath)
        if os.path.samefile(dirname, self.dirsdir):
            raise LibraryError("{} is in special directory".format(dirname))

        while True:
            target = os.path.join(self.dirsdir,
                                  dpath.resolve_name(dirpath, basename))
            logger.debug("moving %r to %r", dirpath, target)
            try:
                os.rename(dirpath, target)
            except FileExistsError:
                continue
            else:
                logger.debug("symlinking %r to %r", target, dirpath)
                # TODO race condition between this and rename()
                os.symlink(target, dirpath)
                break

    # revert {{{3
    def revert(self, symlink):
        """Revert a converted directory back from a symlink.

        Args:
            symlink: Path to symlink.

        """
        symlink = os.path.abspath(symlink)
        if not os.path.islink(symlink):
            raise LibraryError('{} is not a symbolic link'.format(symlink))
        target = os.readlink(symlink)
        target_dirname, _ = os.path.split(target)
        if not os.path.samefile(target_dirname, self.dirsdir):
            raise LibraryError(
                '{} is not a converted directory'.format(target_dirname))
        # Check only one
        links = self._liststrictpaths(symlink)
        if len(links) != 1:
            raise LibraryError(
                '{} is tagged in multiple places'.format(symlink))
        # Move directory back
        os.unlink(symlink)
        os.rename(target, symlink)

    # cleandirs {{{3
    def cleandirs(self):
        """Clean converted directories.

        Remove directories in the library's converted directories
        directory which do not have a symlink in the library that
        references them.  Nuke them with shutil.rmtree.

        """
        if not shutil.rmtree.avoids_symlink_attacks:
            logger.warning('Vulnerable to symlink attacks')
        dirsdir = self.dirsdir
        prefix = re.compile(re.escape(dirsdir))
        symlinks = dpath.findsymlinks(self.root)
        # pylint: disable=bad-builtin
        linkedto = filter(prefix.match, (os.readlink(x[0]) for x in symlinks))
        dirs = dpath.listdir(dirsdir)
        for dirpath in linkedto:
            try:
                dirs.remove(dirpath)
            except ValueError:
                logger.warning("Broken link %r", dirpath)
        logger.debug("Found unreferenced dirs %r", dirs)
        for dirpath in dirs:
            logger.debug("Nuking %r", dirpath)
            shutil.rmtree(dirpath)

    # find {{{3
    def find(self, tags):
        """Return a list of files with all of the given tags.

        Args:
            tags: List of tags.  List is not changed.

        Returns:
            List of absolute paths to the hard links corresponding to
            the first tag given.

        """
        search_path = (dpath.pathfromtag(tags[0], self.root) if
                       dpath.istag(tags[0]) else tags[0])
        tagpaths = (dpath.pathfromtag(tag, self.root) if dpath.istag(tag) else
                    tag for tag in tags)
        inodes = (set(os.lstat(x) for x in dpath.listdir(path))
                  for path in tagpaths)
        inodes = functools.reduce(set.intersection, inodes)
        return [x for x in
                dpath.listdir(search_path)
                if os.lstat(x) in inodes]

    # rm {{{3
    def rm(self, file):  # pylint: disable=invalid-name
        """Removes all tags from file.

        Args:
            file: path to file.

        If file is not tagged, nothing happens.

        This removes all hard links in the library to the file!  If no
        other hard links exist, the file is essentially deleted.

        """
        for filepath in self._liststrictpaths(file):
            logger.debug('unlinking %r', filepath)
            try:
                os.unlink(filepath)
            except OSError as err:
                logger.warning('Encountered OSError: %s', err)
                raise

    # rename {{{3
    def rename(self, file, new):
        """Rename tracked file.

        Rename all hard links in the library of file to new.  If
        file is not tagged, nothing happens.

        """
        for filepath in self._liststrictpaths(file):
            dirname = os.path.dirname(filepath)
            while True:
                dest = os.path.join(dirname, new)
                if os.path.exists(dest):
                    if not os.path.samefile(filepath, dest):
                        dest = os.path.join(
                            dirname, dpath.resolve_name(dirname, new))
                    else:
                        os.unlink(filepath)
                        break
                logger.debug('Moving %r to %r', filepath, dest)
                try:
                    os.rename(filepath, dest)
                except FileExistsError:
                    continue
                else:
                    break

    # fix {{{3
    def fix(self):
        """Fix symlinks of converted directories."""
        logger.info('Checking if moved')
        if not self._moved:
            logger.info('Not moved so doing nothing')
            return
        logger.info('Move detected; fixing')
        files = dpath.findsymlinks(self.root)
        logger.debug('Found symlinks %r', files)
        olddir = Library(self._realroot).dirsdir
        newdir = self.dirsdir
        dpath.fixsymlinks(files, olddir, newdir)
        logger.debug('Writing %r', self.rootfile)
        with open(self.rootfile, 'w') as f:  # pylint: disable=invalid-name
            f.write(self.root)
        logger.info('Finished fixing')

    # maketree {{{3
    def maketree(self):
        """Make node tree from library tree data file."""
        logger.info("making tree")
        if os.path.exists(self.treefile):
            with open(self.treefile) as inputfile:
                try:
                    data = json.load(inputfile)
                except ValueError:
                    logger.warn('Problem loading tree config')
                    return treelib.RootNode(self)
                else:
                    return treelib.load(self, data)
        else:
            return treelib.RootNode(self)

    # mount {{{3
    def mount(self, path, tree):
        """Mount library using FUSE."""
        addr = self.fusesock
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


# ProxyLibrary {{{1
class ProxyLibrary(Library):

    """
    Subclass of Library which overrides a number of methods for a
    FUSE-mounted library.

    """

    __slots__ = ['root', '_real_library']

    def __init__(self, root):
        super().__init__(root)
        self._real_library = Library(self._realroot)

    def cleandirs(self):
        self._real_library.cleandirs()

    def fix(self):
        logger.warning("can't fix fuse library")
        return

    def mount(self, path, tree):
        logger.warning("can't mount fuse library")
        return

    def convert(self, dirpath):
        self._real_library.convert(dirpath)


# SocketOperations {{{1
class SocketOperations(threading.Thread):

    """
    A Thread that manages a FUSE-mounted library and its socket, reading
    from the socket and processing commands.

    Methods that begin with do_ are commands.  The following input
    to the socket:

        command arg1 arg2 arg3

    will result in the method call:

        do_command(arg1, arg2, arg3)

    Path arguments to commands are absolute relative to the FUSE mount
    root.

    """

    def __init__(self, sock, root, tree):
        """
        Args:
            sock: Server socket
            root: Library instance
            tree: RootNode instance

        """
        super().__init__()
        self.sock = sock
        self.root = root
        self.tree = tree
        self.running = True

    def stop(self):
        """Stop thread."""
        self.running = False
        self.sock.shutdown(socket.SHUT_RD)

    def run(self):
        """Run thread."""
        while self.running:
            try:
                sock, _ = self.sock.accept()
            except OSError as err:
                logger.debug(
                    'Got exception listening for socket connection %r', err)
                continue
            msg = ""
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                msg += data.decode()
            logger.debug('recieved from socket %r', msg)
            msg = shlex.split(msg)
            try:
                cmd = msg.pop(0)
            except IndexError:
                logger.warning('Empty message received')
                continue
            try:
                cmdfunc = getattr(self, 'do_' + cmd)
            except AttributeError:
                logger.warning('Received unknown command %r', cmd)
                continue
            else:
                try:
                    cmdfunc(*msg)  # pylint: disable=star-args
                except Exception as err:  # pylint: disable=broad-except
                    logger.warning('Exception in SocketOperations %r', err)

    def do_mknode(self, path, *tags):
        """
        Args:
            path: path of node to make
            *tags: tags in tag format, not paths

        """
        logger.debug('mknode(%r, %r)', path, tags)
        node, path, ret = self.tree.get(path)
        if not path or ret == 0:  # path exists or leads into real space
            return
        for item in path[:-1]:
            node[item] = treelib.Node()
            node = node[item]
        node[path[-1]] = treelib.TagNode(self.root, tags)

    def do_rmnode(self, path):
        """Remove nodes."""
        logger.debug('rmnode(%r)', path)
        path, name_node = os.path.split(path)
        node, path, ret = self.tree.get(path)
        if path:
            return
        assert ret == 0
        del node[name_node]


# Exceptions {{{1
@_public
class LibraryError(Exception):
    """Library error."""


@_public
class TagError(LibraryError):
    """Tag error."""
