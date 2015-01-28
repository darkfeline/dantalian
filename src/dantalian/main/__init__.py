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

"""This package implements the Dantalian program."""

import logging

from . import argparse


def main():
    """Entry function."""
    # Set up logging.
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    root_logger.addHandler(handler)
    # Parse arguments.
    parser = argparse.make_parser()
    args = parser.parse_args()
    if args.debug:
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s @%(name)s %(message)s'))
        # handler default is pass all
        root_logger.setLevel('DEBUG')
    else:
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        handler.setLevel('WARNING')
        # root logger default is WARNING
    # Run command.
    try:
        func = args.func
    except AttributeError:
        parser.print_help()
    else:
        func(args)

if __name__ == '__main__':
    main()
