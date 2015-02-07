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
This module contains unit tests for dantalian.searching
"""

import os
import posixpath
from unittest import TestCase

from dantalian import searching

from . import testlib

# pylint: disable=missing-docstring


class QueryMixin(TestCase):

    """TestCase mixin with convenient assertions."""

    # pylint: disable=invalid-name
    # pylint: disable=too-few-public-methods

    def assertSameQuery(self, node1, node2):
        """Assert two query node trees are equal."""
        self.assertEqual(node1, node2)
        if isinstance(node1, searching.GroupNode):
            for i in range(len(node1.children)):
                self.assertSameQuery(node1.children[i], node2.children[i])


class TestLibraryParsing(QueryMixin):

    root = 'foobar'

    def test_parse_and(self):
        tree = searching.parse_query(self.root, "AND A B C END")
        self.assertSameQuery(tree, searching.AndNode(
            [searching.DirNode("A"),
             searching.DirNode("B"),
             searching.DirNode("C")]))

    def test_parse_or(self):
        tree = searching.parse_query(self.root, "OR A B C END")
        self.assertSameQuery(tree, searching.OrNode(
            [searching.DirNode("A"),
             searching.DirNode("B"),
             searching.DirNode("C")]))

    def test_parse_minus(self):
        tree = searching.parse_query(self.root, "MINUS A B C END")
        self.assertSameQuery(tree, searching.MinusNode(
            [searching.DirNode("A"),
             searching.DirNode("B"),
             searching.DirNode("C")]))

    def test_parse_and_escape(self):
        tree = searching.parse_query(self.root,
                                     r"AND '\AND' '\\AND' '\\\AND' END")
        self.assertSameQuery(tree, searching.AndNode(
            [searching.DirNode(r'AND'),
             searching.DirNode(r'\AND'),
             searching.DirNode(r'\\AND')]))

    def test_parse_end_escape(self):
        tree = searching.parse_query(self.root, r"AND A B \\END END")
        self.assertSameQuery(tree, searching.AndNode(
            [searching.DirNode(r'A'),
             searching.DirNode(r'B'),
             searching.DirNode(r'END')]))

    def test_parse_and_or(self):
        tree = searching.parse_query(self.root, "AND A B C OR spam eggs END END")
        self.assertSameQuery(tree, searching.AndNode(
            [searching.DirNode("A"),
             searching.DirNode("B"),
             searching.DirNode("C"),
             searching.OrNode(
                 [searching.DirNode('spam'),
                  searching.DirNode('eggs')])
            ]))

    def test_parse_tags(self):
        tree = searching.parse_query(self.root, "AND A /B //C //D/E END")
        self.assertSameQuery(tree, searching.AndNode(
            [searching.DirNode("A"),
             searching.DirNode("/B"),
             searching.DirNode(posixpath.join(self.root, 'C')),
             searching.DirNode(posixpath.join(self.root, 'D/E')),
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
        results = searching.search(
            searching.AndNode(
                [searching.DirNode('A'),
                 searching.DirNode('B'),
                 searching.DirNode('C')]
            )
        )
        self.assertListEqual(
            results,
            ['A/c'],
        )

    def test_or(self):
        results = searching.search(
            searching.OrNode(
                [searching.DirNode('A'),
                 searching.DirNode('B'),
                 searching.DirNode('C')]
            )
        )
        self.assertListEqual(
            sorted(results),
            sorted(['A/a', 'A/b', 'A/c', 'C/d']),
        )

    def test_minus(self):
        results = searching.search(
            searching.MinusNode(
                [searching.DirNode('A'),
                 searching.DirNode('B'),
                 searching.DirNode('C')]
            )
        )
        self.assertListEqual(
            results,
            ['A/a']
        )

    def test_dir(self):
        results = searching.search(
            searching.DirNode('A')
        )
        self.assertListEqual(
            sorted(results),
            sorted(['A/a', 'A/b', 'A/c']),
        )
