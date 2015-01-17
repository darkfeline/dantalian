"""This module contains library operations for directory external tagging."""

import os

from .. import taglib

from . import internal


def _targets(link, target):
    """Check if symlink path is equal to target path."""
    return os.path.abspath(os.readlink(link)) == os.path.abspath(target)


def make_symlink(src, dst):
    """Try to symlink."""
    try:
        os.symlink(src, dst)
    except OSError:
        return


def load(root, dirpath):
    """Create symlink external tags for a directory."""
    tags = internal.list_tags(dirpath)
    target = os.path.abspath(dirpath)
    for tagname in tags:
        tagpath = taglib.tag2path(root, tagname)
        make_symlink(target, tagpath)


def unload(root, dirpath):
    """Remove symlinks using a directory's internal tags."""
    tags = internal.list_tags(dirpath)
    for tagname in tags:
        tagpath = taglib.tag2path(root, tagname)
        if os.path.islink(tagpath) and _targets(tagpath, dirpath):
            os.unlink(tagpath)


def clean(dirpath):
    """Remove all broken symlinks under the given directory."""
    for dirpath, _, filenames in os.walk(dirpath):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            if os.path.islink(path) and not os.path.exists(path):
                os.unlink(path)
