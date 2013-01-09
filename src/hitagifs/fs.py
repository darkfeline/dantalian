"""
.. autoclass:: HitagiFS

.. autoclass:: FSError

.. autoclass:: TagError

.. autoclass:: DependencyError

"""

import os
import subprocess

__all__ = ['HitagiFS', 'FSError', 'TagError', 'DependencyError']


class HitagiFS:

    """
    HitagiFS virtual file system.  All paths are handled internally as
    normalized absolute paths.  All external paths are sanitized with
    :func:`os.path.abspath` prior to being stored internally or returned.

    .. automethod:: tag

    .. automethod:: untag

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
            except KeyError:
                raise FSError('HITAGIFS_ROOT not set')
        if not os.path.isdir(root):
            raise FSError("Root {} isn't a directory".format(root))
        self.root = os.path.abspath(root)

    def tag(self, file, tag):
        """Tag `file` with `tag`.

        `file` is relative to current dir. `tag` is relative to FS root.  If
        file is already tagged, :exc:`TagError` is raised.

        """
        dest = self._get_tag_path(tag)
        name = os.path.basename(file)
        dest = os.path.join([dest, name])
        try:
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
            os.unlink(dest)
        except OSError:
            raise TagError('File not tagged')

    def find(self, tags):
        """Return a list of files with all of the given tags.

        `tags` is a list. `tags` is left unchanged.  Returns a list.

        """
        tag = tags[:].pop(0)
        path = self._get_tag_path(tag)
        files = set(os.listdir(path))
        for tag in tags:
            path = self._get_tag_path(tag)
            files &= set(os.listdir(path))
        return list(files)

    def rm(self, file):
        """Removes all tags from `file`.

        `file` is a path relative to the current dir.  If `file` is not tagged,
        nothing happens.  Relies on 'find' utility, for sheer simplicity and
        speed.  If it cannot be found, :exc:`DependencyError` is raised.

        In essence, this removes all tracked hard links to `file`!  If no other
        hard links exist, `file` is deleted.

        """
        try:
            output = subprocess.check_output(
                ['find', self.root, '-samefile', file])
        except FileNotFoundError:
            raise DependencyError("'find' could not be found")
        output = output.decode().rstrip().split('\n')
        for file in output:
            os.unlink(file)

    def _get_tag_path(self, tag):
        path = os.path.join(self.root, tag)
        if not os.path.isdir(path):
            raise TagError(
                "Tag {} doesn't exist (or isn't a directory)".format(tag))
        path = os.path.abspath(path)
        return path


class FSError(Exception):
    pass


class TagError(Exception):
    pass


class DependencyError(Exception):
    pass
