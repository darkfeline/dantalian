"""
This module contains various shared path-related functions.
"""

import os
from itertools import count

__all__ = []


def _public(func):
    """Public decorator."""
    __all__.append(func.__name__)
    return func


@_public
def listdirpaths(path):
    """Like os.listdir(), except return paths."""
    for entry in os.listdir(path):
        yield os.path.join(path, entry)


@_public
def resolve_name(directory, name):
    """Find a free filename in the given directory.

    Given a desired filename, this function attempts to find a filename
    that is not currently being used in the given directory, adding an
    incrementing index to the filename as necessary.

    Note that the returned filename might not work, as a file with that
    name might be created between being checked in the function and when
    it is actually used.  Program accordingly.

    Args:
        name: Desired filename.
        directory: Pathname of directory to look in.

    Returns:
        Filename.
    """
    files = os.listdir(directory)
    if name not in files:
        return name
    base, ext = os.path.splitext(name)
    i = count(1)
    while True:
        name = ''.join((base, '.', str(next(i)), ext))
        if name not in files:
            return name
