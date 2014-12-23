"""
This module contains unit tests for dantalian.library
"""

import os

from . import testlib
from dantalian import library
from dantalian.library import base
from dantalian.library import dirlib

# pylint: disable=missing-docstring


class TestLibraryBaseParsing(testlib.ExtendedTestCase):

    _root = 'foobar'

    def test_parse_and(self):
        tree = library.parse_query(self._root, "AND A B C )")
        self.assertSameTree(tree, base.AndNode(
            [dirlib.DirNode("A"),
             dirlib.DirNode("B"),
             dirlib.DirNode("C")]))

    def test_parse_or(self):
        tree = library.parse_query(self._root, "OR A B C )")
        self.assertSameTree(tree, base.OrNode(
            [dirlib.DirNode("A"),
             dirlib.DirNode("B"),
             dirlib.DirNode("C")]))

    def test_parse_minus(self):
        tree = library.parse_query(self._root, "MINUS A B C )")
        self.assertSameTree(tree, base.MinusNode(
            [dirlib.DirNode("A"),
             dirlib.DirNode("B"),
             dirlib.DirNode("C")]))

    def test_parse_and_escape(self):
        tree = library.parse_query(self._root,
                                   r"AND '\AND' '\\AND' '\\\AND' )")
        self.assertSameTree(tree, base.AndNode(
            [dirlib.DirNode(r'AND'),
             dirlib.DirNode(r'\AND'),
             dirlib.DirNode(r'\\AND')]))

    def test_parse_paren_escape(self):
        tree = library.parse_query(self._root, r"AND A B \\) )")
        self.assertSameTree(tree, base.AndNode(
            [dirlib.DirNode(r'A'),
             dirlib.DirNode(r'B'),
             dirlib.DirNode(r')')]))

    def test_parse_and_or(self):
        tree = library.parse_query(self._root, "AND A B C OR spam eggs ) )")
        self.assertSameTree(tree, base.AndNode(
            [dirlib.DirNode("A"),
             dirlib.DirNode("B"),
             dirlib.DirNode("C"),
             base.OrNode(
                 [dirlib.DirNode('spam'),
                  dirlib.DirNode('eggs')])
            ]))

    def test_parse_tags(self):
        tree = library.parse_query(self._root, "AND A /B //C //D/E )")
        self.assertSameTree(tree, base.AndNode(
            [dirlib.DirNode("A"),
             dirlib.DirNode("/B"),
             dirlib.DirNode(os.path.join(self._root, 'C')),
             dirlib.DirNode(os.path.join(self._root, 'D/E')),
            ]))
