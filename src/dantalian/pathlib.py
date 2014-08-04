import os
import logging
import re
import subprocess
from itertools import count
from collections import defaultdict

from .errors import DependencyError

logger = logging.getLogger(__name__)
__all__ = []


def _public(x):
    __all__.append(x.__name__)
    return x


@_public
def istag(tag):
    """Check if tag is a tag qualifier.

    A tag qualifier is a pathname that begins with at least two forward
    slashes.  It is a pathname relative to a given libraray root
    directory as opposed to the current working directory.

    """
    return tag.startswith('//')


@_public
def pathfromtag(tag, root):
    """Get the pathname of a tag qualifier.

    If root is relative, the returned pathname will be relative, and if
    root is absolute, the returned pathname will be absolute.

    Args:
        tag: Tag qualifier.
        root: Pathname of library root directory.

    Raises:
        ValueError: Invalid tag qualifier.

    Returns:
        Pathname.

    """
    if not istag(tag):
        raise ValueError('{} is not a tag'.format(tag))
    return os.path.join(root, tag.lstrip('/'))


@_public
def tagfrompath(path, root):
    """Get the tag qualifier corresponding to the given pathname.

    Args:
        path: Pathname.
        root: Pathname of library root directory.

    Returns:
        Tag qualifier.

    """
    return '//' + os.path.relpath(path, root)


@_public
def listdir(path):
    """Return full pathnames of a directory.

    Unlike os.listdir(), which only returns the names of the directory's
    contents, this function joins the names with the given directory's
    path.  Consequently, the values returned by this function can be
    used to reference the directory's contents directly.

    Returns:
        A list of pathnames.

    """
    return [os.path.join(path, f) for f in os.listdir(path)]


# TODO Rename resolve_filename()
@_public
def resolve_name(directory, name):
    """Find a free filename in the given directory.

    Given a desired filename, this function attempts to find a filename
    that is not currently being used in the given directory, adding an
    incrementing index to the filename as necessary.

    Note that the returned filename might not work, as a file with that
    name might be created between being checked in the function and when
    it is actually used.  Program accordingly.

    Args:
        name: Desired filename.
        directory: Pathname of directory to look in.

    Returns:
        Filename.

    """
    files = os.listdir(directory)
    if name not in files:
        return name
    base, ext = os.path.splitext(name)
    i = count(1)
    while True:
        x = ''.join((base, '.', str(next(i)), ext))
        if x not in files:
            return x


# TODO Rename resolve_pathname()
@_public
def resolve_name_path(pathname):
    """Find a free pathname for a file.

    This function is a convenience wrapper around resolve_name().

    Args:
        pathname: Pathname of file.

    Returns:
        Pathname.

    """
    dirname, filename = os.path.split(pathname)
    return os.path.join(dirname, resolve_name(dirname, filename))


@_public
def fuse_resolve(name, path):
    """Generate a unique filename for a file using its inode number.

    This function doesn't follow symbolic links.

    Args:
        name: Desired filename.
        path: Pathname of file.

    Returns:
        Filename.

    """
    filename, ext = os.path.splitext(name)
    inode = os.lstat(path).st_ino
    new_pathname = ''.join((filename, '.', inode, ext))
    return new_pathname


@_public
def fuse_resolve_path(path):
    """Generate a unique filename for a file using its inode number.

    This function is a convenience wrapper around fuse_resolve().

    Args:
        pathname: Pathname of file.

    Returns:
        Filename.

    """
    return fuse_resolve(os.path.basename(path), path)


@_public
def fixsymlinks(links, oldprefix, newprefix):
    """Fixes symbolic links by replacing part of their target paths.

    This function replaces symbolic links whose target matches oldprefix
    with new symbolic links whose targets have oldprefix replaced with
    newprefix.  Hard link relationships are remade afterward.

    links is as returned from findsymlinks().

    Args:
        links: Symbolic links to fix.
        oldprefix: Old prefix to replace.
        newprefix: New prefix to use.

    """
    oldprefix = re.compile(r"^" + re.escape(oldprefix))
    for set in links:
        # Create first symlink
        try:
            f = set.pop(0)
        except IndexError:
            logger.warning("Empty set")
            continue
        newtarget = oldprefix.sub(newprefix, os.readlink(f))
        logger.debug("Unlinking %r", f)
        os.unlink(f)
        while True:
            f = resolve_name_path(f)
            logger.debug("Symlinking %r to %r", f, newtarget)
            try:
                os.symlink(newtarget, f)
            except FileExistsError:
                continue
            else:
                break
        # Link rest of them to new symlink
        for file in set:
            logger.debug("Unlinking %r", file)
            os.unlink(file)
            while True:
                dest = resolve_name_path(file)
                logger.debug('Linking %r to %r', dest, f)
                try:
                    os.link(f, dest)
                except FileExistsError:
                    continue
                else:
                    break


@_public
def findsymlinks(dirname):
    """Find symlinks.

    Relies on find utility, for sheer simplicity and speed.  If it
    cannot be found, DependencyError is raised.

    Returns:
        A list of lists of absolute pathnames.  Symbolic links that
        point to the same inode are grouped together.

    Raises:
        DependencyError: find was not found.

    """
    try:
        output = subprocess.check_output(
            ['find', dirname, '-type', 'l', '-print0'])
    except FileNotFoundError:
        raise DependencyError("find could not be found; \
            probably findutils is not installed")
    if not output:
        return []
    output = [x.decode() for x in output.split(b'\0') if x]
    symlinks = defaultdict(list)
    for file in output:
        stat = os.lstat(file)
        symlinks[(stat.st_ino, stat.st_dev)].append(file)
    return [x for x in symlinks.values()]
