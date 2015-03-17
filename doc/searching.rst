Searching
=========

.. module:: dantalian.findlib

The :mod:`dantalian.findlib` module implements tag queries.  See :ref:`tagging`
for more information about tags.

Queries are represented as a tree of :class:`SearchNodes`.

Example usage::

  from dantalian import findlib

  # Find files which are tagged foo and bar
  paths = findlib.search(findlib.parse_query('AND foo bar END'))

.. function:: search(search_node)

   Return a list of result paths for a given search query.

.. function:: parse_query(rootpath, query)

   Parse a query string into a query node tree.

   Parent node syntax::

     NODE foo [bar...] END

   where NODE is AND, OR, or MINUS

   Tokens beginning with a backslash are used directly in :class:`DirNode`s.
   Everything else parses to a :class:`DirNode`.

   Tagnames are converted to paths using the given `rootpath`.

   Query strings look like::

     'AND foo bar OR spam eggs END AND \AND \OR \END \\\END END END'

   which parses to::

     AndNode([
        DirNode('foo'),
        DirNode('bar'),
        OrNode([
            DirNode('spam'),
            DirNode('eggs'),
        ]),
        AndNode([
            DirNode('AND'),
            DirNode('OR'),
            DirNode('END'),
            DirNode('\\END'),
        ]),
     ])

Query nodes
-----------

Query nodes are used to represent a search query.  Query node trees can be
built manually using the node classes or by using :func:`parse_query`

.. class:: SearchNode

   An abstract interface for all query nodes.

   .. method:: get_results(self)

      Abstract method.  Returns the results of query represented by the current
      node.

      :returns: A dictionary mapping inode objects to paths.

.. class:: GroupNode(children)

    Abstract class for query nodes that have a list of child nodes,
    i.e. non-leaf nodes.

    :param list children: List of children nodes.

.. class:: AndNode(children)

   Query node that merges the results of its children nodes by set intersection.

   :param list children: List of children nodes.

.. class:: OrNode(children)

   Query node that merges the results of its children nodes by set union.

   :param list children: List of children nodes.

.. class:: MinusNode(children)

   Query node that merges the results of its children nodes by set difference:
   the results of its first child minus the results of the rest of its
   children.

   :param list children: List of children nodes.
   
.. class:: DirNode(dirpath)

   Query node that returns a directory's contents as results.  These are the
   leaf nodes in a query search tree.
