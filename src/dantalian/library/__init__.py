"""
This package contains high-level functions for performing library operations,
built from the simpler functions in submodules.
"""

from collections import deque
import logging
import os
import shlex

from . import base
from . import rooted
from . import dir

_LOGGER = logging.getLogger(__name__)


def tag(basepath, target, name):
    """Tag target file-or-directory with given name.

    Args:
        basepath: Base path for tag conversions.
        target: Path to target.
        name: Tag or path.

    If target is already tagged, nothing happens.
    """
    if os.path.isfile(target):
        if rooted.is_tag(name):
            name = tag2path(basepath, name)
        base.tag(target, name)
    else:
        pass


def untag(basepath, target, name):
    """Remove tag from target file-or-directory.

    Args:
        basepath: Base path for tag conversions.
        target: Path to target.
        name: Tag or path.

    If file is not tagged, nothing happens.
    """
    if os.path.isfile(target):
        if rooted.is_tag(name):
            name = tag2path(basepath, name)
        base.untag(target, name)
    else:
        pass


def rename(basepath, target, newname):
    """Rename all links to the target file-or-directory.

    Args:
        basepath: Base path for tag conversions.
        target: Path to target.
        newname: New filename.

    Attempt to rename all links to the target file under the basepath to
    newname, finding a name as necessary.
    """
    if os.path.isfile(target):
        if rooted.is_tag(name):
            name = tag2path(basepath, name)
        base.rename(basepath, target, name)
    else:
        pass


def remove(basepath, target):
    """Remove all links to the target file.

    Remove all links to the target file under the basepath.
    """


def list_tags(basepath, target):
    """List all links to the target file."""


def search(search_node):
    """Return files by tag query.

    Args:
        search_node: Root Node of search query tree

    Returns:
        Files by path.
    """


def parse_query(query):
    r"""Parse query string into query node tree.

    Query strings look like:

        'AND foo bar OR spam eggs ) AND \AND \OR \) \\\) ) )'

    which parses to:

        AndNode(
            DirNode('foo'),
            DirNode('bar'),
            OrNode(
                DirNode('spam'),
                DirNode('eggs')),
            AndNode(
                DirNode('AND'),
                DirNode('OR')),
                DirNode(')'),
                DirNode('\\)'))
    """
    tokens = deque(shlex.split(query))
    parse_stack = []
    parse_list = []
    while tokens:
        token = tokens.popleft()
        _LOGGER.debug("Parsing token %s", token)
        if token[0] == '\\':
            token = token[1:]
            parse_list.append(base.DirNode(token))
        elif token == 'AND':
            parse_stack.append(parse_list)
            parse_stack.append(base.AndNode)
            parse_list = []
        elif token == 'OR':
            parse_stack.append(parse_list)
            parse_stack.append(base.OrNode)
            parse_list = []
        elif token == ')':
            node_type = parse_stack.pop()
            node = node_type(parse_list)
            parse_list = parse_stack.pop()
            parse_list.append(node)
        else:
            parse_list.append(base.DirNode(token))
    if len(parse_list) != 1:
        raise errors.ParseError(parse_stack, parse_list,
                                "Not exactly one node at top of parse")
    return parse_list[0]
