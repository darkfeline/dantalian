import os
import subprocess
import logging
import json
import importlib
import functools
import re
import shutil

from dantalian import mount
from dantalian import tree
from dantalian import path as libpath
from dantalian.errors import DependencyError

__all__ = [
    'init_library', 'open_library', 'Library', 'FUSELibrary', 'LibraryError']
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
    If `root` is :data:`None`, search up the directory tree for the first
    library (a directory that contains ``.dantalian``) we find and use that.
    If none are found, raises :exc:`LibraryError`.  Otherwise, `root` will be
    used.  Return a Library or subclass.
    """
    if root is None:
        logger.debug("Finding library...")
        root = _find_root(os.getcwd())
        logger.debug("Found %r", root)
    if os.path.isdir(libpath.fuserootdir(root)):
        return FUSELibrary(root)
    else:
        return Library(root)


class Library:

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

    def tag(self, file, tag, alt=None):
        """Tag `file` with `tag`.

        `file` is relative to current dir. `tag` is relative to library root.
        If `file` is already tagged, nothing happens.  This includes if the
        file is hardlinked under another name.  If `file` is an unconverted
        directory, :exc:`IsADirectoryError` will be raised.  If there's a name
        collision, :exc:`FileExistsError` is raised.

        """
        assert isinstance(file, str)
        assert isinstance(tag, str)
        if os.path.isdir(file) and not os.path.islink(file):
            raise IsADirectoryError(
                '{} is a directory; convert it first'.format(file))
        dest = self.tagpath(tag)
        if alt is not None:
            assert isinstance(alt, str)
            dest = os.path.join(dest, alt)
        name = os.path.basename(file)
        logger.info('checking if %r already tagged with %r', file, tag)
        for f in libpath.listdir(dest):
            if libpath.samefile(f, file):
                return
        logger.info('check okay')
        dest = os.path.join(dest, name)
        logger.debug('linking %r %r', file, dest)
        try:
            os.link(file, dest)
        except FileExistsError as e:
            raise e

    def untag(self, file, tag):
        """Remove `tag` from `file`.

        `file` is relative to current dir. `tag` is relative to library root.
        If file is not tagged, nothing happens.  Removes *all* hard links to
        `file` with `tag`.

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
                os.unlink(f)

    def listpaths(self, file):
        """Return a list of paths to all hard links to `file`

        Relies on 'find' utility, for sheer simplicity and speed.  If it cannot
        be found, :exc:`DependencyError` is raised.  Output paths are absolute.
        Trims out any '.hitagifs/dirs/' entries.

        :rtype: :class:`list`

        """
        assert isinstance(file, str)
        try:
            output = subprocess.check_output(
                ['find', '-L', self.root, '-samefile', file])
        except FileNotFoundError:
            raise DependencyError("find could not be found; \
                probably findutils is not installed")
        output = output.decode().rstrip().split('\n')
        for x in iter(output):
            if '.hitagifs/dirs/' in x:
                output.remove(x)
        return output

    def listtags(self, file):
        """Return a list of all tags of `file`

        :rtype: :class:`list`

        """
        assert isinstance(file, str)
        files = self.listpaths(file)
        return [os.path.dirname(file).replace(self.root + '/', '') for file in
                files]

    def convert(self, dir, alt=None):
        """Convert a directory to a symlink.

        If `dir` is in ``.dantalian/dirs`` (smartassery), :meth:`convert`
        raises :exc:`LibraryError`.  If `dir` is a symlink (probably already
        converted), :meth:`convert` returns without doing anything.  If its
        name conflicts, :exc:`FileExistsError` will be raised.  If `dir` is not
        a directory, :exc:`NotADirectoryError` will be raised.  If `alt` is
        given, the alternate name will be used for the copy kept in
        ``.dantalian/dirs``.

        """
        logger.debug('convert(%r, %r)', dir, alt)
        _convertto(*_convertcheck(dir, libpath.dirsdir(self.root), alt))

    def cleandirs(self):
        """Clean converted directories

        Remove directories in the library's converted directories directory
        which do not have a symlink in the library that references them.  Nuke
        them with shutil.rmtree
        """
        _cleandirs(self.root)

    def find(self, tags):
        """Return a list of files with all of the given tags.

        `tags` is a list. `tags` is left unchanged.  Returns a list.  File
        paths are absolute and are paths to the hard link under the first tag
        given.

        :rtype: :class:`list`

        """
        assert len(tags) > 0
        logger.debug("find(%r)", tags)
        map = dict((os.lstat(x), x) for x in libpath.listdir(tags[0]))
        logger.debug("using map %r", map)
        inodes = functools.reduce(set.intersection, (
            set(os.lstat(x) for x in libpath.listdir(y)) for y in tags))
        logger.debug("found unique inodes %r", inodes)
        return [map[x] for x in inodes]

    def rm(self, file):
        """Removes all tags from `file`.

        `file` is a path relative to the current dir.  If `file` is not tagged,
        nothing happens.  If a file cannot be removed (for whatever reason), it
        is skipped, a warning is logged, and :meth:`rm` returns ``1``.
        Otherwise, returns ``0``.

        .. warning::
            In essence, this removes all tracked hard links to `file`!  If no
            other hard links exist, `file` is deleted.

        :rtype: :class:`int`

        """
        assert isinstance(file, str)
        error = 0
        for file in self.listpaths(file):
            logger.debug('unlinking %r', file)
            try:
                os.unlink(file)
            except OSError as e:
                logger.warn(e)
                logger.warn('Could not unlink %r', file)
                error = 1
        return error

    def rename(self, file, new):
        """Rename tracked file.

        Rename all tracked hard links of `file` to `new`.  If file is not
        tagged, nothing happens.  If any name collisions exist, nothing
        will be renamed and :exc:`FileExistsError` will be raised.

        """
        assert isinstance(file, str)
        assert isinstance(new, str)
        files = self.listpaths(file)
        logger.debug('found to rename %r', files)
        for file in files:
            head = os.path.dirname(file)
            new = os.path.join(head, new)
            if os.path.exists(new):
                raise FileExistsError('{} exists'.format(new))
        logger.info('rename check okay')
        for file in files:
            head = os.path.dirname(file)
            new = os.path.join(head, new)
            logger.debug('renaming %r %r', file, new)
            os.rename(file, new)

    def tagpath(self, tag):
        """Get absolute path of `tag`.

        Raise NotADirectoryError if tag doesn't exist
        :rtype: :class:`str`

        """
        path = os.path.join(self.root, tag)
        if not os.path.isdir(path):
            raise NotADirectoryError(
                "Tag {} doesn't exist (or isn't a directory)".format(tag))
        return os.path.abspath(path)

    def fix(self):
        logger.info('Checking if moved')
        if not self._moved:
            logger.info('Not moved so doing nothing')
            return
        logger.info('Move detected; fixing')
        files = libpath.findsymlinks(self.root)
        logger.debug('found symlinks %r', files)
        olddir = libpath.dirsdir(self._moved)
        newdir = libpath.dirsdir(self.root)
        libpath.fixsymlinks(files, olddir, newdir)
        logger.debug('writing %r', libpath.rootfile(self.root))
        with open(libpath.rootfile(self.root), 'w') as f:
            f.write(self.root)
        logger.info('finished fixing')

    def maketree(self):
        logger.info("making tree")
        if os.path.exists(libpath.ctreefile(self.root)):
            logger.info("using custom")
            name = 'custom'
            path = libpath.ctreefile(self.root)
            custom = importlib.SourceFileLoader(name, path).load_module(name)
            return custom.maketree(self.root)
        else:
            logger.info("using auto")
            return _maketree(self, libpath.treefile(self.root))

    def mount(self, path):
        return mount.mount(path, self, self.maketree())


