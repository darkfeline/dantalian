"""
All the functions in this module are scripts to be called from the command
line.  See the manpage for usage.
"""

import argparse
import logging
import os
import sys

from dantalian import library

logger = logging.getLogger(__name__)


def public(f):
    all = sys.modules[f.__module__].__dict__.setdefault('__all__', [])
    if f.__name__ not in all:
        all.append(f.__name__)
    return f


@public
def tag(lib, *args):
    """
    Tags `file` with `tag` (Hard links `file` under `tag` directory with the
    same name).  If `file` is already tagged, does nothing.  If `file` is a
    directory, you'll need to convert it first.
    """
    logger.debug('tag(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian tag", add_help=False)
    parser.add_argument('tag')
    parser.add_argument('file', nargs="+")
    args = parser.parse_args(args)
    for file in args.file:
        try:
            lib.tag(file, args.tag)
        except IsADirectoryError:
            logger.warn('skipped %r; convert it first', file)


@public
def untag(lib, *args):
    """
    Removes tag `tag` from `file` (Removes the hard link to `file` under `tag`
    directory).  If `file` isn't tagged, does nothing.
    """
    logger.debug('untag(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian utag", add_help=False)
    parser.add_argument('tag')
    parser.add_argument('file', nargs="+")
    args = parser.parse_args(args)
    for file in args.file:
        lib.untag(file, args.tag)


@public
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


@public
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


@public
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


@public
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


@public
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


@public
def fix(lib, *args):
    """
    Fixes symlinks after the library has been moved.  If it hasn't been moved,
    does nothing.
    """
    logger.debug('fix(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian fix", add_help=False)
    args = parser.parse_args(args)
    lib.fix()


@public
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


@public
def mount(lib, *args):
    """
    Mount FUSE according to config files.
    """
    logger.debug('mount(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian mount", add_help=False)
    parser.add_argument('path')
    args = parser.parse_args(args)
    lib.mount(args.path)
    logger.debug('exit')
