import argparse
import os

from . import commands


# Set up parser {{{1
# Main parser {{{2
parser = argparse.ArgumentParser()
parser.add_argument('--log', metavar='LOGFILE')

# Parser templates {{{2
_library_args = argparse.ArgumentParser(add_help=False)
_library_args.add_argument('--root', metavar='PATH')

# Subparsers {{{2
subparsers = parser.add_subparsers(title='Commands')

# Library commands {{{3
# tag {{{4
tmp_parser = subparsers.add_parser(
    'tag',
    usage='''%(prog)s [--root PATH] FILE TAG
%(prog)s [--root PATH] TAG -f FILE [FILE ...]
%(prog)s [--root PATH] FILE -t TAG [TAG ...]
%(prog)s [--root PATH] -f FILE [FILE ...] -t TAG [TAG ...]
%(prog)s --help''',
    parents=[_library_args])
tmp_parser.add_argument('-f', nargs='+', metavar='FILE')
tmp_parser.add_argument('-t', nargs='+', metavar='TAG')
tmp_parser.add_argument('args', nargs='*')
tmp_parser.set_defaults(func=commands.tag)

# untag {{{4
tmp_parser = subparsers.add_parser(
    'untag',
    usage='''%(prog)s [--root PATH] FILE TAG
%(prog)s [--root PATH] TAG -f FILE [FILE ...]
%(prog)s [--root PATH] FILE -t TAG [TAG ...]
%(prog)s [--root PATH] -f FILE [FILE ...] -t TAG [TAG ...]
%(prog)s --help''',
    parents=[_library_args])
tmp_parser.add_argument('-f', nargs='+', metavar='FILE')
tmp_parser.add_argument('-t', nargs='+', metavar='TAG')
tmp_parser.add_argument('args', nargs='*')
tmp_parser.set_defaults(func=commands.untag)

# mktag {{{4
tmp_parser = subparsers.add_parser(
    'mktag',
    parents=[_library_args])
tmp_parser.add_argument('tags', nargs='+', metavar='TAG')
tmp_parser.set_defaults(func=commands.mktag)

# rmtag {{{4
tmp_parser = subparsers.add_parser(
    'rmtag',
    parents=[_library_args])
tmp_parser.add_argument('tags', nargs='+', metavar='TAG')
tmp_parser.set_defaults(func=commands.rmtag)

# tags {{{4
tmp_parser = subparsers.add_parser(
    'tags',
    parents=[_library_args])
tmp_parser.add_argument('file')
tmp_parser.add_argument('--print0', action='store_const', const='\00',
                        default='\n', dest='endline')
tmp_parser.set_defaults(func=commands.tags)

# find {{{4
tmp_parser = subparsers.add_parser(
    'find',
    parents=[_library_args])
tmp_parser.add_argument('tags', nargs='+', metavar='TAG')
tmp_parser.add_argument('--print0', action='store_const', const='\00',
                        default='\n', dest='endline')
tmp_parser.add_argument('-t', metavar='DIR', dest='target_dir')
tmp_parser.set_defaults(func=commands.find)

# rm {{{4
tmp_parser = subparsers.add_parser(
    'rm',
    parents=[_library_args])
tmp_parser.add_argument('files', nargs='+', metavar='FILE')
tmp_parser.set_defaults(func=commands.rm)

# rename {{{4
tmp_parser = subparsers.add_parser(
    'rename',
    parents=[_library_args])
tmp_parser.add_argument('file')
tmp_parser.add_argument('new')
tmp_parser.set_defaults(func=commands.rename)

# convert {{{4
tmp_parser = subparsers.add_parser(
    'convert',
    parents=[_library_args])
tmp_parser.add_argument('dirs', nargs='+', metavar='DIR')
tmp_parser.set_defaults(func=commands.convert)

# revert {{{4
tmp_parser = subparsers.add_parser(
    'revert',
    parents=[_library_args])
tmp_parser.add_argument('dirs', nargs='+', metavar='DIR')
tmp_parser.set_defaults(func=commands.revert)

# fix {{{4
tmp_parser = subparsers.add_parser(
    'fix',
    parents=[_library_args])
tmp_parser.set_defaults(func=commands.fix)

# clean {{{4
tmp_parser = subparsers.add_parser(
    'clean',
    parents=[_library_args])
tmp_parser.set_defaults(func=commands.clean)

# mount {{{4
tmp_parser = subparsers.add_parser(
    'mount',
    parents=[_library_args])
tmp_parser.add_argument('path')
tmp_parser.set_defaults(func=commands.mount)

# Global commands {{{3
# init {{{4
tmp_parser = subparsers.add_parser('init')
tmp_parser.add_argument('path', nargs='?', default=os.getcwd())
tmp_parser.set_defaults(func=commands.init)

# Socket commands {{{3
# mknode {{{4
tmp_parser = subparsers.add_parser(
    'mknode',
    parents=[_library_args])
tmp_parser.add_argument('path')
tmp_parser.add_argument('tags', nargs='+', metavar='TAG')
tmp_parser.set_defaults(func=commands.mknode)

# rmnode {{{4
tmp_parser = subparsers.add_parser(
    'rmnode',
    parents=[_library_args])
tmp_parser.add_argument('paths', nargs='+', metavar='PATH')
tmp_parser.set_defaults(func=commands.rmnode)
