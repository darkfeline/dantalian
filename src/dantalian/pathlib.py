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
    return tag.startswith('//')


@_public
def pathfromtag(tag, root):
    """Get absolute path from tag.

    Args:
        tag: Tag.
        root: Absolute path to library root directory.

    Raises:
        ValueError: Invalid tag.

    Returns:
        Absolute path.

    """
    if not istag(tag):
        raise ValueError('{} is not a tag'.format(tag))
    return os.path.abspath(os.path.join(root, tag[2:]))


@_public
def tagfrompath(path, root):
    """Get tag from path.

    Args:
        path: Path.
        root: Absolute path to library root directory.

    Returns:
        Tag.

    """
    return '//' + os.path.relpath(path, root)


@_public
def listdir(path):
    """Return full paths of files in `path`.

    Returns:
        list

    """
    return [os.path.join(path, f) for f in os.listdir(path)]


@_public
def resolve_name(dir, name):
    """Find a free name for the file, using an incrementing number.

    Args:
        name: Name of file
        dir: Directory to look in.

    Returns:
        Filename.

    """
    files = os.listdir(dir)
    if name not in files:
        return name
    base, ext = os.path.splitext(name)
    i = count(1)
    while True:
        x = '.'.join(x for x in (base, str(next(i)), ext[1:]) if x)
        if x not in files:
            return x


@_public
def resolve_name_path(path):
    """Find a free name for the file, using an incrementing number.

    Args:
        path: Path to file.

    Returns:
        Absolute path.

    """
    dir, name = os.path.split(path)
    return os.path.join(dir, resolve_name(dir, name))


@_public
def fuse_resolve(name, path):
    """Find a unique name for the file, using the file's inode number.

    Args:
        name: Name of file
        path: Path to file.

    Returns:
        Filename.

    """
    file, ext = os.path.splitext(name)
    inode = os.lstat(path).st_ino
    return '.'.join([file, inode, ext[1:]])


@_public
def fuse_resolve_path(path):
    """Find a unique name for the file, using the file's inode number.

    Args:
        path: Path to file.

    Returns:
        Filename.

    """
    return fuse_resolve(os.path.basename(path), path)


@_public
def fixsymlinks(links, oldprefix, newprefix):
    """Fix symlinks.

    Recursively replace symlinks that match oldprefix with
    newprefix.  links is as returned from findsymlinks().

    Args:
        links: Symlinks to fix.
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
def findsymlinks(dir):
    """Find symlinks

    Relies on find utility, for sheer simplicity and speed.  If it
    cannot be found, DependencyError is raised.

    Returns:
        List of lists of absolute paths.  Symlinks that have
        the same inode are grouped together.

    Raises:
        DependencyError: find was not found.

    """
    try:
        output = subprocess.check_output(
            ['find', dir, '-type', 'l', '-print0'])
    except FileNotFoundError:
        raise DependencyError("find could not be found; \
            probably findutils is not installed")
    if not output:
        return []
    output = [x.decode() for x in output.split(0)]
    symlinks = defaultdict(list)
    for file in output:
        stat = os.lstat(file)
        symlinks[(stat.st_ino, stat.st_dev)].append(file)
    return [x for x in symlinks.values()]
