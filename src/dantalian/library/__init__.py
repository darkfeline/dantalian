"""
This package contains high-level functions for performing library operations,
built from the simpler functions in submodules.

Serves as a public interface to library functionality.

"""

from collections import deque
import logging
import os
import shlex
import shutil

from dantalian import oserrors

from . import errors
from . import baselib
from . import taglib
from . import dirlib

# exported as module API
from .baselib import search
from .taglib import init_library
from .taglib import find_library

_LOGGER = logging.getLogger(__name__)


def _get_tag_path(rootpath, name):
    """Return tuple containing tagname and path."""
    if taglib.is_tag(name):
        tagname = name
        path = taglib.tag2path(rootpath, name)
    else:
        tagname = taglib.path2tag(rootpath, name)
        path = name
    return (tagname, path)


# TODO use only paths, not tagnames.
def tag(rootpath, target, name):
    """Tag target file-or-directory with given name.

    Args:
        rootpath: Rootpath to resolve tagnames.
        target: Tagname or path to target.
        name: Tagname or path.
    """
    target = taglib.path(rootpath, target)
    if os.path.isfile(target):
        path = taglib.path(rootpath, name)
        if os.path.isdir(path):
            baselib.tag_with(target, path)
        elif not os.path.exists(path):
            os.link(target, path)
        else:
            raise oserrors.file_exists(target, path)
    if os.path.isdir(target):
        tagname, path = _get_tag_path(rootpath, name)
        if os.path.isdir(path):
            basename = os.path.basename(target)
            tagname = os.path.join(tagname, basename)
            path = os.path.join(path, basename)
        dirlib.tag(target, tagname)
        dirlib.make_symlink(target, path)
    else:
        raise oserrors.file_not_found(target)


def untag(rootpath, target, name):
    """Remove tag with given name from target file-or-directory.

    Args:
        rootpath: Rootpath to resolve tagnames.
        target: Tagname or path to target.
        name: Tagname or path.
    """
    target = taglib.path(rootpath, target)
    if os.path.isfile(target):
        path = taglib.path(rootpath, name)
        if os.path.isdir(path):
            baselib.untag_with(target, path)
        elif os.path.exists(path) and os.path.samefile(target, path):
            os.unlink(path)
        else:
            return
    if os.path.isdir(target):
        tagname, path = _get_tag_path(rootpath, name)
        if os.path.isdir(path):
            dirlib.untag_dirname(target, path)
        else:
            dirlib.untag(target, tagname)
    else:
        raise oserrors.file_not_found(target)


def list_links(rootpath, target):
    """List all links to the target file.

    Args:
        rootpath: Rootpath for tag conversions and finding links.
        target: Tagname or path to target.

    Returns:
        Generator yielding paths.
    """
    if os.path.isfile(target):
        target = taglib.path(rootpath, target)
        return baselib.list_links(rootpath, target)
    elif os.path.isdir(target):
        raise oserrors.is_a_directory(target)
    else:
        raise oserrors.file_not_found(target)


def list_tags(rootpath, target):
    """List all tags of the target directory.

    Args:
        rootpath: Rootpath for tag conversions and finding links.
        target: Tagname or path to target.

    Returns:
        Generator yielding tagnames.
    """
    if os.path.isdir(target):
        target = taglib.path(rootpath, target)
        return dirlib.list_tags(target)
    elif os.path.isfile(target):
        raise oserrors.not_a_directory(target)
    else:
        raise oserrors.file_not_found(target)


def move(rootpath, src, dst):
    """Move src to dst and fix tags for directories.

    Args:
        rootpath: Rootpath for tag conversions.
        src: Source tagname or pathname.
        dst: Destination tagname or pathname.
    """
    src = taglib.path(rootpath, src)
    dst = taglib.path(rootpath, dst)
    if os.path.isfile(src):
        os.rename(src, dst)
    elif os.path.islink(src):
        os.rename(src, dst)
        if os.path.isdir(dst):
            src_tag = taglib.path2tag(rootpath, src)
            if dirlib.is_tagged(dst, src_tag):
                dst_tag = taglib.path2tag(rootpath, dst)
                dirlib.replace_tag(dst, src_tag, dst_tag)
    elif os.path.isdir(src):
        dirlib.unload(rootpath, src)
        dirlib.rename_all(src, dst)
        dirlib.load(rootpath, dst)
    else:
        raise oserrors.file_not_found(src)


