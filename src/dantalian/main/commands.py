"""
This module contains functions implementing commands for the main script.
"""

import logging
import sys

from dantalian import library

_LOGGER = logging.getLogger(__name__)


def _unpack(args):
    """Unpack tags and files arguments.

    Args:
        args: An object with attributes f and/or t.

    Returns:
        (files, tags), a tuple of lists of strings.
    """
    files = args.f
    if not files:
        tags = args.t
        if not tags:
            if len(args.args) != 2:
                _LOGGER.error('Invalid number of arguments.')
                sys.exit(1)
            files = [args.args[0]]
            tags = [args.args[1]]
        else:
            if len(args.args) != 1:
                _LOGGER.error('Invalid number of arguments.')
                sys.exit(1)
            files = [args.args[0]]
    else:
        tags = args.t
        if not tags:
            if len(args.args) != 1:
                _LOGGER.error('Invalid number of arguments.')
                sys.exit(1)
            tags = [args.args[0]]
        else:
            if len(args.args) != 0:
                _LOGGER.error('Invalid number of arguments.')
                sys.exit(1)
    return files, tags


def tag(args):
    """Tag files."""
    files, tags = _unpack(args)
    root = library.find_root(args.root)
    for current_file in files:
        for current_tag in tags:
            try:
                library.tag(root, current_file, current_tag)
            except OSError as err:
                _LOGGER.error('OSError encountered tagging %s with %s: %s',
                              current_file, current_tag, err)


def untag(args):
    """Untag files."""
    files, tags = _unpack(args)
    root = library.find_root(args.root)
    for current_file in files:
        for current_tag in tags:
            try:
                library.untag(root, current_file, current_tag)
            except OSError as err:
                _LOGGER.error('OSError encountered tagging %s with %s: %s',
                              current_file, current_tag, err)


def search(args):
    """Search for files."""
    root = library.find_root(args.root)
    query_tree = library.parse_query(root, args.query)
    results = library.search(query_tree)
    for entry in results:
        print(entry)
