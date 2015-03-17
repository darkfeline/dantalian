Basic linking
=============

This section describes Dantalian's basic linking features.

.. module:: dantalian.base

Dantalian's fundamental linking functionality is contained in
:mod:`dantalian.base`.  The main functions defined in this module are
:func:`link`, :func:`unlink`, and :func:`rename`, which are analogous to
their counterparts in the standard :mod:`os` module, except that they have been
extended to work with directories (see :ref:`dir-linking`).
:mod:`dantalian.base` additionally includes helper functions to compensate for
the implementation of these extended features.

.. function:: link(rootpath, src, dst)

   Link `src` to `dst`.  See :ref:`dir-linking` for how directories are linked.

   :param str rootpath: Path for tagname conversions.
   :param str src: Source path.
   :param str dst: Destination path.

.. function:: unlink(rootpath, path)

   Unlink the given path.  See :ref:`dir-linking` for how directories are
   unlinked.

   If the directory does not have any extra links, :exc:`IsADirectoryError` is
   raised.

   If `path` is the actual directory and the directory dies have extra links,
   the directory is swapped out using :func:`swap_dir`

   :param str rootpath: Path for tagname conversions.
   :param str path: Target path.
   :raises IsADirectoryError: Target is a directory without any other links.

   .. note::

      This function does not work recursively for directories.  For example,
      unlinking a directory ``foo`` that contains a link ``bar`` to another
      directory will not properly update ``bar``'s ``.dtags`` file.

.. function:: rename(rootpath, src, dst)

   Renames the given link.  Implemented as and functionally equivalent to::

     link(rootpath, src, dst)
     unlink(rootpath, src)

   :param str rootpath: Path for tagname conversions.
   :param str src: Source path.
   :param str dst: Destination path.

   .. note::

      This will not overwrite files, unlike :func:`os.rename`.

   .. note::

      This function does not work recursively for directories.  For example,
      renaming a directory ``foo`` that contains a link ``bar`` to another
      directory will not properly update ``bar``'s ``.dtags`` file.

The following function is provided for convenience.

.. function:: list_links(top, path)

   Traverse the directory tree, finding all of the links to the target file.

   :param str top: Path of directory to begin search.
   :param str path: Path of target file.
   :return: Generator yielding paths.

   .. note::

      This function returns a generator that lazily traverses the file system.
      Any changes to the file system will affect the generator's execution.

.. _dir-linking:

Directory linking
-----------------

Directory linking is implemented in Dantalian using symlinks and a file named
:file:`.dtags` in each tagged directory.  Dantalian assumes that the status of
symlinks in the file system are consistent with the contents of the
:file:`.dtags` files, except for a number of administrative functions.

A directory is linked thus, given a target path `path` and a rootpath
`rootpath`: A symlink is created at `path`, whose target is the absolute path
to the directory.  A tagname is created given `path` and `rootpath`, which is
added to the file named :file:`.dtags` in the directory.

Similarly, a directory is unlinked thus, given a target path `path` and a
rootpath `rootpath`: The symlink at `path` is removed, and the tagname created
given `path` and `rootpath` is removed from the :file:`.dtags` file in the
directory.  Unlinking a directory that has no such extra links is invalid.

The following function is provided for convenience.

.. function:: swap_dir(rootpath, path)

   Swap a symlink with its target directory.  More specifically, given that an
   actual directory with path ``foo`` is also linked at ``bar``, calling this
   function on ``bar`` will move the actual directory to ``bar``, creating a
   symlink at ``foo``, and updating the :file:`.dtags` file appropriately.

   This is useful when the actual directory, not a symlink, is needed somewhere.

   :param str rootpath: Path for tagname conversions.
   :param str path: Target path.
   :raises ValueError: Target is not a symlink to a directory.

The following are administrative functions that do not necessarily assume that
symlink state is consistent with :file:`.dtags` state and are used to repair
and maintain such state consistency.

