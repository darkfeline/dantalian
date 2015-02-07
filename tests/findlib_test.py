# Copyright (C) 2015  Allen Li
#
# This file is part of Dantalian.
#
# Dantalian is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dantalian is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dantalian.  If not, see <http://www.gnu.org/licenses/>.

"""
This module contains unit tests for dantalian.findlib
"""

import os
import posixpath
from unittest import TestCase

from dantalian import findlib

from . import testlib

# pylint: disable=missing-docstring


class QueryMixin(TestCase):

    """TestCase mixin with convenient assertions."""

    # pylint: disable=invalid-name
    # pylint: disable=too-few-public-methods

    def assertSameQuery(self, node1, node2):
        """Assert two query node trees are equal."""
        self.assertEqual(node1, node2)
        if isinstance(node1, findlib.GroupNode):
            for i in range(len(node1.children)):
                self.assertSameQuery(node1.children[i], node2.children[i])


class TestLibraryParsing(QueryMixin):

    root = 'foobar'

    def test_parse_and(self):
        tree = findlib.parse_query(self.root, "AND A B C END")
        self.assertSameQuery(tree, findlib.AndNode(
            [findlib.DirNode("A"),
             findlib.DirNode("B"),
             findlib.DirNode("C")]))

    def test_parse_or(self):
        tree = findlib.parse_query(self.root, "OR A B C END")
        self.assertSameQuery(tree, findlib.OrNode(
            [findlib.DirNode("A"),
             findlib.DirNode("B"),
             findlib.DirNode("C")]))

    def test_parse_minus(self):
        tree = findlib.parse_query(self.root, "MINUS A B C END")
        self.assertSameQuery(tree, findlib.MinusNode(
            [findlib.DirNode("A"),
             findlib.DirNode("B"),
             findlib.DirNode("C")]))

    def test_parse_and_escape(self):
        tree = findlib.parse_query(self.root,
                                     r"AND '\AND' '\\AND' '\\\AND' END")
        self.assertSameQuery(tree, findlib.AndNode(
            [findlib.DirNode(r'AND'),
             findlib.DirNode(r'\AND'),
             findlib.DirNode(r'\\AND')]))

    def test_parse_end_escape(self):
        tree = findlib.parse_query(self.root, r"AND A B \\END END")
        self.assertSameQuery(tree, findlib.AndNode(
            [findlib.DirNode(r'A'),
             findlib.DirNode(r'B'),
             findlib.DirNode(r'END')]))

    def test_parse_and_or(self):
        tree = findlib.parse_query(self.root, "AND A B C OR spam eggs END END")
        self.assertSameQuery(tree, findlib.AndNode(
            [findlib.DirNode("A"),
             findlib.DirNode("B"),
             findlib.DirNode("C"),
             findlib.OrNode(
                 [findlib.DirNode('spam'),
                  findlib.DirNode('eggs')])
            ]))

    def test_parse_tags(self):
        tree = findlib.parse_query(self.root, "AND A /B //C //D/E END")
        self.assertSameQuery(tree, findlib.AndNode(
            [findlib.DirNode("A"),
             findlib.DirNode("/B"),
             findlib.DirNode(posixpath.join(self.root, 'C')),
             findlib.DirNode(posixpath.join(self.root, 'D/E')),
            ]))


class TestSearch(testlib.FSMixin):

    def setUp(self):
        super().setUp()
        os.makedirs('A')
        os.makedirs('B')
        os.makedirs('C')
        os.mknod('A/a')
        os.mknod('A/b')
        os.mknod('A/c')
        os.mknod('C/d')
        os.link('A/b', 'B/b')
        os.link('A/c', 'B/c')
        os.link('A/c', 'C/c')

    def test_and(self):
        results = findlib.search(
            findlib.AndNode(
                [findlib.DirNode('A'),
                 findlib.DirNode('B'),
                 findlib.DirNode('C')]
            )
        )
        self.assertListEqual(
            results,
            ['A/c'],
        )

    def test_or(self):
        results = findlib.search(
            findlib.OrNode(
                [findlib.DirNode('A'),
                 findlib.DirNode('B'),
                 findlib.DirNode('C')]
            )
        )
        self.assertListEqual(
            sorted(results),
            sorted(['A/a', 'A/b', 'A/c', 'C/d']),
        )

    def test_minus(self):
        results = findlib.search(
            findlib.MinusNode(
                [findlib.DirNode('A'),
                 findlib.DirNode('B'),
                 findlib.DirNode('C')]
            )
        )
        self.assertListEqual(
            results,
            ['A/a']
        )

    def test_dir(self):
        results = findlib.search(
            findlib.DirNode('A')
        )
        self.assertListEqual(
            sorted(results),
            sorted(['A/a', 'A/b', 'A/c']),
        )
