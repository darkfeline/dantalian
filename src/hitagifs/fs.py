import os
import subprocess
import logging

__all__ = ['mount', 'HitagiFS', 'FSError', 'TagError', 'DependencyError']
logger = logging.getLogger(__name__)


class HitagiFS:

    """
    HitagiFS virtual file system.  All paths are handled internally as
    normalized absolute paths.  All external paths are sanitized with
    :func:`os.path.abspath` prior to being stored internally or returned.

    .. automethod:: __init__

    """

    def __init__(self, root=None):
        """
        If `root` is ``None``, HitagiFS will get `root` from the environment
        variable ``HITAGIFS_ROOT``.  If it's not set, it will raise
        :exc:`FSError`.  Otherwise, `root` will be used.  Either way, the path
        will be normalized with :func:`os.path.abspath`.

        """
        if root is None:
            try:
                root = os.environ['HITAGIFS_ROOT']
                logger.debug('got root from env')
            except KeyError:
                raise FSError('HITAGIFS_ROOT not set')
        if not os.path.isdir(root):
            raise FSError("Root {} isn't a directory".format(root))
        self.root = os.path.abspath(root)
        logger.info('HitagiFS initialized')
        logger.debug('root is %s', self.root)

    def tag(self, file, tag):
        """Tag `file` with `tag`.

        `file` is relative to current dir. `tag` is relative to FS root.  If
        file is already tagged, :exc:`TagError` is raised.

        """
        dest = self._get_tag_path(tag)
        name = os.path.basename(file)
        dest = os.path.join([dest, name])
        try:
            logger.debug('tagging %s %s', file, dest)
            os.link(file, dest)
        except OSError:
            raise TagError('File already tagged')

    def untag(self, file, tag):
        """Remove `tag` from `file`.

        `file` is relative to current dir. `tag` is relative to FS root.  If
        file is not tagged, :exc:`TagError` is raised.

        """
        dest = self._get_tag_path(tag)
        name = os.path.basename(file)
        dest = os.path.join([dest, name])
        try:
            logger.debug('untagging %s %s', file, dest)
            os.unlink(dest)
        except OSError:
            raise TagError('File not tagged')

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
            In essence, this removes all tracked hard links to `file`!  If no
            other hard links exist, `file` is deleted.

        """
        for file in self._get_all(file):
            logger.debug('unlinking %s', file)
            os.unlink(file)

    def rename(self, source, dest, tag=None):
        """Rename tracked file.

        Rename all tracked hard links of `source` to `dest`.  If file is not
        tagged, nothing happens.  If `tag` is given, only that singular
        instance of file is renamed.  If any name collisions exist, nothing
        will be renamed and :exc:`FSError` will be raised.

        .. warning::
            Don't use single rename yet.  Without a database, it will break
            tracking, probably.

        """
        output = self._get_all(source)
        logger.debug('found to rename %s', output)
        for file in output:
            head = os.path.dirname(file)
            new = os.path.join([head, dest])
            if os.path.exists(new):
                raise FSError('{} exists'.format(new))
        logger.info('rename check okay')
        for file in output:
            head = os.path.dirname(file)
            new = os.path.join([head, dest])
            logger.debug('renaming %s %s', file, new)
            os.rename(file, new)

    def _get_all(self, file):
        """Get all tracked hard links of `file`.

        Relies on 'find' utility, for sheer simplicity and
        speed.  If it cannot be found, :exc:`DependencyError` is raised.

        """
        try:
            output = subprocess.check_output(
                ['find', self.root, '-samefile', file])
        except FileNotFoundError:
            raise DependencyError("'find' could not be found")
        output = output.decode().rstrip().split('\n')

    def _get_tag_path(self, tag):
        path = os.path.join(self.root, tag)
        if not os.path.isdir(path):
            raise TagError(
                "Tag {} doesn't exist (or isn't a directory)".format(tag))
        path = os.path.abspath(path)
        return path


def mount(root):
    """Mount hitagiFS at `root`.

    Sets environment variable ``HITAGIFS_ROOT``.

    """
    os.environ['HITAGIFS_ROOT'] = os.path.abspath(root)


class FSError(Exception):
    """File system error"""


class TagError(Exception):
    """Tag error"""


class DependencyError(Exception):
    """Dependency error"""
