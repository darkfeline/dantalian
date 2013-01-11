import os
import subprocess
import logging

__all__ = ['HitagiFS', 'FSError', 'DependencyError']
logger = logging.getLogger(__name__)


class HitagiFS:

    """
    HitagiFS virtual file system.

    .. automethod:: __init__

    """

    _root_dir = '.hitagifs'
    _root_file = os.path.join(_root_dir, 'root')
    _dirs_dir = os.path.join(_root_dir, 'dirs')

    @classmethod
    def init(cls, root):
        """Initialize a hitagiFS at `root`

        Calling :meth:`init` on an existing hitagiFS does no harm.  Returns an
        instance of :class:`HitagiFS`.

        """

        logger.debug('init(%s)', root)
        root_dir = os.path.join(root, cls._root_dir)
        logger.debug('mkdir %s', root_dir)
        try:
            os.mkdir(root_dir)
        except FileExistsError:
            logger.debug('skipping %s; exists', root_dir)
        root_file = os.path.join(root, cls._root_file)
        if not os.path.exists(root_file):
            logger.debug('writing %s', root_file)
            with open(root_file, 'w') as f:
                f.write(root)

        dirs = os.path.join(root, cls._dirs_dir)
        try:
            dirs = os.mkdir(dirs)
        except FileExistsError:
            logger.debug('skipping %s; exists', dirs)

        return cls(root)

    def __init__(self, root=None):
        """
        If `root` is ``None``, HitagiFS will search up the directory tree for
        the first hitagifs (a directory that contains ``.hitagifs``) it finds
        and use that.  If none are found, raises :exc:`FSError`.  Otherwise,
        `root` will be used.  Either way, the path will be normalized with
        :func:`os.path.abspath`.  If `root` is not a directory,
        :exc:`NotADirectoryError` will be raised.

        """
        if root is None:
            root = self._find_root(os.getcwd())
        if not os.path.isdir(root):
            raise NotADirectoryError("Root {} isn't a directory".format(root))
        self.root = os.path.abspath(root)
        logger.info('HitagiFS initialized')
        logger.debug('root is %s', self.root)
        logger.info('Checking if moved')
        with open(os.path.join(self.root, self.__class__._root_file)) as f:
            old_root = f.read()
        if old_root == self.root:
            logger.info('All clear')
        else:
            logger.info('Move detected; fixing')
            newdir = os.path.join(self.root, self.__class__._dirs_dir)
            files = self._get_symlinks()
            for file in files:
                old = os.readlink(file)
                oldbase = os.path.basename(old)
                new = os.path.join(newdir, oldbase)
                logger.debug("symlinking %s to %s", old, new)
                os.symlink(new, old)
            logger.info('finished fixing')

    def tag(self, file, tag):
        """Tag `file` with `tag`.

        `file` is relative to current dir. `tag` is relative to FS root.  If
        file is already tagged, :exc:`FileExistsError` is raised.

        """
        dest = self._get_tag_path(tag)
        name = os.path.basename(file)
        dest = os.path.join(dest, name)
        try:
            logger.debug('tagging %s %s', file, dest)
            os.link(file, dest)
        except FileExistsError:
            raise FileExistsError('File already tagged')

    def untag(self, file, tag):
        """Remove `tag` from `file`.

        `file` is relative to current dir. `tag` is relative to FS root.  If
        file is not tagged, :exc:`FileNotFoundError` is raised.

        """
        dest = self._get_tag_path(tag)
        name = os.path.basename(file)
        dest = os.path.join(dest, name)
        try:
            logger.debug('untagging %s %s', file, dest)
            os.unlink(dest)
        except FileNotFoundError:
            raise FileNotFoundError('File not tagged')

    def listtags(self, file):
        """Return a list of all tags of `file`"""
        files = self._get_all(file)
        return [os.path.dirname(file).replace(self.root, '') for file in files]

    def convert(self, dir, alt=None):
        """Convert a directory to a symlink.

        If `dir` is in ``.hitagifs/dirs`` (converting an already converted
        directory/smartassery), :meth:`convert()` returns without doing
        anything.  If its name conflicts, :exc:`FileExistsError` will be
        raised.  If `dir` is not a directory, :exc:`NotADirectoryError` will be
        raised.  If `alt` is given, the alternate name will be used for the
        copy kept in ``.hitagifs/dirs``.

        """
        if not os.path.isdir(dir):
            raise NotADirectoryError("{} is not a directory".format(dir))
        logger.info("Checking %s is not already converted", dir)
        dirs_dir = os.path.join(self.root, self.__class__._dirs_dir)
        dirbase, dirname = os.path.split(dir)
        if os.path.samefile(dirbase, dirs_dir):
            return
        logger.info("Check okay")
        if alt is not None:
            assert isinstance(alt, str)
            dirname = alt
        new = os.path.join(dirs_dir, dirname)
        logger.info("Checking name conflict")
        if os.path.exists(new):
            raise FileExistsError('{} exists'.format(new))
        logger.info("Check okay")
        logger.debug("moving %s to %s", dir, new)
        os.rename(dir, new)
        logger.debug("linking %s to %s", dir, new)
        os.symlink(new, dir)

    def find(self, tags):
        """Return a list of files with all of the given tags.

        `tags` is a list. `tags` is left unchanged.  Returns a list.

        """
        tag = tags[:].pop(0)
        logger.debug('filter tag %s', tag)
        path = self._get_tag_path(tag)
        files = set(os.listdir(path))
        logger.debug('found set %s', files)
        for tag in tags:
            logger.debug('filter tag %s', tag)
            path = self._get_tag_path(tag)
            files &= set(os.listdir(path))
            logger.debug('found set %s', files)
        return list(files)

    def rm(self, file):
        """Removes all tags from `file`.

        `file` is a path relative to the current dir.  If `file` is not tagged,
        nothing happens.

        .. warning::
            Currently has no safety measure if unlinking one of the hard links
            fails.  If that happens, state will be left halfway.

        .. warning::
            In essence, this removes all tracked hard links to `file`!  If no
            other hard links exist, `file` is deleted.

        """
        for file in self._get_all(file):
            logger.debug('unlinking %s', file)
            os.unlink(file)

    def rename(self, file, new):
        """Rename tracked file.

        Rename all tracked hard links of `file` to `new`.  If file is not
        tagged, nothing happens.  If any name collisions exist, nothing
        will be renamed and :exc:`FileExistsError` will be raised.

        """
        files = self._get_all(file)
        logger.debug('found to rename %s', files)
        for file in files:
            head = os.path.dirname(file)
            new = os.path.join(head, new)
            if os.path.exists(new):
                raise FileExistsError('{} exists'.format(new))
        logger.info('rename check okay')
        for file in files:
            head = os.path.dirname(file)
            new = os.path.join(head, new)
            logger.debug('renaming %s %s', file, new)
            os.rename(file, new)

    def _get_all(self, file):
        """Get all tracked hard links of `file`.

        Relies on 'find' utility, for sheer simplicity and speed.  If it cannot
        be found, :exc:`DependencyError` is raised.  Output paths are absolute.

        """
        try:
            output = subprocess.check_output(
                ['find', '-L', self.root, '-samefile', file])
        except FileNotFoundError:
            raise DependencyError("'find' could not be found")
        output = output.decode().rstrip().split('\n')
        return output

    def _get_symlinks(self):
        """Get all tracked symlinks.

        Relies on 'find' utility, for sheer simplicity and speed.  If it cannot
        be found, :exc:`DependencyError` is raised.  Output paths are absolute.

        """
        try:
            output = subprocess.check_output(
                ['find', self.root, '-type', 'l'])
        except FileNotFoundError:
            raise DependencyError("'find' could not be found")
        output = output.decode().rstrip().split('\n')
        return output

    def _get_tag_path(self, tag):
        """Get absolute path of `tag`."""
        path = os.path.join(self.root, tag)
        if not os.path.isdir(path):
            raise NotADirectoryError(
                "Tag {} doesn't exist (or isn't a directory)".format(tag))
        path = os.path.abspath(path)
        return path

    @classmethod
    def _find_root(cls, dir):
        """Find the first hitagiFS root directory above `dir`.

        If none are found, raises :exc:`FSError`.

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


class FSError(Exception):
    """File system error"""


class DependencyError(Exception):
    """Dependency error"""
