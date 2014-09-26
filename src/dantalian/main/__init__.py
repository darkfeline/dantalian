"""
Main entry point.
"""

import logging

from dantalian.main.argparse import make_parser


def main():
    """Script main function."""
    # Set up logging.
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    root_logger.addHandler(handler)
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    handler.setLevel('WARNING')
    # Parse arguments.
    args = make_parser().parse_args()
    if args.log:
        file_handler = logging.FileHandler(args.log)
        root_logger.addHandler(file_handler)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s @%(name)s %(message)s'))
        file_handler.setLevel('DEBUG')
        root_logger.setLevel('DEBUG')
    # Run command.
    args.func(args)

if __name__ == '__main__':
    main()
