import argparse
import logging
import os

from hitagifs.fs import HitagiFS

__all__ = ['tag', 'untag', 'tags', 'find', 'rm', 'rename', 'convert', 'init']
logger = logging.getLogger(__name__)


def tag(fs, *args):
    logger.debug('tag(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs tag", add_help=False)
    parser.add_argument('tag')
    parser.add_argument('file', nargs="+")
    args = parser.parse_args(args)
    for file in args.file:
        try:
            fs.tag(file, args.tag)
        except IsADirectoryError:
            logger.warn('skipped %r; convert it first', file)


def untag(fs, *args):
    logger.debug('untag(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs utag", add_help=False)
    parser.add_argument('tag')
    parser.add_argument('file', nargs="+")
    args = parser.parse_args(args)
    for file in args.file:
        fs.untag(file, args.tag)


def tags(fs, *args):
    logger.debug('tags(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs tags", add_help=False)
    parser.add_argument('file')
    args = parser.parse_args(args)
    r = fs.listtags(args.file)
    for tag in r:
        print(tag)


def find(fs, *args):
    logger.debug('find(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs find", add_help=False)
    parser.add_argument('tags', nargs='+')
    args = parser.parse_args(args)
    r = fs.find(args.tags)
    for file in r:
        print(file)


def rm(fs, *args):
    logger.debug('rm(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs rm", add_help=False)
    parser.add_argument('files', nargs='+')
    args = parser.parse_args(args)
    for file in args.files:
        fs.rm(file)


def rename(fs, *args):
    logger.debug('rename(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs rename", add_help=False)
    parser.add_argument('file')
    parser.add_argument('new')
    args = parser.parse_args(args)
    fs.rename(args.source, args.dest)


def convert(fs, *args):
    logger.debug('convert(%r, %r)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs convert", add_help=False)
    parser.add_argument('dir', nargs="+")
    args = parser.parse_args(args)
    for dir in args.dir:
        try:
            fs.convert(dir)
        except NotADirectoryError:
            logger.warn('%r is not a directory; skipping', dir)
        except FileExistsError:
            logger.warn('Name conflict %r; skipping', dir)


def init(*args):
    logger.debug('init(%r)', args)
    parser = argparse.ArgumentParser(prog="hfs init", add_help=False)
    parser.add_argument('root', nargs="?", default=os.getcwd())
    args = parser.parse_args(args)
    HitagiFS.init(args.root)