def remove(rootpath, target):
    """Remove target and fix tags for symlinked directories.

    Args:
        rootpath: Rootpath for tag conversions.
        target: Target tagname or pathname.

    Raise an error if target is a directory (not a symlink).

    """
    target = taglib.path(rootpath, target)
    if os.path.isfile(target):
        os.unlink(target)
    elif os.path.islink(target):
        if os.path.isdir(target):
            tagname = taglib.path2tag(rootpath, target)
            dirlib.untag(target, tagname)
        os.unlink(target)
    elif os.path.isdir(target):
        raise oserrors.is_a_directory(target)
    else:
        raise oserrors.file_not_found(target)


def swap(rootpath, target):
    """Swap a directory with its symlink tag.

    Args:
        rootpath: Rootpath for tag conversions.
        target: Target symlink tagname or pathname.

    """
    target = taglib.path(rootpath, target)
    if os.path.islink(target) and os.path.isdir(target):
        here = target
        there = os.readlink(target)
        os.rename(here, there)
        os.symlink(here, there)
        here_tag = taglib.path2tag(rootpath, here)
        there_tag = taglib.path2tag(rootpath, there)
        dirlib.replace_tag(here, here_tag, there_tag)
    else:
        raise ValueError('{} is not a symlink to a directory'.format(target))


def rename_all(rootpath, target, newname):
    """Rename all links to the target file-or-directory.

    Args:
        rootpath: Base path for tag conversions and search.
        target: Tag or path to target.
        newname: New filename.

    Attempt to rename all links to the target under the rootpath to newname,
    finding a name as necessary.

    """
    target = taglib.path(rootpath, target)
    if os.path.isfile(target):
        baselib.rename_all(rootpath, target, newname)
    elif os.path.isdir(target):
        dirlib.rename_all(target, newname)
    else:
        raise oserrors.file_not_found(target)


def remove_all(rootpath, target):
    """Remove all links to the target file-or-directory.

    Args:
        rootpath: Base path for tag conversions and search.
        target: Tag or path to target.

    Remove all links to the target under the rootpath.

    """
    target = taglib.path(rootpath, target)
    if os.path.isfile(target):
        baselib.remove_all(rootpath, target)
    elif os.path.isdir(target):
        dirlib.unload(rootpath, target)
        shutil.rmtree(target)
    else:
        raise oserrors.file_not_found(target)


def load(rootpath, target):
    """Load symlinks from a directory's internal tags.

    Args:
        rootpath: Base path for tag conversions.
        target: Tag or path to target.

    """
    target = taglib.path(rootpath, target)
    if os.path.isdir(target):
        dirlib.load(rootpath, target)
    else:
        raise oserrors.not_a_directory(target)


def unload(rootpath, target):
    """Unload symlinks from a directory's internal tags.

    Args:
        rootpath: Base path for tag conversions.
        target: Tag or path to target.

    """
    target = taglib.path(rootpath, target)
    if os.path.isdir(target):
        dirlib.unload(rootpath, target)
    else:
        raise oserrors.not_a_directory(target)


def load_all(rootpath, top):
    """Load all directories.

    Args:
        rootpath: Base path for tag conversions.
        top: Top of directory tree to search.

    """
    top = taglib.path(rootpath, top)
    for dirpath, _, dirnames in os.walk(top):
        for dirname in dirnames:
            path = os.path.join(dirpath, dirname)
            dirlib.load(rootpath, path)


def unload_all(rootpath, top):
    """Unload all directories.

    Args:
        rootpath: Base path for tag conversions.
        top: Top of directory tree to search.

    """
    top = taglib.path(rootpath, top)
    for dirpath, _, dirnames in os.walk(top):
        for dirname in dirnames:
            path = os.path.join(dirpath, dirname)
            dirlib.unload(rootpath, path)


# TODO
# load_all
# unload_all
# clean
# import
# export


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
            parse_list.append(baselib.DirNode(token))
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
            parse_list.append(baselib.DirNode(token))
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
