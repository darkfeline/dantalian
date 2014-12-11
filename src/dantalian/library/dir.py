"""
This module contains library operations for directory tagging.

Directory tags exist either internally or externally.  Internal tags are stored
in a special folder in the directory and is considered canonical.  External
tags are stored as symbolic links created from the internal tags.  These
symlinks are absolute and start with two slashes.  External tags are not
considered canonical.
"""

# pylint: disable=all

import os

from dantalian import pathlib
from . import base

DTAGS_FILE = '.dtags'


def tag(target, dirpath):
    """Tag target directory with given directory.

    Args:
        target: Path of directory to tag.
        dirpath: Path of directory.

    If the directory is already tagged, nothing happens.  If it is not, it will
    be tagged internally and externally.
    """
    dirpath = os.path.abspath(dirpath)
    tags_file = os.path.join(target, DTAGS_FILE)
    with open(tags_file, 'r+') as duplex:
        current_tags = duplex.readlines()
        if dirpath in current_tags:
            return
        duplex.write(dirpath + '\n')
    current_tags.append(dirpath)
    name = os.path.basename(target)
    target = pathlib.special_target(target)
    pathlib.resolve_do(dirpath, name, lambda dest: os.symlink(target, dest))


def untag(target, dirpath):
    """Remove tag from target directory.

    Args:
        target: Path of directory to untag.
        dirpath: Path of directory.

    If the directory is not tagged, nothing happens.  If it is, it will
    be untagged internally and external untagging will be attempted.
    """
    dirpath = os.path.abspath(dirpath)
    tags_file = os.path.join(target, DTAGS_FILE)
    with open(tags_file, 'r+') as duplex:
        current_tags = duplex.readlines()
        if dirpath not in current_tags:
            return
        current_tags = [tag for tag in current_tags if tag != dirpath]
        duplex.seek()
        duplex.writelines(tag + '\n' for tag in current_tags)
        duplex.truncate()
    target = pathlib.special_target(target)
    for entry in pathlib.listdirpaths(dirpath):
        if os.path.islink(entry) and os.readlink(entry) == target:
            os.unlink(entry)


def rename(basepath, target, newname):
    pass


def load_dir(target):
    """Load directory's internal tags into external tags."""
    target = os.path.abspath(target)
    tags_file = os.path.join(target, DTAGS_FILE)
    with open(tags_file, 'r') as infile:
        tags = infile.readlines()
    target = pathlib.special_target(target)
    for tag in tags:
        for entry in pathlib.listdirpaths(tag):
            if os.path.islink(entry) and os.readlink(entry) == target:
                break
            name = os.path.basename(target)
            pathlib.resolve_do(tag, name,
                               lambda dest: os.symlink(target, dest))


def parse_query(query):
    """Extended for directory tagging support."""
    tree = base.parse_query(query)
    return _convert_dirnodes(tree)


def _convert_dirnodes(node):
    """Recursively convert DirNodes to support directory tagging."""
    if isinstance(node, base.DirNode):
        return DirNode(node.dirpath)
    else:
        for i, child in enumerate(node.children):
            node.children[i] = _convert_dirnodes(child)
        return node


class DirNode(base.DirNode):

    """
    DirNode extended with tagged directory support.
    """

    # pylint: disable=too-few-public-methods

    @staticmethod
    def _get_inode(filepath):
        """Return inode and path pair."""
        if os.path.islink(filepath) and \
           pathlib.is_special_target(os.readlink(filepath)):
            return (os.lstat(os.readlink(filepath)), filepath)
        else:
            return super()._get_inode(filepath)
