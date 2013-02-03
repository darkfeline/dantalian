import os
import subprocess
import logging

__all__ = ['HitagiFS', 'FSError', 'DependencyError']
logger = logging.getLogger(__name__)


class HitagiFS:

    _root_dir = '.hitagifs'
    _root_file = os.path.join(_root_dir, 'root')
    _dirs_dir = os.path.join(_root_dir, 'dirs')

    @classmethod
    def init(cls, root):
        """Initialize a hitagiFS at `root`

        Calling :meth:`init` on an existing hitagiFS does no harm.  Returns an
        instance of :class:`HitagiFS`.

        """

        logger.debug('init(%r)', root)
        root = os.path.abspath(root)
        root_dir = os.path.join(root, cls._root_dir)
        logger.debug('mkdir %r', root_dir)
        try:
            os.mkdir(root_dir)
        except FileExistsError:
            logger.debug('skipping %r; exists', root_dir)
        root_file = os.path.join(root, cls._root_file)
        if not os.path.exists(root_file):
            logger.debug('writing %r', root_file)
            with open(root_file, 'w') as f:
                f.write(root)

        dirs = os.path.join(root, cls._dirs_dir)
        try:
            dirs = os.mkdir(dirs)
        except FileExistsError:
            logger.debug('skipping %r; exists', dirs)

        return cls(root)

    @property
    def _moved(self):
        with open(os.path.join(self.root, self._root_file)) as f:
            old_root = f.read()
        if old_root == self.root:
            return False
        else:
            return True

    def fix(self):
        assert self._moved
        newdir = os.path.join(self.root, self._dirs_dir)
        files = self._get_symlinks()
        logger.debug('found symlinks %r', files)
        for set in files:
            f = set.pop(0)
            new = os.path.join(newdir, os.path.basename(os.readlink(f)))
            logger.debug("unlinking %r", f)
            os.unlink(f)
            logger.debug("symlinking %r to %r", f, new)
            os.symlink(new, f)
            for file in set:
                logger.debug("unlinking %r", file)
                os.unlink(file)
                logger.debug("linking %r to %r", file, f)
                os.link(f, file)
        root_file = os.path.join(self.root, self._root_file)
        logger.debug('writing %r', root_file)
        with open(root_file, 'w') as f:
            f.write(self.root)

    def __init__(self, root=None):
        """
        If `root` is :data:`None`, HitagiFS will search up the directory tree
        for the first hitagifs (a directory that contains ``.hitagifs``) it
        finds and use that.  If none are found, raises :exc:`FSError`.
        Otherwise, `root` will be used.  If `root` is not a directory,
        :exc:`NotADirectoryError` will be raised.

        """
        if root is None:
            root = self._find_root(os.getcwd())
        if not os.path.isdir(root):
            raise NotADirectoryError("Root {} isn't a directory".format(root))
        self.root = os.path.abspath(root)
        logger.info('HitagiFS initialized')
        logger.debug('root is %r', self.root)
        logger.info('Checking if moved')
        if not self._moved:
            logger.info('All clear')
        else:
            logger.info('Move detected; fixing')
            self.fix()
            logger.info('finished fixing')

    def tag(self, file, tag):
        """Tag `file` with `tag`.

        `file` is relative to current dir. `tag` is relative to FS root.  If
        `file` is already tagged, nothing happens.  This includes if the file
        is hardlinked under another name.  If `file` is an unconverted
        directory, :exc:`IsADirectoryError` will be raised.  If there's a name
        collision, :exc:`FileExistsError` is raised.

        """
        assert isinstance(file, str)
        assert isinstance(tag, str)
        if os.path.isdir(file) and not os.path.islink(file):
            raise IsADirectoryError(
                '{} is a directory; convert it first'.format(file))
        dest = self.tagpath(tag)
        name = os.path.basename(file)
        logger.info('checking if %r already tagged with %r', file, tag)
        for f in listdir(dest):
            if samefile(f, file):
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

        `file` is relative to current dir. `tag` is relative to FS root.  If
        file is not tagged, nothing happens.  Removes all hard links to `file`
        with `tag`.

        """
        assert isinstance(file, str)
        assert isinstance(tag, str)
        dest = self.tagpath(tag)
        inode = os.lstat(file)
        for f in listdir(dest):
            logger.debug('checking %r', f)
            if os.path.samestat(inode, os.lstat(f)):
                logger.debug('unlinking %r', f)
                os.unlink(f)

    def listpaths(self, file):
        """Return a list of all paths to `file`

        :rtype: :class:`list`

        """
        assert isinstance(file, str)
        return self._get_all(file)

    def listtags(self, file):
        """Return a list of all tags of `file`

        :rtype: :class:`list`

        """
        assert isinstance(file, str)
        files = self._get_all(file)
        return [os.path.dirname(file).replace(self.root + '/', '') for file in
                files]

    def convert(self, dir, alt=None):

        """Convert a directory to a symlink.

        If `dir` is in ``.hitagifs/dirs`` (smartassery), :meth:`convert` raises
        :exc:`FSError`.  If `dir` is a symlink (probably already converted),
        :meth:`convert` returns without doing anything.  If its name conflicts,
        :exc:`FileExistsError` will be raised.  If `dir` is not a directory,
        :exc:`NotADirectoryError` will be raised.  If `alt` is given, the
        alternate name will be used for the copy kept in ``.hitagifs/dirs``.

        """

        logger.debug('convert(%r, %r)', dir, alt)
        assert isinstance(dir, str)
        assert alt is None or isinstance(alt, str)
        dir = os.path.abspath(dir)

        logger.info("Checking %r is a dir", dir)
        if not os.path.isdir(dir):
            raise NotADirectoryError("{} is not a directory".format(dir))
        logger.info("Check okay")

        logger.info("Checking %r is not a symlink", dir)
        if os.path.islink(dir):
            return
        logger.info("Check okay")

        logger.info("Checking %r is not in dirs", dir)
        dirs_dir = os.path.join(self.root, self._dirs_dir)
        dirname, basename = os.path.split(os.path.abspath(dir))
        if samefile(dirname, dirs_dir):
            raise FSError("{} is in special directory".format(dirname))
        logger.info("Check okay")

        if alt is not None:
            assert isinstance(alt, str)
            basename = alt
        new = os.path.join(dirs_dir, basename)
        logger.info("Checking name conflict")
        if os.path.exists(new):
            raise FileExistsError('{} exists'.format(new))
        logger.info("Check okay")

        logger.debug("moving %r to %r", dir, new)
        os.rename(dir, new)
        logger.debug("linking %r to %r", dir, new)
        os.symlink(new, dir)

    def find(self, tags):
        """Return a list of files with all of the given tags.

        `tags` is an iterable. `tags` is left unchanged.  Returns a list.  File
        paths are absolute and are paths to the hard link under the first tag
        given.

        :rtype: :class:`list`

        """
        tags = list(tags)
        tag = tags.pop(0)
        logger.debug('filter tag %r', tag)
        path = self.tagpath(tag)
        files = list(listdir(path))
        logger.debug('found set %r', files)
        for tag in tags:
            logger.debug('filter tag %r', tag)
            path = self.tagpath(tag)
            good = []
            for file in files:
                for f in listdir(path):
                    if samefile(file, f):
                        good.append(file)
                        break
            files = good
            logger.debug('found set %r', files)
        return files

    def rm(self, file):
        """Removes all tags from `file`.

        `file` is a path relative to the current dir.  If `file` is not tagged,
        nothing happens.  If a file cannot be removed, it is skipped, a
        warning is logged, and :meth:`rm` returns ``1``.  Otherwise, returns
        :data:`None`.

        .. warning::
            In essence, this removes all tracked hard links to `file`!  If no
            other hard links exist, `file` is deleted.

        :rtype: :data:`None` or :class:`int`

        """
        assert isinstance(file, str)
        error = None
        for file in self._get_all(file):
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
        files = self._get_all(file)
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

    def _get_all(self, file):
        """Get all tracked hard links of `file`.

        Relies on 'find' utility, for sheer simplicity and speed.  If it cannot
        be found, :exc:`DependencyError` is raised.  Output paths are absolute.
        Trims out any '.hitagifs/dirs/' entries.

        :rtype: :class:`list`

        """
        try:
            output = subprocess.check_output(
                ['find', '-L', self.root, '-samefile', file])
        except FileNotFoundError:
            raise DependencyError("'find' could not be found")
        output = output.decode().rstrip().split('\n')
        for x in iter(output):
            if '.hitagifs/dirs/' in x:
                output.remove(x)
        return output

    def _get_symlinks(self):
        """Get all tracked symlinks.

        Returns a list of lists.  Symlinks that are the same inode are grouped
        together.  Relies on 'find' utility, for sheer simplicity and speed.
        If it cannot be found, :exc:`DependencyError` is raised.  Output paths
        are absolute.

        """
        try:
            output = subprocess.check_output(
                ['find', self.root, '-type', 'l'])
        except FileNotFoundError:
            raise DependencyError("'find' could not be found")
        output = output.decode().rstrip().split('\n')
        result = []
        for file in output:
            found = 0
            for set in result:
                if samefile(set[0], file):
                    set.append(file)
                    found = 1
                    break
            if not found:
                result.append([file])
        return result

    def tagpath(self, tag):
        """Get absolute path of `tag`.

        :rtype: :class:`str`

        """
        path = os.path.join(self.root, tag)
        if not os.path.isdir(path):
            raise NotADirectoryError(
                "Tag {} doesn't exist (or isn't a directory)".format(tag))
        return os.path.abspath(path)

    @classmethod
    def _find_root(cls, dir):
        """Find the first hitagiFS root directory above `dir`.

        If none are found, raises :exc:`FSError`.

        :rtype: :class:`str

        """
        assert os.path.isdir(dir)
        dir = os.path.abspath(dir)
        while dir:
            if cls._root_dir in os.listdir(dir):
                return dir
            else:
                if dir == '/':
                    break
                dir = os.path.dirname(dir)
        raise FSError('No root found')


def samefile(f1, f2):
    """If `f1` and `f2` refer to same inode.

    :rtype: :class:`bool`

    """
    return os.path.samestat(os.lstat(f1), os.lstat(f2))


def listdir(path):
    """Return full paths of files in `path`.

    :rtype: `iterator`

    """
    return iter(os.path.join(path, f) for f in os.listdir(path))


class FSError(Exception):
    """File system error"""


class DependencyError(Exception):
    """Dependency error"""
