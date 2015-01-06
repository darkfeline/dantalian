"""This module contains library operations for directory tagging.

A directory may contain a link to a file with the filename `.dtags`.  The file
to which this link points contains tagnames which are each terminated with a
single newline.

A directory is internally tagged with a tagname if and only if its `.dtags`
file contains that tagname.

A directory A is externally tagged with a directory B if and only if there
exists at least one special symlink in B that refers to A.

A directory A is externally tagged at pathname B if and only if B refers to a
special symlink that refers to A.

Given a rootpath, a directory A being internally tagged with a tagname B is
equivalent to A being externally tagged at the pathname which is equivalent
to B.

Dantalian only considers and manipulates internal tags.  Dantalian will attempt
to keep a directory's external tags consistent with its internal tags where
convenient.

"""

import os

from . import pathlib
from . import baselib
from . import taglib

DTAGS_FILE = '.dtags'


def dtags_file(dirpath):
    """Get the path of a directory's dtags file."""
    return os.path.join(dirpath, DTAGS_FILE)


def is_spsymlink(pathname):
    """Return whether the given path is a special symlink target."""
    return pathname.startswith('//')


def spsymlink(pathname):
    """Make the given path into a special symlink target.

    Args:
        pathname: Pathname.

    This also normalizes an existing special symlink target:

    ////foo//bar -> //foo/bar

    """
    return '/' + os.path.abspath(pathname)


def tag(root, target, tagname):
    """Tag target directory with the given tagname.

    Args:
        root: Rootpath.
        target: Path of directory to tag.
        tagname: Tagname.

    If the directory is already tagged internally, nothing happens.  If it is
    not, it will be tagged internally and externally.

    In the event the creation of a symlink fails, the directory will still be
    tagged internally, but external tagging has failed and an OSError will be
    raised.

    """
    tagname = tagname.rstrip('/')  # can't tag into a directory
    tags_file = dtags_file(target)
    with open(tags_file, 'r+') as duplex:
        current_tags = duplex.read().splitlines()
        if tagname in current_tags:
            return
        duplex.write(tagname + '\n')
    symlink_src = spsymlink(target)
    symlink_name = taglib.path(root, tagname)
    os.symlink(symlink_src, symlink_name)


def untag(root, target, tagname):
    """Remove tag from target directory.

    Args:
        root: Rootpath.
        target: Path of directory to untag.
        tagname: Tagname.

    If the directory is not tagged internally, nothing happens.  If it is, it
    will be untagged internally and external untagging will be attempted.

    """
    tagname = tagname.rstrip('/')  # can't tag into a directory
    tags_file = dtags_file(target)
    with open(tags_file, 'r+') as duplex:
        current_tags = duplex.read().splitlines()
        if tagname not in current_tags:
            return
        current_tags = [tag for tag in current_tags if tag != tagname]
        duplex.seek()
        duplex.writelines(tag + '\n' for tag in current_tags)
        duplex.truncate()
    target = spsymlink(target)
    path = taglib.path(root, tagname)
    if os.path.islink(path) and os.readlink(path) == target:
        os.unlink(path)


def list_tags(dirpath):
    """Return a list of tagnames of a directory."""
    tags_file = dtags_file(dirpath)
    with open(tags_file) as rfile:
        tags = rfile.read().splitlines()
    return tags


def is_tagged(dirpath, tagname):
    """Return if directory is tagged with tagname.

    Args:
        dirpath: Path of directory.
        tagname: Tagname.

      """
    return tagname in list_tags(dirpath)


def rename(target, newname):
    """Rename a directory.

    Args:
        target: Path of directory to rename.
        newname: New name.

    Rename the directory and the basenames of all of its tagnames.  Doesn't
    touch external tags.

    """
    parent_dir = os.path.dirname(target.rstrip('/'))
    target = pathlib.free_name_do(
        parent_dir, newname, lambda dst: pathlib.rename_safe(target, dst))
    tags_file = dtags_file(target)
    with open(tags_file, 'r+') as duplex:
        tags = duplex.read().splitlines()
        tags = [os.path.join(os.path.dirname(tag), newname) for tag in tags]
        duplex.seek()
        duplex.writelines(tag + '\n' for tag in tags)
        duplex.truncate()


def load_dir(root, dirpath):
    """Create special symlink external tags for a directory."""
    tags = list_tags(dirpath)
    target = spsymlink(dirpath)
    for tag_ in tags:
        tagpath = taglib.path(root, tag_)
        dirname, basename = os.path.split(tagpath)
        pathlib.free_name_do(dirname, basename,
                             lambda dst: os.symlink(target, dst))


def clean(dirpath):
    """Remove all special symlinks under the given directory."""
    for dirpath, _, filenames in os.walk(dirpath):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            if os.path.islink(path) and is_spsymlink(os.readlink(path)):
                os.unlink(path)


class DirNode(baselib.DirNode):

    """DirNode extended with tagged directory support.

    Special symlinks in the DirNode's directory will be replaced with the info
    of the directories they refer to.

    """

    # pylint: disable=too-few-public-methods

    @staticmethod
    def _get_inode(filepath):
        """Return inode and path pair."""
        if os.path.islink(filepath):
            target = os.readlink(filepath)
            if is_spsymlink(target) and os.path.isdir(target):
                return (os.lstat(target), filepath)
            return super()._get_inode(filepath)
