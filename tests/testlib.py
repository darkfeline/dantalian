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
This module contains TestCase mixin classes that implement functionality
shared between other test modules.

"""

import os
import posixpath
import shutil
import tempfile
from unittest import TestCase


class SameFileMixin(TestCase):

    """TestCase mixin with convenient assertions."""

    # pylint: disable=invalid-name

    def assertSameFile(self, file1, file2):
        """Assert both files are the same by inode."""
        self.assertTrue(posixpath.samefile(file1, file2))

    def assertNotSameFile(self, file1, file2):
        """Assert files are not the same.

        Assertion fails if first file does not exist.
        """
        self.assertTrue(posixpath.exists(file1))
        if posixpath.exists(file2):
            self.assertFalse(posixpath.samefile(file1, file2))


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
        """Get path of text fixture directory root."""
        return self.__tmproot

    def tearDown(self):
        os.chdir(self.__olddir)
        shutil.rmtree(self.__tmproot)
