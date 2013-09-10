import abc
import logging

__all__ = []
logger = logging.getLogger(__name__)


def _public(f):
    __all__.append(f.__name__)
    return f


@_public
class BaseLibrary(metaclass=abc.ABCMeta):

    """
    BaseLibrary is the abstract base class for library implementations.

    """

    @abc.abstractmethod
    def tag(self, file, tag):
        """
        `file` should be tagged with `tag` after call, regardless of
        whether it was before.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def untag(self, file, tag):
        """
        `file` should not be tagged with `tag` after call, regardless of
        whether it was before.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def listtags(self, file):
        """
        Return a list of all of the tags of `file`.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def find(self, tags):
        """
        Return a list of files that have all of the given tags in
        `tags`.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def mount(self, path, tree):
        """
        Mount a virtual representation of the library representation
        `tree` at `path`.

        """
        raise NotImplementedError


@_public
class LibraryError(Exception):
    pass


@_public
class TagError(LibraryError):
    pass
