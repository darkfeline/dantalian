"""
All the functions in this module are scripts to be called from the command
line.  See the manpage for usage.
"""

import argparse
import logging
import os

from dantalian import library

__all__ = [
    't_global', 't_library', 't_sock',

    'tag', 'untag', 'tags', 'find', 'rm', 'rename', 'convert', 'fix', 'clean',
    'init', 'mount', 'mknode'
]
t_global = ['init']
t_library = [
    'tag', 'untag', 'tags', 'find', 'rm', 'rename', 'convert', 'fix', 'clean',
    'mount'
]
t_sock = ['mknode']
logger = logging.getLogger(__name__)


def tag(lib, *args):
    """
    Tags `file` with `tag` (Hard links `file` under `tag` directory with the
    same name).  If `file` is already tagged, does nothing.  If `file` is a
    directory, you'll need to convert it first.
    """
    logger.debug('tag(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian tag", add_help=False)
    parser.add_argument('-s')
    parser.add_argument('tag')
    parser.add_argument('file', nargs="+")
    args = parser.parse_args(args)
    for file in args.file:
        try:
            if not args.s:
                lib.tag(file, args.tag)
            else:
                lib.tag(args.tag, file)
        except IsADirectoryError:
            logger.warn('skipped %r; convert it first', file)


def untag(lib, *args):
    """
    Removes tag `tag` from `file` (Removes the hard link to `file` under `tag`
    directory).  If `file` isn't tagged, does nothing.
    """
    logger.debug('untag(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian untag", add_help=False)
    parser.add_argument('-s')
    parser.add_argument('tag')
    parser.add_argument('file', nargs="+")
    args = parser.parse_args(args)
    for file in args.file:
        if not args.s:
            lib.untag(file, args.tag)
        else:
            lib.untag(args.tag, file)


def tags(lib, *args):
    """
    Lists all the tags of `file` (Lists the directories that have hard links to
    `file`).
    """
    logger.debug('tags(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian tags", add_help=False)
    parser.add_argument('file')
    args = parser.parse_args(args)
    r = lib.listtags(args.file)
    for tag in r:
        print(tag)


def find(lib, *args):
    """
    Intersect tag search.  Lists all files that have all of the given tags.
    Lists files by the path to the hard link under the first tag given.
    """
    logger.debug('find(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian find", add_help=False)
    parser.add_argument('tags', nargs='+')
    args = parser.parse_args(args)
    r = lib.find(args.tags)
    for file in r:
        print(file)


def rm(lib, *args):
    """
    Removes the files given (Removes all hard links to the files under the root
    directory).
    """
    logger.debug('rm(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian rm", add_help=False)
    parser.add_argument('files', nargs='+')
    args = parser.parse_args(args)
    for file in args.files:
        lib.rm(file)


def rename(lib, *args):
    """
    Renames all hard links of `file` to `new`.
    """
    logger.debug('rename(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian rename", add_help=False)
    parser.add_argument('file')
    parser.add_argument('new')
    args = parser.parse_args(args)
    lib.rename(args.source, args.dest)


def convert(lib, *args):
    """
    Converts directories so they can be tagged.  (Moves directories to special
    location '.dantalian/dirs' and replaces the original with a symlink
    pointing to the absolute path)
    """
    logger.debug('convert(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian convert", add_help=False)
    parser.add_argument('dir', nargs="+")
    args = parser.parse_args(args)
    for dir in args.dir:
        try:
            lib.convert(dir)
        except NotADirectoryError:
            logger.warn('%r is not a directory; skipping', dir)
        except FileExistsError:
            logger.warn('Name conflict %r; skipping', dir)


def fix(lib, *args):
    """
    Fixes symlinks after the library has been moved.  If it hasn't been moved,
    does nothing.
    """
    logger.debug('fix(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian fix", add_help=False)
    args = parser.parse_args(args)
    lib.fix()


def clean(lib, *args):
    """
    Clean converted directories.
    """
    logger.debug('clean(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian clean", add_help=False)
    args = parser.parse_args(args)
    lib.cleandirs()


def init(*args):
    """
    Creates a library in `dir`.  If `dir` is omitted, creates a library in
    the current directory.
    """
    logger.debug('init(%r)', args)
    parser = argparse.ArgumentParser(prog="dantalian init", add_help=False)
    parser.add_argument('root', nargs="?", default=os.getcwd())
    args = parser.parse_args(args)
    library.init_library(args.root)


def mount(lib, *args):
    """
    Mount FUSE according to config files.
    """
    logger.debug('mount(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian mount", add_help=False)
    parser.add_argument('path')
    args = parser.parse_args(args)
    lib.mount(args.path, lib.maketree())
    logger.debug('exit')


def mknode(sock, *args):
    """
    Make a node in FUSE
    """
    logger.debug('mknode(%r, %r)', sock, args)
    parser = argparse.ArgumentParser(prog="dantalian mknode", add_help=False)
    parser.add_argument('path')
    parser.add_argument('tags', nargs="+")
    args = parser.parse_args(args)
    sock.send(" ".join(['mknode'] + ['/' + args.path] + args.tags).encode())
