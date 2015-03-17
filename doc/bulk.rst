Bulk operations
===============

.. module:: dantalian.bulk

Bulk operations are defined in :mod:`dantalian.bulk`.  These functions operate
on multiple file or entire directory trees.

.. function:: clean_symlinks(dirpath)

   Remove all broken symlinks in the given directory tree.

.. function:: rename_all(rootpath, top, path, name)

   Rename all links to the given file or directory.

   Attempt to rename all links to the target under the rootpath to the given
   name, finding a name as necessary.  If there are multiple links in a
   directory, the first will be renamed and the rest unlinked.

   :param str rootpath: Base path for tagname conversions.
   :param str top: Path of search directory.
   :param str path: Path of target to rename.
   :param str name: New filename.

.. function:: unlink_all(rootpath, top, path)

   Unlink all links to the target file or directory.  This can be used to
   completely remove a file instead of needing to manually unlink each of its
   links.

   :param str rootpath: Base path for tagname conversions.
   :param str top: Path of search directory.
   :param str path: Path of target.

Import and export
-----------------

.. function:: import_tags(rootpath, path_tag_map)

   Import a path tag map, such as one returned from :func:`export_tags`.

   Tags each path with the given tagnames, thus "importing" tag data.

   :param str rootpath: Base path for tag conversions.
   :param dict path_tag_map: Mapping of paths to lists of tagnames.

.. function:: export_tags(rootpath, top, full=False)

   Export a path tag map.

   Each file will only have one key path mapping to a list of tags.  If `full`
   is ``True``, each file will have one key path for each one of that file's
   links, all mapping to the same list of tags.

   Example without `full`::

     {'foo/file': ['//foo', '//bar']}
     
   With ``full``::

     {'foo/file': ['//foo', '//bar'], 
      'bar/file': ['//foo', '//bar']}

   :param str rootpath: Base path for tag conversions.
   :param str top: Top of directory tree to export.
   :param bool full: Whether to include all paths to a file.  Defaults to False.
   :returns: Mapping of paths to lists of tagnames.
   :rtype: dict
