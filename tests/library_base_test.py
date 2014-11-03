"""
This module contains unit tests for dantalian.library.base
"""

import tempfile
import shutil
import os

from . import testlib
from dantalian.library import base

# pylint: disable=missing-docstring,too-many-public-methods


class TestLibraryBase(testlib.ExtendedTestCase):

    def setUp(self):
        self._olddir = os.getcwd()
        self.root = tempfile.mkdtemp()
        os.chdir(self.root)
        os.makedirs('A')
        os.makedirs('B')
        os.mknod(os.path.join('A', 'a'))
        os.mknod(os.path.join('A', 'b'))
        os.link(os.path.join('A', 'b'), os.path.join('B', 'b'))

    def tearDown(self):
        shutil.rmtree(self.root)
        os.chdir(self._olddir)

    def test_tag(self):
        base.tag(os.path.join('A', 'a'), 'B')
        self.assertSameFile(os.path.join('A', 'a'), os.path.join('B', 'a'))

    def test_untag(self):
        base.untag(os.path.join('A', 'b'), 'B')
        self.assertNotSameFile(os.path.join('A', 'b'), os.path.join('B', 'b'))

    def test_rename(self):
        base.rename(self.root, os.path.join('A', 'b'), 'foo')
        self.assertSameFile(os.path.join('A', 'foo'), os.path.join('B', 'foo'))

    def test_remove(self):
        base.remove(self.root, os.path.join('A', 'b'))
        self.assertFalse(os.path.exists(os.path.join('A', 'b')))
        self.assertFalse(os.path.exists(os.path.join('B', 'b')))

    def test_list_tags(self):
        tags = base.list_tags(self.root, os.path.join('A', 'b'))
        self.assertSetEqual(set(tags),
                            set(os.path.join(self.root, filename, 'b')
                                for filename in ('A', 'B')))


class TestLibraryBaseQuery(testlib.ExtendedTestCase):

    def setUp(self):
        self._olddir = os.getcwd()
        self.root = tempfile.mkdtemp()
        os.chdir(self.root)
        os.makedirs('A')
        os.makedirs('B')
        os.makedirs('C')
        os.mknod(os.path.join('A', 'a'))
        os.mknod(os.path.join('A', 'b'))
        os.mknod(os.path.join('A', 'c'))
        os.mknod(os.path.join('C', 'd'))
        os.link(os.path.join('A', 'b'), os.path.join('B', 'b'))
        os.link(os.path.join('A', 'c'), os.path.join('B', 'c'))
        os.link(os.path.join('A', 'c'), os.path.join('C', 'c'))

    def tearDown(self):
        shutil.rmtree(self.root)
        os.chdir(self._olddir)

    def test_and(self):
        results = base.search(
            base.AndNode(
                [base.DirNode('A'),
                 base.DirNode('B'),
                 base.DirNode('C')]
            )
        )
        self.assertListEqual(
            results,
            [os.path.join('A', 'c')],
        )

    def test_or(self):
        results = base.search(
            base.OrNode(
                [base.DirNode('A'),
                 base.DirNode('B'),
                 base.DirNode('C')]
            )
        )
        self.assertListEqual(
            sorted(results),
            sorted([os.path.join('A', 'a'),
                    os.path.join('A', 'b'),
                    os.path.join('A', 'c'),
                    os.path.join('C', 'd')]),
        )

    def test_minus(self):
        results = base.search(
            base.MinusNode(
                [base.DirNode('A'),
                 base.DirNode('B'),
                 base.DirNode('C')]
            )
        )
        self.assertListEqual(
            results,
            [os.path.join('A', 'a')]
        )

    def test_dir(self):
        results = base.search(
            base.DirNode('A')
        )
        self.assertListEqual(
            sorted(results),
            sorted([os.path.join('A', 'a'),
                    os.path.join('A', 'b'),
                    os.path.join('A', 'c')]),
        )
