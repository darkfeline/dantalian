"""This module contains functions for working with tagnames and libraries."""

import os


def is_tag(name):
    """Check if name is a tagname."""
    return name.startswith('//')


def path2tag(rootpath, pathname):
    """Convert a pathname to a tagname."""
    return '//' + os.path.relpath(pathname, rootpath)


def tag2path(rootpath, tagname):
    """Convert a tagname to a pathname."""
    return os.path.join(rootpath, tagname.lstrip('/'))


def path(rootpath, name):
    """Return tagname or pathname as a pathname."""
    if is_tag(name):
        name = tag2path(rootpath, name)
    return name


_ROOTDIR = '.dantalian'

def is_library(dirpath):
    """Return whether dirpath refers to a library."""
    return os.path.isdir(os.path.join(dirpath, _ROOTDIR))


def find_library(dirpath=''):
    """Find library.

    Return the path of the first library found above the given path.  Return
    None if no library is found.

    An empty string means to use the current directory.

    """
    dirpath = os.path.abspath(dirpath)
    _, dirpath = os.path.splitdrive(dirpath)
    while True:
        if is_library(dirpath):
            return dirpath
        elif dirpath in ('/', ''):
            return None
        else:
            dirpath, _ = os.path.split(dirpath)


def init_root(dirpath):
    """Initialize library."""
    os.mkdir(os.path.join(dirpath, _ROOTDIR))


def get_resource(dirpath, resource_path):
    """Get the path of a resource for a library."""
    return os.path.join(dirpath, _ROOTDIR, resource_path)
