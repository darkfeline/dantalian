"""
This module contains TestCase mixin classes that implement functionality
shared between other test modules.

"""

import os
import shutil
import tempfile
from unittest import TestCase


class SamefileMixin(TestCase):

    """TestCase mixin with convenient assertions."""

    # pylint: disable=invalid-name

    def assertSameFile(self, file1, file2):
        """Assert both files are the same by inode."""
        self.assertTrue(os.path.samefile(file1, file2))

    def assertNotSameFile(self, file1, file2):
        """Assert files are not the same.

        Assertion fails if first file does not exist.
        """
        self.assertTrue(os.path.exists(file1))
        if os.path.exists(file2):
            self.assertFalse(os.path.samefile(file1, file2))


class FSMixin(TestCase):

    """TestCase mixin with convenient assertions.

    File system setup mixin.

    Example:

        class Foo(FSMixin):
            def setUp(self):
                super().setUp()
                # Do any file system initialization here
                os.makedir('foo')
                os.mknod('foo/bar')

    """

    # pylint: disable=invalid-name

    def setUp(self):
        self.__olddir = os.getcwd()
        self.__tmproot = tempfile.mkdtemp()
        os.chdir(self.__tmproot)

    @property
    def root(self):
        return self.__tmproot

    def tearDown(self):
        os.chdir(self.__olddir)
        shutil.rmtree(self.__tmproot)

