"""
This module contains functions for working with tags and rooted libraries.

This module contains advanced, bound library operations.

These operations extend the basic operations by binding libraries to a file
system pathname and allowing tag identifiers to be used.
"""

import os


def is_tag(name):
    """Check if name is a tagname."""
    return name.startswith('//')


def path2tag(basepath, pathname):
    """Convert a pathname to a tagname."""
    return os.path.relpath(pathname, basepath)


def tag2path(basepath, tagname):
    """Convert a tagname to a pathname."""
    return os.path.join(basepath, tagname.lstrip('/'))
