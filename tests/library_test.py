import unittest
import tempfile
import shutil
import os

from dantalian import library


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