.. function:: save_dtags(rootpath, top, dirpath)

   Save the current state of symlinks to the target directory in its ``.dtags``
   file, overwriting its current ``.dtags`` state.  The file system search is
   done recursively from `top`.

   This is useful for "committing" file system changes to ``.dtags`` files.

   :param str rootpath: Path for tagname conversions.
   :param str top: Path of search directory.
   :param str dirpath: Path of target directory.

.. function:: load_dtags(rootpath, dirpath)

   Create symlinks according to the directory's ``.dtags`` file.

   This is useful in conjunction with :func:`unload_dtags` for moving directory
   trees around without worrying about symlink targets.

   :param str rootpath: Path for tagname conversions.
   :param str dirpath: Path of target directory.

.. function:: unload_dtags(rootpath, dirpath)

   Remove symlinks according to the directory's ``.dtags`` file.

   This is useful in conjunction with :func:`load_dtags` for moving directory
   trees around without worrying about symlink targets.

   :param str rootpath: Path for tagname conversions.
   :param str dirpath: Path of target directory.

.. _tagnames:

Tagnames
--------

.. module:: dantalian.tagnames

Tagnames are a special type of pathnames used by Dantalian internally.  They
begin with at least two forward slashes.  After stripping all forward slashes
from the beginning of a tagname, the remaining string is considered a pathname
relative to a given rootpath.

Tagnames are used in :file:`.dtags` files for tagging directories, as well as
as shortcuts for the standalone script.

:mod:`dantalian.tagnames` contains functions for working with tagnames.  Even
though the transformation between tagnames and pathnames is relatively simple,
use the functions provided in this module to ensure consistent behavior.

.. function:: is_tag(name)

   Check if the given path is a tagname.

   :param str name: Pathname.
   :returns: Whether the given path is a tagname.
   :rtype: bool

.. function:: path2tag(rootpath, pathname)

   Convert a pathname to a tagname.

   This function will also normalize the given path before converting it to a
   tagname.

   :param str rootpath: Path for tagname conversions.
   :param str pathname: Pathname.
   :returns: Tagname.
   :rtype: str

.. function:: tag2path(rootpath, tagname)

   Convert a tagname to a pathname.

   This function doesn't normalize the resulting path.

   :param str rootpath: Path for tagname conversions.
   :param str tagname: Tagname.
   :returns: Pathname.
   :rtype: str

.. function:: path(rootpath, name)

   Return the given tagname or pathname as a pathname.

   In other words, convert the given name to a pathname if it is tagname.

.. function:: tag(rootpath, name)

   Return the given tagname or pathname as a tagname.

   In other words, convert the given name to a tagname if it is not a tagname.

.. _libraries:

Libraries
---------

.. module:: dantalian.library

Libraries are special directories Dantalian uses to make file management more
convenient.  A library is a directory that contains a subdirectory named
:file:`.dantalian`.

Currently, libraries exist to provide a clear `rootpath` to be used by
Dantalian's various linking function.  The standalone Dantalian script will
search parent directories for a library to use as a root for many commands so
that you do not have to explicitly provide one yourself.  Other scripts using
Dantalian as a library can also take advantage of libraries as anchor points.

Currently, :file:`.dantalian` is not used for anything beyond identifying
libraries, but in the future, it may be used for caching search results or
other caching or data storage purposes.

:mod:`dantalian.library` contains functions for working with libraries.

.. function:: is_library(dirpath)

   Return whether the given directory is a library.

   :param str dirpath: Path to directory.
   :returns: Whether directory is library.
   :rtype: bool

.. function:: find_library(dirpath='.')

   Find a library.  Starting from the given path, search up the file system.
   Return the path of the first library found, including the initially given
   path.  Returns ``None`` if no library is found.

   :param str dirpath: Path to search.
   :returns: Path or None
   :rtype: str or None

.. function:: init_library(dirpath)

   Initialize a library.  Does nothing if the given directory is already a
   library.

   :param str dirpath: Path to directory.

.. function:: get_resource(dirpath, resource_path)

   Get the path of a resource stored in the library.

   May be used in the future for library data or cache storage.
