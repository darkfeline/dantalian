"""
This package contains high-level functions for performing library operations,
built from the simpler functions in submodules.

Serves as a public interface to library functionality.

"""

from collections import deque
import logging
import os
import shlex

from . import errors
from . import baselib
from . import taglib
from . import dirlib

# exported as module API
from .baselib import search
from .taglib import init_root
from .taglib import find_root

_LOGGER = logging.getLogger(__name__)


def tag(basepath, target, name):
    """Tag target file-or-directory with given name.

    Args:
        basepath: Base path for tag conversions.
        target: Tag or path to target.
        name: Tag or path.

    If target is already tagged, nothing happens.
    """
    if os.path.isfile(target):
        target = taglib.path(basepath, target)
        name = taglib.path(basepath, name)
        baselib.tag(target, name)
    else:
        pass


def untag(basepath, target, name):
    """Remove tag from target file-or-directory.

    Args:
        basepath: Base path for tag conversions.
        target: Tag or path to target.
        name: Tag or path.

    If file is not tagged, nothing happens.
    """
    if os.path.isfile(target):
        target = taglib.path(basepath, target)
        name = taglib.path(basepath, name)
        baselib.untag(target, name)
    else:
        pass


def rename(basepath, target, newname):
    """Rename all links to the target file-or-directory.

    Args:
        basepath: Base path for tag conversions.
        target: Tag or path to target.
        newname: New filename.

    Attempt to rename all links to the target under the basepath to
    newname, finding a name as necessary.
    """
    if os.path.isfile(target):
        target = taglib.path(basepath, target)
        baselib.rename(basepath, target, newname)
    else:
        pass


def remove(basepath, target):
    """Remove all links to the target file-or-directory.

    Args:
        basepath: Base path for tag conversions.
        target: Tag or path to target.

    Remove all links to the target under the basepath.
    """
    if os.path.isfile(target):
        target = taglib.path(basepath, target)
        baselib.remove(basepath, target)
    else:
        pass


def list_links(basepath, target):
    """List all links to the target file-or-directory.

    Args:
        basepath: Base path for tag conversions.
        target: Tag or path to target.

    Returns:
        Generator yielding paths.
    """
    if os.path.isfile(target):
        target = taglib.path(basepath, target)
        return baselib.list_links(basepath, target)
    else:
        pass


def parse_query(basepath, query):
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
            parse_list.append(dirlib.DirNode(token))
        elif token == 'AND':
            parse_stack.append(parse_list)
            parse_stack.append(baselib.AndNode)
            parse_list = []
        elif token == 'OR':
            parse_stack.append(parse_list)
            parse_stack.append(baselib.OrNode)
            parse_list = []
        elif token == 'MINUS':
            parse_stack.append(parse_list)
            parse_stack.append(baselib.MinusNode)
            parse_list = []
        elif token == ')':
            node_type = parse_stack.pop()
            node = node_type(parse_list)
            parse_list = parse_stack.pop()
            parse_list.append(node)
        else:
            token = taglib.path(basepath, token)
            parse_list.append(dirlib.DirNode(token))
    if len(parse_list) != 1:
        raise ParseError(parse_stack, parse_list,
                         "Not exactly one node at top of parse")
    return parse_list[0]


class ParseError(errors.Error):

    """Error parsing query."""

    def __init__(self, parse_stack, parse_list, msg=''):
        super().__init__()
        self.parse_stack = parse_stack
        self.parse_list = parse_list
        self.msg = msg

    def __str__(self):
        return "{}\nstack={}\nlist={}".format(
            self.msg, self.parse_stack, self.parse_list)

    def __repr__(self):
        return "ParseError({!r}, {!r}, {!r})".format(
            self.parse_stack, self.parse_list, self.msg)
