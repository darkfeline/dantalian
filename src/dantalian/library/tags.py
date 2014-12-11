"""
This module contains functions for working with tags and rooted libraries.
"""

import os


def is_tag(name):
    """Check if name is a tagname."""
    return name.startswith('//')


def path2tag(basepath, pathname):
    """Convert a pathname to a tagname."""
    return '//' + os.path.relpath(pathname, basepath)


def tag2path(basepath, tagname):
    """Convert a tagname to a pathname."""
    return os.path.join(basepath, tagname.lstrip('/'))


def path(basepath, name):
    """Return name as a path."""
    if is_tag(name):
        name = tag2path(basepath, name)
    return name


_ROOTDIR = '.dantalian'

def is_root(dirpath):
    """Return if path is a library root."""
    return os.path.isdir(os.path.join(dirpath, _ROOTDIR))


def find_root(dirpath=''):
    """Find library root.

    Return the path of first library root found above the given path.  Return
    None if no library root found.

    An empty string or no dirpath means to use the current directory.
    """
    dirpath = os.path.abspath(dirpath)
    _, dirpath = os.path.splitdrive(dirpath)
    while True:
        if is_root(dirpath):
            return dirpath
        elif dirpath in ('/', ''):
            return None
        else:
            dirpath, _ = os.path.split(dirpath)


def init_root(dirpath):
    """Initialize library root."""
    os.mkdir(os.path.join(dirpath, _ROOTDIR))


def get_resource(dirpath, resource_path):
    """Get resource path from library root."""
    return os.path.join(dirpath, _ROOTDIR, resource_path)
