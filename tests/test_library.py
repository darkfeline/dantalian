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

    def test_tag(self):
        l = self.library
        os.chdir('library')
        l.tag('a', '/A')
        self.assertTrue(os.path.isfile(os.path.join('A', 'a')))
        self.assertTrue(os.path.samefile(os.path.join('A', 'a'), 'a'))
