# Copyright 2015 Allen Li
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This package provides an easy framework for implementing commands.
"""

import argparse
import logging

from . import commands


def main():
    """Entry function."""
    # Set up logging.
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    root_logger.addHandler(handler)
    # Parse arguments.
    parser = _make_parser()
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


def _make_parser():
    """Make argument parser for main script.

    Argument parser is reusable, so keep the parser around instead of remaking
    it.

    You can use it to parse and run an argument list like so:

        >>> parser = make_parser()
        >>> args = parser.parse_args(['tag', 'foo', 'bar'])
        >>> args.func(args)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    subparsers = parser.add_subparsers(title='Commands')
    for cmd in commands.COMMANDS:
        cmd.add_parser(subparsers)
    return parser

if __name__ == '__main__':
    main()
