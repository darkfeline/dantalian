"""
Main entry point.

This is used by setuptools as an entry point for the command line script.
"""

import logging

from .argparse import make_parser


def main():
    """Script main function."""
    # Set up logging.
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    root_logger.addHandler(handler)
    # Parse arguments.
    args = make_parser().parse_args()
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
    args.func(args)

if __name__ == '__main__':
    main()
