import os


class HitagiFS:

    """
    HitagiFS virtual file system

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
        self.root = os.path.abspath(root)


class FSError(Exception):
    pass

__all__ = [HitagiFS, FSError]
