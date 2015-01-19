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
