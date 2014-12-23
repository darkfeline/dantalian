"""
This module contains library operations for directory tagging.

Directory tags exist either internally or externally.  Internal tags are stored
in a special folder in the directory and is considered canonical.  External
tags are stored as symbolic links created from the internal tags.  These
symlinks are absolute and start with two slashes.  External tags are not
considered canonical.
"""

import os

from dantalian import pathlib
from . import base
from . import tags

DTAGS_FILE = '.dtags'


def tag(root, target, tagname):
    """Tag target directory with given tag.

    Args:
        root: Path of root.
        target: Path of directory to tag.
        tagname: Tag.

    If the directory is already tagged internally, nothing happens.  If it is
    not, it will be tagged internally and externally.
    """
    tags_file = os.path.join(target, DTAGS_FILE)
    with open(tags_file, 'r+') as duplex:
        current_tags = duplex.read().splitlines()
        if tagname in current_tags:
            return
        duplex.write(tagname + '\n')
    name = os.path.basename(target)
    target = pathlib.special_target(target)
    dest = tags.tag2path(root, tagname)
    pathlib.free_name_do(dest, name, lambda dest: os.symlink(target, dest))


def untag(root, target, tagname):
    """Remove tag from target directory.

    Args:
        root: Path of root.
        target: Path of directory to untag.
        tagname: Tag.

    If the directory is not tagged internally, nothing happens.  If it is, it
    will be untagged internally and external untagging will be attempted.
    """
    tags_file = os.path.join(target, DTAGS_FILE)
    with open(tags_file, 'r+') as duplex:
        current_tags = duplex.read().splitlines()
        if tagname not in current_tags:
            return
        current_tags = [tag for tag in current_tags if tag != tagname]
        duplex.seek()
        duplex.writelines(tag + '\n' for tag in current_tags)
        duplex.truncate()
    target = pathlib.special_target(target)
    dirpath = tags.tag2path(root, tagname)
    for path in pathlib.listdirpaths(dirpath):
        if os.path.islink(path) and os.readlink(path) == target:
            os.unlink(path)


def rename(root, target, newname):
    """Rename directory and external tags.

    Args:
        root: Path of root.
        target: Path of directory to rename.
        newname: New name.

    Will find a name as necessary.  External tags will be renamed if they
    exist.
    """
    target = os.path.normpath(target)  # strip trailing slashes for dirs
    dirpath, _ = os.path.split(target)
    new_target = pathlib.free_name_do(
        dirpath, newname, lambda dst: pathlib.rename_safe(target, dst))
    tags_file = os.path.join(target, DTAGS_FILE)
    new_target = pathlib.special_target(new_target)
    with open(tags_file, 'r') as rfile:
        current_tags = rfile.read().splitlines()
    for tag_ in current_tags:
        tagpath = tags.path(root, tag_)
        for path in pathlib.listdirpaths(tagpath):
            if os.path.islink(path) and os.readlink(path) == target:
                os.unlink(path)
                pathlib.free_name_do(tagpath, newname,
                                     lambda dst: os.symlink(new_target, dst))


def load_dir(root, target):
    """Load directory's internal tags into external tags."""
    tags_file = os.path.join(target, DTAGS_FILE)
    with open(tags_file, 'r') as infile:
        tags_ = infile.read().splitlines()
    target = pathlib.special_target(target)
    name = os.path.basename(target)
    for tag_ in tags_:
        tagpath = tags.path(root, tag_)
        pathlib.free_name_do(tagpath, name,
                             lambda dest: os.symlink(target, dest))


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
