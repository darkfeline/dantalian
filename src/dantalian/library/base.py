"""
This module contains basic library operations.
"""

import os

from dantalian import pathlib


def tag(target, tagpath):
    """Tag target with given tag.

    Args:
        target: Path of file to tag.
        tagpath: Path of tag.

    If file is already tagged, nothing happens.  This includes if
    the file is hardlinked in the respective directory under
    another name.
    """
    for entry in pathlib.listdirpaths(tagpath):
        if os.path.samefile(entry, target):
            return
    name = os.path.basename(target)
    while True:
        dest = os.path.join(tagpath, pathlib.resolve_name(tagpath, name))
        try:
            os.link(target, dest)
        except FileExistsError:
            continue
        else:
            break


def untag(target, tagpath):
    """Remove tag from target.

    Args:
        target: Path to target file.
        tagpath: Path to tag.

    If file is not tagged, nothing happens.  Remove *all* hard
    links to the file in the directory corresponding to the given
    tag.
    """
    inode = os.lstat(target)
    for candidate in pathlib.listdirpaths(tagpath):
        candidate_inode = os.lstat(candidate)
        if os.path.samestat(inode, candidate_inode):
            os.unlink(candidate)


class _Struct:
    """Simple struct-like implementation."""
    # pylint: disable=too-few-public-methods
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)
