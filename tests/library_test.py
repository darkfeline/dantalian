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
This module contains unit tests for dantalian.library
"""

import os
import posixpath
from unittest import TestCase

from dantalian import library
from dantalian.library import baselib

from . import testlib

# pylint: disable=missing-docstring


class QueryMixin(TestCase):

    """TestCase mixin with convenient assertions."""

    # pylint: disable=invalid-name
    # pylint: disable=too-few-public-methods

    def assertSameQuery(self, node1, node2):
        """Assert two query node trees are equal."""
        self.assertEqual(node1, node2)
        if isinstance(node1, baselib.GroupNode):
            for i in range(len(node1.children)):
                self.assertSameQuery(node1.children[i], node2.children[i])


class TestLibraryParsing(QueryMixin):

    root = 'foobar'

    def test_parse_and(self):
        tree = library.parse_query(self.root, "AND A B C END")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode("A"),
             baselib.DirNode("B"),
             baselib.DirNode("C")]))

    def test_parse_or(self):
        tree = library.parse_query(self.root, "OR A B C END")
        self.assertSameQuery(tree, baselib.OrNode(
            [baselib.DirNode("A"),
             baselib.DirNode("B"),
             baselib.DirNode("C")]))

    def test_parse_minus(self):
        tree = library.parse_query(self.root, "MINUS A B C END")
        self.assertSameQuery(tree, baselib.MinusNode(
            [baselib.DirNode("A"),
             baselib.DirNode("B"),
             baselib.DirNode("C")]))

    def test_parse_and_escape(self):
        tree = library.parse_query(self.root,
                                   r"AND '\AND' '\\AND' '\\\AND' END")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode(r'AND'),
             baselib.DirNode(r'\AND'),
             baselib.DirNode(r'\\AND')]))

    def test_parse_end_escape(self):
        tree = library.parse_query(self.root, r"AND A B \\END END")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode(r'A'),
             baselib.DirNode(r'B'),
             baselib.DirNode(r'END')]))

    def test_parse_and_or(self):
        tree = library.parse_query(self.root, "AND A B C OR spam eggs END END")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode("A"),
             baselib.DirNode("B"),
             baselib.DirNode("C"),
             baselib.OrNode(
                 [baselib.DirNode('spam'),
                  baselib.DirNode('eggs')])
            ]))

    def test_parse_tags(self):
        tree = library.parse_query(self.root, "AND A /B //C //D/E END")
        self.assertSameQuery(tree, baselib.AndNode(
            [baselib.DirNode("A"),
             baselib.DirNode("/B"),
             baselib.DirNode(posixpath.join(self.root, 'C')),
             baselib.DirNode(posixpath.join(self.root, 'D/E')),
            ]))


class TestLibraryTag(testlib.FSMixin, testlib.SameFileMixin):

    def setUp(self):
        super().setUp()
        os.mkdir('2hu')
        os.mknod('flan')

    def test_tag(self):
        library.tag(self.root, 'flan', '2hu')
        self.assertSameFile('2hu/flan', 'flan')


class TestLibrarySearch(testlib.FSMixin, testlib.SameFileMixin):

    def setUp(self):
        super().setUp()
        os.mkdir('2hu')
        os.mknod('flan')
        os.link('flan', '2hu/flan')

    def test_search(self):
        query_tree = library.parse_query(self.root, 'AND 2hu . END')
        result = library.search(query_tree)
        self.assertEqual(result, ['2hu/flan'])

    def test_list_links(self):
        query_tree = library.parse_query(self.root, 'AND 2hu . END')
        result = library.search(query_tree)
