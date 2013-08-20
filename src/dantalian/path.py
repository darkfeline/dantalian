import os
import logging
import re
import subprocess
from itertools import count

from dantalian.errors import DependencyError

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
    """Get absolute path from tag

    Parameters
    ----------
    tag : str
        Tag.
    root : str
        Absolute path to library root directory.

    """
    assert istag(tag)
    return os.path.join(root, tag.lstrip('//'))


@_public
def tagfrompath(path, root):
    """Get tag from path

    Parameters
    ----------
    path : str
        Path.
    root : str
        Absolute path to library root directory.

    """
    return '//' + os.path.relpath(path, root)


@_public
def listdir(path):
    """Return full paths of files in `path`.

    Returns
    -------
    list

    """
    return [os.path.join(path, f) for f in os.listdir(path)]


@_public
def resolve_name(dir, name):
    files = os.listdir(dir)
    base, ext = os.path.splitext(name)
    if name not in files:
        return name
    i = count(1)
    while True:
        x = '.'.join(x for x in (base, str(next(i)), ext.lstrip('.')) if x)
        if x not in files:
            return x


@_public
def fuse_resolve(name, path):
    file, ext = os.path.splitext(name)
    inode = os.lstat(path).st_ino
    return '.'.join([file, inode, ext.lstrip('.')])


@_public
def fuse_resolve_path(path):
    return fuse_resolve(os.path.basename(path), path)


@_public
def fixsymlinks(links, oldprefix, newprefix):
    """Fix symlinks

    Recursively replace symlinks `links` that match `oldprefix` with
    `newprefix`.  `links` is as returned from findsymlinks().

    Parameters
    ----------
    links : iterable
        Symlinks to fix
    oldprefix : str
        Old prefix to replace
    newprefix : str
        New prefix to use

    """
    oldprefix = re.compile(r"^" + re.escape(oldprefix))
    for set in links:
        try:
            f = set.pop(0)
        except IndexError:
            logger.warning("Empty set")
            continue
        newtarget = oldprefix.sub(newprefix, os.readlink(f), count=1)
        logger.debug("Unlinking %r", f)
        os.unlink(f)
        dir, name = os.path.dirname(f)
        while True:
            f = os.path.join(dir, resolve_name(dir, name))
            logger.debug("Symlinking %r to %r", f, newtarget)
            try:
                os.symlink(newtarget, f)
            except FileExistsError:
                continue
            else:
                break
        for file in set:
            logger.debug("Unlinking %r", file)
            os.unlink(file)
            dir = os.path.dirname(file)
            while True:
                dest = os.path.join(dir, resolve_name(dir, file))
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

    Relies on 'find' utility, for sheer simplicity and speed.  If it
    cannot be found, DependencyError is raised.

    Returns
    -------
    list
        Returns a list of lists of absolute paths.  Symlinks that are
        the same inode are grouped together.

    Raises
    ------
    DependencyError
        'find' was not found.

    """
    try:
        output = subprocess.check_output(
            ['find', dir, '-type', 'l'])
    except FileNotFoundError:
        raise DependencyError("find could not be found; \
            probably findutils is not installed")
    if not output:
        return []
    output = output.decode().rstrip().split('\n')
    result = []
    for file in output:
        found = 0
        for stat, set in result:
            if os.path.samestat(stat, os.lstat(file)):
                set.append(file)
                found = 1
                break
        if not found:
            result.append((os.lstat(file), [file]))
    return [x[1] for x in result]
