"""
This module contains various shared path-related functions.
"""

import os
from itertools import count


def listdirpaths(path):
    """Like os.listdir(), except return pathnames instead of filenames.

    Returns:
      A generator yielding paths.

    """
    for entry in os.listdir(path):
        yield os.path.join(path, entry)


def free_name(dirpath, name):
    """Find a free filename in the given directory.

    Given a desired filename, this function attempts to find a filename
    that is not currently being used in the given directory, adding an
    incrementing index to the filename as necessary.

    Note that the returned filename might not work due to race
    conditions. Program accordingly.

    Args:
        name: Desired filename.
        dirpath: Pathname of directory to look in.

    Returns:
        Filename.

    """
    files = os.listdir(dirpath)
    if name not in files:
        return name
    base, ext = os.path.splitext(name)
    i = count(1)
    while True:
        name = ''.join((base, '.', str(next(i)), ext))
        if name not in files:
            return name


def free_name_do(dirpath, name, callback):
    """Repeatedly attempt to do something while finding a free filename.

    Returns:
        Path of successful new name.
    """
    while True:
        dest = os.path.join(dirpath, free_name(dirpath, name))
        try:
            callback(dest)
        except FileExistsError:
            continue
        else:
            return dest


def rename_safe(src, dst):
    """Semi-safe rename.

    Raises FileExistsError if dst exists (instead of silently overwriting), but
    not safe from race conditions.

    """
    if os.path.isfile(dst):
        raise FileExistsError(
            'rename_safe() failed: {} -> {}'.format(src, dst))
    os.rename(src, dst)
