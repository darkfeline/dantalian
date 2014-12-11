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
