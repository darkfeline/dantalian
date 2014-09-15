"""
All the functions in this module are hooked in the dantalian script as
commands.  See the manpage for usage.

"""

import logging
import shlex
import os
import json
from functools import partial
import sys
import socket

from . import library
from . import pathlib as dpath

logger = logging.getLogger(__name__)


# Library commands {{{1
# Helper functions {{{2
def _unpack(args):
    """Unpack tags and files arguments."""
    files = args.f
    if not files:
        tags = args.t
        if not tags:
            if len(args.args) != 2:
                logger.error('Invalid number of arguments.')
                sys.exit(1)
            files = [args.args[0]]
            tags = [args.args[1]]
        else:
            if len(args.args) != 1:
                logger.error('Invalid number of arguments.')
                sys.exit(1)
            files = [args.args[0]]
    else:
        tags = args.t
        if not tags:
            if len(args.args) != 1:
                logger.error('Invalid number of arguments.')
                sys.exit(1)
            tags = [args.args[0]]
        else:
            if len(args.args) != 0:
                logger.error('Invalid number of arguments.')
                sys.exit(1)
    return files, tags


# tag {{{2
def tag(args):
    files, tags = _unpack(args)
    lib = library.open_library(args.root)
    f = files[0]
    bad_tags = []
    for t in tags:
        try:
            lib.tag(f, t)
        except IsADirectoryError:
            logger.error('%s is a directory.  Convert before tagging.',
                         f)
        except library.TagError:
            logger.error('%s is an invalid tag', t)
            bad_tags.append(t)
    for t in bad_tags:
        tags.remove(t)
    for f in files[1:]:
        for t in tags:
            try:
                lib.tag(f, t)
            except IsADirectoryError:
                logger.error('%s is a directory.  Convert before tagging.',
                             f)
                break


# untag {{{2
def untag(args):
    files, tags = _unpack(args)
    lib = library.open_library(args.root)
    f = files[0]
    bad_tags = []
    for t in tags:
        try:
            lib.untag(f, t)
        except library.TagError:
            logger.error('%s is an invalid tag', t)
            bad_tags.append(t)
    for t in bad_tags:
        tags.remove(t)
    for f in files[1:]:
        for t in tags:
            lib.untag(f, t)


# mktag {{{2
def mktag(args):
    lib = library.open_library(args.root)
    for t in args.tags:
        lib.mktag(t)


# rmtag {{{2
def rmtag(args):
    lib = library.open_library(args.root)
    for t in args.tags:
        lib.mktag(t)


# tags {{{2
def tags(args):
    lib = library.open_library(args.root)
    for tag in lib.listtags(args.file):
        print(tag, end=args.endline)


# find {{{2
def find(args):
    lib = library.open_library(args.root)
    if args.target_dir:
        target = args.target_dir
        if dpath.istag(target):
            target = dpath.pathfromtag(target, lib.root)
        if not os.path.isdir(target):
            logger.error("%s is not a directory", target)

        def func(f):
            name = os.path.basename(f)
            while True:
                dest = os.path.join(target, dpath.resolve_name(target, name))
                try:
                    os.link(f, dest)
                except FileExistsError:
                    continue
                else:
                    break
    else:
        func = partial(print, end=args.endline)
    for f in lib.find(args.tags):
        func(f)


# rm {{{2
def rm(args):
    lib = library.open_library(args.root)
    for file in args.files:
        lib.rm(file)


# rename {{{2
def rename(args):
    lib = library.open_library(args.root)
    lib.rename(args.file, args.new)


# convert {{{2
def convert(args):
    lib = library.open_library(args.root)
    for dir in args.dirs:
        try:
            lib.convert(dir)
        except NotADirectoryError:
            logger.error('%r is not a directory.', dir)
        except library.LibraryError:
            logger.error('%r is already converted.', dir)


# revert {{{2
def revert(args):
    lib = library.open_library(args.root)
    for dir in args.dirs:
        try:
            lib.revert(dir)
        except library.LibraryError as e:
            logger.error(str(e))


# fix {{{2
def fix(args):
    lib = library.open_library(args.root)
    lib.fix()


# clean {{{2
def clean(args):
    lib = library.open_library(args.root)
    lib.cleandirs()


# mount {{{2
def mount(args):
    lib = library.open_library(args.root)
    tree = lib.mount(args.path, lib.maketree())
    tree = tree.dump()
    with open(lib.treefile, 'w') as f:
        json.dump(tree, f)


# Global commands {{{1
# init {{{2
def init(args):
    library.init_library(args.path)


# Socket commands {{{1
# Helper functions {{{2
def _fix_path(root, path):
    """Fix path.

    If path is a tag, return as is.  Otherwise rebase path to root.

    Args:
        root: Absolute path where FUSE is mounted.
        path: Path relative to root.

    """
    if dpath.istag(path):
        return path
    else:
        return _rebase_path(root, path)


def _rebase_path(root, path):
    """Rebase path as an absolute path relative to the FUSE mount root.

    Args:
        root: Absolute path where FUSE is mounted.
        path: Path relative to root.

    """
    path = os.path.relpath(path, root)
    assert not path.startswith('..')
    return '/' + path


def _open_sock(root):
    """Load library and return socket and root path."""
    lib = library.open_library(root)
    if not isinstance(lib, library.ProxyLibrary):
        logger.error('Socket command can only be used with fuse')
        sys.exit(1)
    addr = lib.fusesock
    sock = socket.socket(socket.AF_UNIX)
    sock.connect(addr)
    return sock, lib.root


# mknode {{{2
def mknode(args):
    sock, mountroot = _open_sock(args.root)
    rebaser = partial(_fix_path, mountroot)
    path = rebaser(args.path)
    tags = [rebaser(t) for t in args.tags]
    sock.send(" ".join(
        ['mknode'] + [shlex.quote(path)] +
        [shlex.quote(x) for x in tags]
    ).encode())


# rmnode {{{2
def rmnode(args):
    sock, mountroot = _open_sock(args.root)
    rebaser = partial(_rebase_path, mountroot)
    paths = [rebaser(p) for p in args.paths]
    sock.send(" ".join(
        ['rmnode'] + [shlex.quote(paths)]
    ).encode())
