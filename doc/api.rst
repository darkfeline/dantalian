API Reference
=============

This reference is for developers looking to extend hitagiFS.  hitagiFS is
written to be mod-friendly, but ultimately, the documentation in the source
code and the source code itself is final.  API documented elsewhere in this
documentation will not be reprinted here.

.. automodule:: hitagifs.fs

   .. autoclass:: HitagiFS
      :members:

      All interactions with hitagiFS and its abstraction model goes through
      :class:`HitagiFS`.

   .. autoclass:: FSError
   .. autoclass:: DependencyError

.. automodule:: hitagifs.tree

   .. autoclass:: FSNode
      :members:

   .. autoclass:: TagNode
      :members:
