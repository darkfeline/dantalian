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
        join = posixpath.join
        os.mknod(join('A', 'a'))
        os.mknod(join('A', 'b'))
        os.link(join('A', 'b'), join('B', 'b'))

    def test_is_tagged_with(self):
        join = posixpath.join
        self.assertTrue(baselib.is_tagged_with(join('A', 'b'), 'B'))
        self.assertFalse(baselib.is_tagged_with(join('A', 'a'), 'B'))

    def test_tag_with(self):
        join = posixpath.join
        baselib.tag_with(join('A', 'a'), 'B')
        self.assertSameFile(join('A', 'a'), join('B', 'a'))

    def test_untag_with(self):
        join = posixpath.join
        baselib.untag_with(join('A', 'b'), 'B')
        self.assertNotSameFile(join('A', 'b'), join('B', 'b'))

    def test_rename_all(self):
        join = posixpath.join
        baselib.rename_all(self.root, join('A', 'b'), 'foo')
        self.assertSameFile(join('A', 'foo'), join('B', 'foo'))

    def test_remove_all(self):
        join = posixpath.join
        baselib.remove_all(self.root, join('A', 'b'))
        self.assertFalse(posixpath.exists(join('A', 'b')))
        self.assertFalse(posixpath.exists(join('B', 'b')))

    def test_list_links(self):
        tags = baselib.list_links(self.root, posixpath.join('A', 'b'))
        self.assertSetEqual(set(tags),
                            set(posixpath.join(self.root, filename, 'b')
                                for filename in ('A', 'B')))


class TestLibraryBaseSearch(testlib.FSMixin):

    def setUp(self):
        super().setUp()
        os.makedirs('A')
        os.makedirs('B')
        os.makedirs('C')
        join = posixpath.join
        os.mknod(join('A', 'a'))
        os.mknod(join('A', 'b'))
        os.mknod(join('A', 'c'))
        os.mknod(join('C', 'd'))
        os.link(join('A', 'b'), join('B', 'b'))
        os.link(join('A', 'c'), join('B', 'c'))
        os.link(join('A', 'c'), join('C', 'c'))

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
            [posixpath.join('A', 'c')],
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
            sorted([posixpath.join('A', 'a'),
                    posixpath.join('A', 'b'),
                    posixpath.join('A', 'c'),
                    posixpath.join('C', 'd')]),
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
            [posixpath.join('A', 'a')]
        )

    def test_dir(self):
        results = baselib.search(
            baselib.DirNode('A')
        )
        self.assertListEqual(
            sorted(results),
            sorted([posixpath.join('A', 'a'),
                    posixpath.join('A', 'b'),
                    posixpath.join('A', 'c')]),
        )
