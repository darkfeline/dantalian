"""
This module contains unit tests for dantalian.library
"""

import os

from . import testlib
from dantalian import library
from dantalian.library import baselib

# pylint: disable=missing-docstring


class TestLibraryBaseParsing(testlib.TestCase):

    _root = 'foobar'

    def test_parse_and(self):
        tree = library.parse_query(self._root, "AND A B C )")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode("A"),
             baselib.DirNode("B"),
             baselib.DirNode("C")]))

    def test_parse_or(self):
        tree = library.parse_query(self._root, "OR A B C )")
        self.assertSameQuery(tree, baselib.OrNode(
            [baselib.DirNode("A"),
             baselib.DirNode("B"),
             baselib.DirNode("C")]))

    def test_parse_minus(self):
        tree = library.parse_query(self._root, "MINUS A B C )")
        self.assertSameQuery(tree, baselib.MinusNode(
            [baselib.DirNode("A"),
             baselib.DirNode("B"),
             baselib.DirNode("C")]))

    def test_parse_and_escape(self):
        tree = library.parse_query(self._root,
                                   r"AND '\AND' '\\AND' '\\\AND' )")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode(r'AND'),
             baselib.DirNode(r'\AND'),
             baselib.DirNode(r'\\AND')]))

    def test_parse_paren_escape(self):
        tree = library.parse_query(self._root, r"AND A B \\) )")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode(r'A'),
             baselib.DirNode(r'B'),
             baselib.DirNode(r')')]))

    def test_parse_and_or(self):
        tree = library.parse_query(self._root, "AND A B C OR spam eggs ) )")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode("A"),
             baselib.DirNode("B"),
             baselib.DirNode("C"),
             baselib.OrNode(
                 [baselib.DirNode('spam'),
                  baselib.DirNode('eggs')])
            ]))

    def test_parse_tags(self):
        tree = library.parse_query(self._root, "AND A /B //C //D/E )")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode("A"),
             baselib.DirNode("/B"),
             baselib.DirNode(os.path.join(self._root, 'C')),
             baselib.DirNode(os.path.join(self._root, 'D/E')),
            ]))
