"""This module contains library operations for directory tagging.

A directory may contain a link to a file with the filename `.dtags`.  The file
to which this link points contains tagnames which are each terminated with a
single newline.

A directory is internally tagged with a tagname if and only if its `.dtags`
file contains that tagname.

A directory A is externally tagged with a directory B if and only if there
exists at least one symlink in B that refers to A.

A directory A is externally tagged at pathname B if and only if B refers to a
symlink that refers to A.

Given a rootpath, a directory A being internally tagged with a tagname B is
equivalent to A being externally tagged at the pathname which is equivalent
to B.

Dantalian uses both internal and external tags, but internal tags are
considered more stable and reliable than external tags.

"""

import os

from . import pathlib
from . import baselib
from . import taglib

DTAGS_FILE = '.dtags'


def dtags_file(dirpath):
    """Get the path of a directory's dtags file."""
    return os.path.join(dirpath, DTAGS_FILE)


def targets(link, target):
    """Check if symlink path is equal to target path."""
    return os.path.abspath(os.readlink(link)) == os.path.abspath(target)


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
    target = os.path.abspath(target)
    tagname = tagname.rstrip('/')  # can't tag into a directory
    tags_file = dtags_file(target)
    with open(tags_file, 'r+') as duplex:
        current_tags = duplex.read().splitlines()
        if tagname in current_tags:
            return
        duplex.write(tagname + '\n')
    symlink_name = taglib.tag2path(root, tagname)
    os.symlink(target, symlink_name)


def filter_tags(target, func):
    """Remove all tags from target directory that satisfies the filter.

    Args:
        root: Rootpath.
        target: Path of directory to untag.
        func: Filter function.
    Return:
        List of removed tagnames.

    Doesn't touch external tags

    """
    tags_file = dtags_file(target)
    keep = []
    discard = []
    with open(tags_file, 'r+') as duplex:
        current_tags = duplex.read().splitlines()
        for tag_ in current_tags:
            if func(tag_):
                discard.append(tag_)
            else:
                keep.append(tag_)
        if discard:
            duplex.seek()
            duplex.writelines(tag + '\n' for tag in keep)
            duplex.truncate()
    return discard


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
    discard = filter_tags(target, lambda tag: tag == tagname)
    if not discard:
        return
    path = taglib.tag2path(root, tagname)
    if os.path.islink(path) and targets(path, target):
        os.unlink(path)


def untag_dirname(root, target, tagname):
    """Remove all tags with the given dirname from target directory.

    Args:
        root: Rootpath.
        target: Path of directory to untag.
        tagname: Tagname, purge all tags whose dirname equals this.

    All symlinks pointing to target in dirname will be removed.

    """
    tagname = tagname.rstrip('/')  # dirname doesn't have trailing slashes
    filter_tags(target, lambda tag: os.path.dirname(tag) == tagname)
    dirpath = taglib.tag2path(root, tagname)
    for path in pathlib.listdirpaths(dirpath):
        if os.path.islink(path) and targets(path, target):
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
    """Create symlink external tags for a directory."""
    tags = list_tags(dirpath)
    target = os.path.abspath(dirpath)
    for tag_ in tags:
        tagpath = taglib.tag2path(root, tag_)
        dirname, basename = os.path.split(tagpath)
        pathlib.free_name_do(dirname, basename,
                             lambda dst: os.symlink(target, dst))


def clean(dirpath):
    """Remove all broken symlinks under the given directory."""
    for dirpath, _, filenames in os.walk(dirpath):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            if os.path.islink(path) and not os.path.exists(os.readlink(path)):
                os.unlink(path)
