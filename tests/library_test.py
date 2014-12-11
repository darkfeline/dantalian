"""
This module contains unit tests for dantalian.library
"""

from . import testlib
from dantalian import library
from dantalian.library import base

# pylint: disable=missing-docstring


class TestLibraryBaseParsing(testlib.ExtendedTestCase):

    def test_parse_and(self):
        tree = library.parse_query("AND A B C )")
        self.assertSameTree(tree, base.AndNode(
            [base.DirNode("A"),
             base.DirNode("B"),
             base.DirNode("C")]))

    def test_parse_or(self):
        tree = library.parse_query("OR A B C )")
        self.assertSameTree(tree, base.OrNode(
            [base.DirNode("A"),
             base.DirNode("B"),
             base.DirNode("C")]))

    def test_parse_minus(self):
        tree = library.parse_query("MINUS A B C )")
        self.assertSameTree(tree, base.MinusNode(
            [base.DirNode("A"),
             base.DirNode("B"),
             base.DirNode("C")]))

    def test_parse_and_escape(self):
        tree = library.parse_query(r"AND '\AND' '\\AND' '\\\AND' )")
        self.assertSameTree(tree, base.AndNode(
            [base.DirNode(r'AND'),
             base.DirNode(r'\AND'),
             base.DirNode(r'\\AND')]))

    def test_parse_paren_escape(self):
        tree = library.parse_query(r"AND A B \\) )")
        self.assertSameTree(tree, base.AndNode(
            [base.DirNode(r'A'),
             base.DirNode(r'B'),
             base.DirNode(r')')]))

    def test_parse_and_or(self):
        tree = library.parse_query("AND A B C OR spam eggs ) )")
        self.assertSameTree(tree, base.AndNode(
            [base.DirNode("A"),
             base.DirNode("B"),
             base.DirNode("C"),
             base.OrNode(
                 [base.DirNode('spam'),
                  base.DirNode('eggs')])
            ]))
