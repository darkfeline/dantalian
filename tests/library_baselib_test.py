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
This module contains unit tests for dantalian.library.baselib
"""

import os
import posixpath

from dantalian.library import baselib

from . import testlib

# pylint: disable=missing-docstring


class TestLibraryBase(testlib.FSMixin, testlib.SameFileMixin):

    def setUp(self):
        super().setUp()
        os.makedirs('A')
        os.makedirs('B')
        os.mknod('A/a')
        os.mknod('A/b')
        os.link('A/b', 'B/b')

    def test_is_tagged_with(self):
        self.assertTrue(baselib.is_tagged_with('A/b', 'B'))
        self.assertFalse(baselib.is_tagged_with('A/a', 'B'))

    def test_tag_with(self):
        baselib.tag_with('A/a', 'B')
        self.assertSameFile('A/a', 'B/a')

    def test_untag_with(self):
        baselib.untag_with('A/b', 'B')
        self.assertNotSameFile('A/b', 'B/b')

    def test_rename_all(self):
        baselib.rename_all(self.root, 'A/b', 'foo')
        self.assertSameFile('A/foo', 'B/foo')

    def test_remove_all(self):
        baselib.remove_all(self.root, 'A/b')
        self.assertFalse(posixpath.exists('A/b'))
        self.assertFalse(posixpath.exists('B/b'))

    def test_list_links(self):
        tags = baselib.list_links(self.root, 'A/b')
        self.assertSetEqual(set(tags),
                            set(posixpath.join(self.root, filename, 'b')
                                for filename in ('A', 'B')))


class TestLibraryBaseSearch(testlib.FSMixin):

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
        results = baselib.search(
            baselib.AndNode(
                [baselib.DirNode('A'),
                 baselib.DirNode('B'),
                 baselib.DirNode('C')]
            )
        )
        self.assertListEqual(
            results,
            ['A/c'],
        )

    def test_or(self):
        results = baselib.search(
            baselib.OrNode(
                [baselib.DirNode('A'),
                 baselib.DirNode('B'),
                 baselib.DirNode('C')]
            )
        )
        self.assertListEqual(
            sorted(results),
            sorted(['A/a', 'A/b', 'A/c', 'C/d']),
        )

    def test_minus(self):
        results = baselib.search(
            baselib.MinusNode(
                [baselib.DirNode('A'),
                 baselib.DirNode('B'),
                 baselib.DirNode('C')]
            )
        )
        self.assertListEqual(
            results,
            ['A/a']
        )

    def test_dir(self):
        results = baselib.search(
            baselib.DirNode('A')
        )
        self.assertListEqual(
            sorted(results),
            sorted(['A/a', 'A/b', 'A/c']),
        )


class TestListSymlink(testlib.FSMixin, testlib.SameFileMixin):

    """Test list_links() on symlinks."""

    def setUp(self):
        super().setUp()
        os.mkdir('A')
        os.symlink('A', 'B')

    def test_symlinks(self):
        links = baselib.list_links(self.root, 'A')
        self.assertSetEqual(set(links),
                            set(posixpath.join(self.root, filename)
                                for filename in ('A', 'B')))
