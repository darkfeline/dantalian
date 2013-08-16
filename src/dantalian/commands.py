"""
All the functions in this module are hooked in the dantalian script as
commands.  See the manpage for usage.

Commands should be decorated appropriately.  All of them should have
``@_public``.  ``@_global`` is for global commands, which take no
additional parameters.  ``@_library`` commands get a Library instance.
``@_sock`` commands get a socket object.

"""

import argparse
import logging
import shlex
import os

from dantalian import library

__all__ = ['t_global', 't_library', 't_sock']
t_global = []
t_library = []
t_sock = []
logger = logging.getLogger(__name__)


def _public(f):
    __all__.append(f.__name__)
    return f


def _global(f):
    t_global.append(f.__name__)
    return f


def _library(f):
    t_library.append(f.__name__)
    return f


def _sock(f):
    t_sock.append(f.__name__)
    return f


@_public
@_library
def tag(lib: 'BaseLibrary', *args):
    """Tag file.

    Tag `file` with `tag` (Hard links `file` under `tag` directory with
    the same name).  If `file` is already tagged, does nothing.  If
    `file` is a directory, you'll need to convert it first.

    Parameters
    ----------
    lib : BaseLibrary
        Library instance.
    *args
        Arguments passed on to ArgumentParser (See code).

    """
    logger.debug('tag(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian tag", add_help=False)
    parser.add_argument('-s', action='store_true')
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


@_public
@_library
def untag(lib: 'BaseLibrary', *args):
    """Untag file.

    Remove tag `tag` from `file` (Removes the hard link to `file` under
    `tag` directory).  If `file` isn't tagged, does nothing.

    Parameters
    ----------
    lib : BaseLibrary
        Library instance.
    *args
        Arguments passed on to ArgumentParser (See code).

    """
    logger.debug('untag(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian untag", add_help=False)
    parser.add_argument('-s', action='store_true')
    parser.add_argument('tag')
    parser.add_argument('file', nargs="+")
    args = parser.parse_args(args)
    for file in args.file:
        if not args.s:
            lib.untag(file, args.tag)
        else:
            lib.untag(args.tag, file)


@_public
@_library
def tags(lib: 'BaseLibrary', *args):
    """List tags.

    List all the tags of `file` (Lists the directories that have hard
    links to `file`).

    Parameters
    ----------
    lib : BaseLibrary
        Library instance.
    *args
        Arguments passed on to ArgumentParser (See code).

    """
    logger.debug('tags(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian tags", add_help=False)
    parser.add_argument('file')
    args = parser.parse_args(args)
    r = lib.listtags(args.file)
    for tag in r:
        print(tag)


@_public
@_library
def find(lib: 'BaseLibrary', *args):
    """Find files with tags.

    Intersect tag search.  Lists all files that have all of the given
    tags.  Lists files by the path to the hard link under the first tag
    given.

    Parameters
    ----------
    lib : BaseLibrary
        Library instance.
    *args
        Arguments passed on to ArgumentParser (See code).

    """
    logger.debug('find(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian find", add_help=False)
    parser.add_argument('tags', nargs='+')
    args = parser.parse_args(args)
    r = lib.find(args.tags)
    for file in r:
        print(file)


@_public
@_library
def rm(lib: 'BaseLibrary', *args):
    """Remove file.

    Remove the files given (Removes all hard links to the files under
    the root directory).

    Parameters
    ----------
    lib : BaseLibrary
        Library instance.
    *args
        Arguments passed on to ArgumentParser (See code).

    """
    logger.debug('rm(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian rm", add_help=False)
    parser.add_argument('files', nargs='+')
    args = parser.parse_args(args)
    for file in args.files:
        lib.rm(file)


@_public
@_library
def rename(lib: 'BaseLibrary', *args):
    """Rename file.

    Rename all hard links of `file` to `new`.  New names are subject to
    name collision resolution.

    Parameters
    ----------
    lib : BaseLibrary
        Library instance.
    *args
        Arguments passed on to ArgumentParser (See code).

    """
    logger.debug('rename(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian rename", add_help=False)
    parser.add_argument('file')
    parser.add_argument('new')
    args = parser.parse_args(args)
    lib.rename(args.file, args.new)


@_public
@_library
def convert(lib: 'BaseLibrary', *args):
    """Convert directory.

    Convert directories so they can be tagged.  (Move directories to
    special location '.dantalian/dirs' and replace the original with a
    symlink pointing to the absolute path.)

    Parameters
    ----------
    lib : BaseLibrary
        Library instance.
    *args
        Arguments passed on to ArgumentParser (See code).

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


@_public
@_library
def fix(lib: 'BaseLibrary', *args):
    """Fix symlinks.

    Fix symlinks after the library has been moved.  If it hasn't been
    moved, do nothing.

    Parameters
    ----------
    lib : BaseLibrary
        Library instance.
    *args
        Arguments passed on to ArgumentParser (See code).

    """
    logger.debug('fix(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian fix", add_help=False)
    args = parser.parse_args(args)
    lib.fix()


@_public
@_library
def clean(lib: 'BaseLibrary', *args):
    """Clean converted directories.

    Internally tracked converted directories which no longer have
    referent symlink under the root directory are removed.

    Parameters
    ----------
    lib : BaseLibrary
        Library instance.
    *args
        Arguments passed on to ArgumentParser (See code).

    """
    logger.debug('clean(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian clean", add_help=False)
    args = parser.parse_args(args)
    lib.cleandirs()


@_public
@_global
def init(*args):
    """Create and initialize a library.

    Create a library in `dir`.  If `dir` is omitted, create a library in
    the current directory.  If a library already exists, it is not
    affected.

    Parameters
    ----------
    *args
        Arguments passed on to ArgumentParser (See code).

    """
    logger.debug('init(%r)', args)
    parser = argparse.ArgumentParser(prog="dantalian init", add_help=False)
    parser.add_argument('root', nargs="?", default=os.getcwd())
    args = parser.parse_args(args)
    library.init_library(args.root)


@_public
@_library
def mount(lib: 'BaseLibrary', *args):
    """Mount FUSE at the given path.

    The library must not be a FUSE-mounted virtual library.

    Parameters
    ----------
    lib : BaseLibrary
        Library instance.
    *args
        Arguments passed on to ArgumentParser (See code).

    """
    logger.debug('mount(%r, %r)', lib, args)
    parser = argparse.ArgumentParser(prog="dantalian mount", add_help=False)
    parser.add_argument('path')
    args = parser.parse_args(args)
    lib.mount(args.path, lib.maketree())
    logger.debug('exit')


@_public
@_sock
def mknode(sock: 'socket', *args):
    """Make a node in FUSE.

    Parameters
    ----------
    sock : socket
        sock (socket): A socket object for a library's FUSE socket.
    args*
        Arguments passed on to ArgumentParser (See code).

    """
    logger.debug('mknode(%r, %r)', sock, args)
    parser = argparse.ArgumentParser(prog="dantalian mknode", add_help=False)
    parser.add_argument('path')
    parser.add_argument('tags', nargs="+")
    args = parser.parse_args(args)
    sock.send(" ".join(
        ['mknode'] + [shlex.quote('/' + args.path)] +
        [shlex.quote(x) for x in args.tags]
    ).encode())
