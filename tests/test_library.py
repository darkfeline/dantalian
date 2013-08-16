import unittest
import tempfile
import shutil
import os

from dantalian import library


class TestLibraryMethods(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp()
        r = os.path.join(self.root, 'library')
        os.makedirs(os.path.join(r, 'A', 'D'))
        os.makedirs(os.path.join(r, 'B'))
        os.makedirs(os.path.join(r, 'C'))
        os.mknod(os.path.join(r, 'a'))
        self.library = library.init_library(r)
        self._olddir = os.getcwd()
        os.chdir(self.root)

    def tearDown(self):
        shutil.rmtree(self.root)
        os.chdir(self._olddir)

    def assertTagged(self, a, b):
        """Assert `b` is tagged at `a`"""
        self.assertTrue(os.path.exists(a))
        self.assertTrue(os.path.samefile(a, b))

    def test_tag(self):
        l = self.library
        os.chdir('library')
        l.tag('a', '/A')
        self.assertTagged(os.path.join('A', 'a'), 'a')
