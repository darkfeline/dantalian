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
This module contains unit tests for dantalian.base
"""

import os
from unittest.mock import patch

from dantalian import base

from . import testlib

# pylint: disable=missing-docstring


class TestLink(testlib.FSMixin, testlib.SameFileMixin):

    def setUp(self):
        super().setUp()
        os.mkdir('bag')
        os.mknod('apple')

    def test_link(self):
        base.link(self.root, 'apple', 'bag/apple')
        self.assertSameFile('apple', 'bag/apple')


class TestLinkDir(testlib.FSMixin, testlib.SameFileMixin):

    def setUp(self):
        super().setUp()
        os.mkdir('bag')
        os.mkdir('apple')

    def test_link_dir(self):
        with patch('dantalian.dtags.add_tag') as mock_func:
            base.link(self.root, 'apple', 'bag/apple')
            self.assertSameFile('apple', 'bag/apple')
            mock_func.assert_called_with('apple', '//bag/apple')

# XXX Finish unit tests