def _cleandirs(root):
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


def _maketree(root, config):
    """Make a FSNode tree

    root is an instance of Library.  config is file path.
    """
    logger.debug("_maketree(%r, %r)", root, config)
    with open(config) as f:
        dat = json.load(f)
    r = tree.RootNode(root)
    for x in dat:
        mount, tags = x['mount'], x['tags']
        logger.debug("doing %r, %r", mount, tags)
        mount = mount.lstrip('/').split('/')
        y = r
        for x in mount[:-1]:
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
        x = mount[-1]
        if x not in y:
            logger.debug("making TagNode at %r[%r]", y, x)
            y[x] = tree.TagNode(root, tags)
        else:
            logger.debug("replacing node at %r[%r]", y, x)
            y[x] = tree.fs2tag(y[x])
    return r


def _convertcheck(dir, to, alt):
    """
    Parameters:

    dir: directory to convert
    to: dantalian library dirsdir
    alt: alternate name (str or None)

    Returns tuple of arguments to _convertto
    """
    logger.debug('_convertcheck(%r, %r, %r)', dir, to, alt)
    assert isinstance(dir, str)
    assert isinstance(to, str)
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
    if libpath.samefile(dirname, to):
        raise LibraryError("{} is in special directory".format(dirname))
    logger.info("Check okay")

    if alt is not None:
        assert isinstance(alt, str)
        basename = alt
    new = os.path.join(to, basename)
    logger.info("Checking name conflict")
    if os.path.exists(new):
        raise FileExistsError('{} exists'.format(new))
    logger.info("Check okay")
    return (dir, new)


def _convertto(dir, target):
    logger.debug('_convertto(%r, %r, %r)', dir, linktarget, movetarget)

    logger.debug("moving %r to %r", dir, target)
    os.rename(dir, target)
    logger.debug("linking %r to %r", dir, target)
    os.symlink(target, dir)


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


class FUSELibrary(Library):

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


class LibraryError(Exception):
    """Library error"""
