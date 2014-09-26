import unittest
import tempfile
import shutil
import os

from dantalian.library import base as library


class TestLibraryBase(unittest.TestCase):

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

    def assertSameFile(self, a, b):
        self.assertTrue(os.path.samefile(a, b))

    def assertNotSameFile(self, a, b):
        if os.path.exists(a) and os.path.exists(b):
            self.assertFalse(os.path.samefile(a, b))
        else:
            self.assertFalse(not os.path.exists(a) and not os.path.exists(b))

    def test_tag(self):
        library.tag(os.path.join('A', 'a'), 'B')
        self.assertSameFile(os.path.join('A', 'a'), os.path.join('B', 'a'))

    def test_untag(self):
        library.untag(os.path.join('A', 'b'), 'B')
        self.assertNotSameFile(os.path.join('A', 'b'), os.path.join('B', 'b'))


class TestLibraryBaseQuery(unittest.TestCase):

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
        results = library.query(
            library.AndNode(
                [library.TagNode('A'),
                 library.TagNode('B'),
                 library.TagNode('C')]
            )
        )
        self.assertListEqual(
            results,
            [os.path.join('A', 'c')],
        )

    def test_or(self):
        results = library.query(
            library.OrNode(
                [library.TagNode('A'),
                 library.TagNode('B'),
                 library.TagNode('C')]
            )
        )
        self.assertListEqual(
            sorted(results),
            sorted([os.path.join('A', 'a'),
                    os.path.join('A', 'b'),
                    os.path.join('A', 'c'),
                    os.path.join('C', 'd')]),
        )
