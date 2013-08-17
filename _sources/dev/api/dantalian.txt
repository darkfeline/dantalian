dantalian Package
=================

:mod:`commands` Module
----------------------

.. automodule:: dantalian.commands
   :members:
   :undoc-members:
   :show-inheritance:

   This module enables external Python applications to execute dantalian
   commands directly without having to use :mod:`subprocess` or going
   through the command line script.

:mod:`errors` Module
--------------------

.. automodule:: dantalian.errors
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`library` Module
---------------------

.. automodule:: dantalian.library

   .. autofunction:: init_library
   .. autofunction:: open_library
   .. autoclass:: BaseLibrary
   .. autoclass:: BaseFSLibrary
      :show-inheritance:

   .. autoclass:: Library
      :show-inheritance:

      Libraries should not be instantiated directly; use
      :func:`open_library` instead.

      The Library class has the following static and class methods which
      return path strings to dantalian libraries' special directories.
      All of them are LRU cached.

      .. staticmethod:: rootdir(root)

         The main dantalian special directory: ``.dantalian``.

      .. staticmethod:: fuserootdir(root)

         The main dantalian special directory, mirrored for FUSE-mounted
         libraries: ``.dantalian-fuse``.

      .. classmethod:: rootfile(root)

         A file which tracks the absolute path to the library root:
         ``.dantalian/root``.

      .. classmethod:: dirsdir(root)

         A directory containing all converted directories:
         ``.dantalian/dirs``.

      .. classmethod:: treefile(root)

         The file with the FUSE mount tree information:
         ``.dantalian/mount``.

      .. classmethod:: ctreefile(root)

         The file with the custom FUSE mount tree builder:
         ``.dantalian/mount_custom``.

      .. classmethod:: fusesock(root)

         The socket for a FUSE mounted library:
         ``.dantalian/fuse.sock``.

      Library instances have the following public methods:

      .. automethod:: tag
      .. automethod:: untag
      .. automethod:: listtags
      .. automethod:: convert
      .. automethod:: cleandirs
      .. automethod:: find
      .. automethod:: rm
      .. automethod:: rename
      .. automethod:: fix
      .. automethod:: mount

   .. autoclass:: ProxyLibrary
      :show-inheritance:

   .. autoclass:: SocketOperations
      :members:
      :undoc-members:
      :show-inheritance:

   .. autoexception:: LibraryError
      :show-inheritance:

   .. autoexception:: TagError
      :show-inheritance:

:mod:`operations` Module
------------------------

.. automodule:: dantalian.operations
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`path` Module
------------------

.. automodule:: dantalian.path
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`tree` Module
------------------

.. automodule:: dantalian.tree
   :members:
   :undoc-members:
   :show-inheritance:

