"""
This module contains unit tests for dantalian.library
"""

import os
from unittest import TestCase

from dantalian import library
from dantalian.library import baselib

# pylint: disable=missing-docstring


class QueryMixin(TestCase):

    """TestCase mixin with convenient assertions."""

    # pylint: disable=invalid-name

    def assertSameQuery(self, node1, node2):
        """Assert two query node trees are equal."""
        self.assertEqual(node1, node2)
        if isinstance(node1, baselib.GroupNode):
            for i in range(len(node1.children)):
                self.assertSameQuery(node1.children[i], node2.children[i])


class TestLibraryParsing(QueryMixin):

    root = 'foobar'

    def test_parse_and(self):
        tree = library.parse_query(self.root, "AND A B C )")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode("A"),
             baselib.DirNode("B"),
             baselib.DirNode("C")]))

    def test_parse_or(self):
        tree = library.parse_query(self.root, "OR A B C )")
        self.assertSameQuery(tree, baselib.OrNode(
            [baselib.DirNode("A"),
             baselib.DirNode("B"),
             baselib.DirNode("C")]))

    def test_parse_minus(self):
        tree = library.parse_query(self.root, "MINUS A B C )")
        self.assertSameQuery(tree, baselib.MinusNode(
            [baselib.DirNode("A"),
             baselib.DirNode("B"),
             baselib.DirNode("C")]))

    def test_parse_and_escape(self):
        tree = library.parse_query(self.root,
                                   r"AND '\AND' '\\AND' '\\\AND' )")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode(r'AND'),
             baselib.DirNode(r'\AND'),
             baselib.DirNode(r'\\AND')]))

    def test_parse_paren_escape(self):
        tree = library.parse_query(self.root, r"AND A B \\) )")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode(r'A'),
             baselib.DirNode(r'B'),
             baselib.DirNode(r')')]))

    def test_parse_and_or(self):
        tree = library.parse_query(self.root, "AND A B C OR spam eggs ) )")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode("A"),
             baselib.DirNode("B"),
             baselib.DirNode("C"),
             baselib.OrNode(
                 [baselib.DirNode('spam'),
                  baselib.DirNode('eggs')])
            ]))

    def test_parse_tags(self):
        tree = library.parse_query(self.root, "AND A /B //C //D/E )")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode("A"),
             baselib.DirNode("/B"),
             baselib.DirNode(os.path.join(self.root, 'C')),
             baselib.DirNode(os.path.join(self.root, 'D/E')),
            ]))
