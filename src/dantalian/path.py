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
def samefile(f1, f2):
    """If `f1` and `f2` refer to same inode.

    :rtype: :class:`bool`

    """
    return os.path.samestat(os.lstat(f1), os.lstat(f2))


@_public
def listdir(path):
    """Return full paths of files in `path`.

    :rtype: `iterator`

    """
    return iter(os.path.join(path, f) for f in os.listdir(path))


@_public
def resolve_name(dir, name):
    """Return an available filename"""
    files = os.listdir(dir)
    base, ext = os.path.splitext(name)
    if name not in files:
        return name
    i = count(1)
    while True:
        x = '.'.join((base, str(next(i)), ext.lstrip('.')))
        if x not in files:
            return x


@_public
def fixsymlinks(links, oldprefix, newprefix):
    """Fix symlinks

    Recursively replace symlinks `links` that match `oldprefix` with
    `newprefix`.  `links` is as returned from findsymlinks().
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

    Returns a list of lists.  Symlinks that are the same inode are
    grouped together.  Relies on 'find' utility, for sheer simplicity
    and speed.  If it cannot be found, DependencyError is raised.
    Output paths are absolute.
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
