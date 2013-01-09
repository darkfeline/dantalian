"""
.. autoclass:: HitagiFS

.. autoclass:: FSError

.. autoclass:: TagError

"""
import os

__all__ = ['HitagiFS', 'FSError', 'TagError']


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
        """`file` is relative to current dir. `tag` is relative to FS root."""
        dest = self._get_tag_path(tag)
        name = os.path.basename(file)
        dest = os.path.join([dest, name])
        try:
            os.link(file, dest)
        except OSError:
            raise TagError('File already tagged')

    def untag(self, file, tag):
        """`file` is relative to current dir. `tag` is relative to FS root."""
        dest = self._get_tag_path(tag)
        name = os.path.basename(file)
        dest = os.path.join([dest, name])
        try:
            os.unlink(dest)
        except OSError:
            raise TagError('File not tagged')

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
