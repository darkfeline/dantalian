"""
All the functions in this module are scripts to be called from the command
line.

Usage: hfs `command` `args` ...

"""

import argparse
import logging
import os
import sys

from hitagifs.fs import HitagiFS

logger = logging.getLogger(__name__)


def public(f):
    all = sys.modules[f.__module__].__dict__.setdefault('__all__', [])
    if f.__name__ not in all:
        all.append(f.__name__)
    return f


@public
def tag(fs, *args):
    """
    Usage: hfs tag `tag` `file1` [`file2`, [...]]

    Tags `file` with `tag` (Hard links `file` under `tag` directory with the
    same name).  If `file` is already tagged, does nothing.  If `file` is a
    directory, you'll need to convert it first.

    """
    logger.debug('tag(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs tag", add_help=False)
    parser.add_argument('tag')
    parser.add_argument('file', nargs="+")
    args = parser.parse_args(args)
    for file in args.file:
        try:
            fs.tag(file, args.tag)
        except IsADirectoryError:
            logger.warn('skipped %r; convert it first', file)


@public
def untag(fs, *args):
    """
    Usage: hfs untag `tag` `file1` [`file2`, [...]]

    Removes tag `tag` from `file` (Removes the hard link to `file` under `tag`
    directory).  If `file` isn't tagged, does nothing.

    """
    logger.debug('untag(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs utag", add_help=False)
    parser.add_argument('tag')
    parser.add_argument('file', nargs="+")
    args = parser.parse_args(args)
    for file in args.file:
        fs.untag(file, args.tag)


@public
def tags(fs, *args):
    """
    Usage: hfs tags `file`

    Lists all the tags of `file` (Lists the directories that have hard links to
    `file`).

    """
    logger.debug('tags(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs tags", add_help=False)
    parser.add_argument('file')
    args = parser.parse_args(args)
    r = fs.listtags(args.file)
    for tag in r:
        print(tag)


@public
def find(fs, *args):
    """
    Usage: hfs find `tag1` [`tag2` [...]]

    Intersect tag search.  Lists all files that have all of the given tags.
    Lists files by the path to the hard link under the first tag given.

    """
    logger.debug('find(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs find", add_help=False)
    parser.add_argument('tags', nargs='+')
    args = parser.parse_args(args)
    r = fs.find(args.tags)
    for file in r:
        print(file)


@public
def rm(fs, *args):
    """
    Usage: hfs rm `file1` [`file2` [...]]

    Removes the files given (Removes all hard links to the files under the root
    directory).

    """
    logger.debug('rm(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs rm", add_help=False)
    parser.add_argument('files', nargs='+')
    args = parser.parse_args(args)
    for file in args.files:
        fs.rm(file)


@public
def rename(fs, *args):
    """
    Usage: hfs rename `file` `new`

    Renames all hard links of `file` to `new`.

    """
    logger.debug('rename(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs rename", add_help=False)
    parser.add_argument('file')
    parser.add_argument('new')
    args = parser.parse_args(args)
    fs.rename(args.source, args.dest)


@public
def convert(fs, *args):
    """
    Usage: hfs convert `dir1` [`dir2` [...]]

    Converts directories so they can be tagged.  (Moves directories to special
    location '.hitagifs/dirs' and replaces the original with a symlink pointing
    to the absolute path)

    """
    logger.debug('convert(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs convert", add_help=False)
    parser.add_argument('dir', nargs="+")
    args = parser.parse_args(args)
    for dir in args.dir:
        try:
            fs.convert(dir)
        except NotADirectoryError:
            logger.warn('%r is not a directory; skipping', dir)
        except FileExistsError:
            logger.warn('Name conflict %r; skipping', dir)


@public
def fix(fs, *args):
    """
    Usage: hfs fix

    Fixes symlinks after the hitagiFS has been moved.  If it hasn't been moved,
    does nothing.

    """
    logger.debug('fix(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs fix", add_help=False)
    args = parser.parse_args(args)
    fs.fix()


@public
def init(*args):
    """
    Usage: hfs init [`dir`]

    Creates a hitagifs in `dir`.  If `dir` is omitted, creates a hitagifs in
    the current directory.

    """
    logger.debug('init(%r)', args)
    parser = argparse.ArgumentParser(prog="hfs init", add_help=False)
    parser.add_argument('root', nargs="?", default=os.getcwd())
    args = parser.parse_args(args)
    HitagiFS.init(args.root)
