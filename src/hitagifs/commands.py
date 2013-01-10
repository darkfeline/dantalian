import argparse
import logging
import os

from hitagifs.fs import HitagiFS

__all__ = ['tag', 'untag', 'tags', 'find', 'rm', 'rename', 'convert', 'init']
logger = logging.getLogger(__name__)


def tag(fs, *args):
    logger.debug('tag(%s, %s)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs tag", add_help=False)
    parser.add_argument('tag')
    parser.add_argument('file')
    args = parser.parse_args(args)
    fs.tag(args.file, args.tag)


def untag(fs, *args):
    logger.debug('untag(%s, %s)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs utag", add_help=False)
    parser.add_argument('tag')
    parser.add_argument('file')
    args = parser.parse_args(args)
    fs.untag(args.file, args.tag)


def tags(fs, *args):
    logger.debug('tags(%s, %s)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs tags", add_help=False)
    parser.add_argument('file')
    args = parser.parse_args(args)
    r = fs.listtags(args.file)
    for tag in r:
        print(tag)


def find(fs, *args):
    logger.debug('find(%s, %s)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs find", add_help=False)
    parser.add_argument('tags', nargs='+')
    args = parser.parse_args(args)
    r = fs.find(args.tags)
    for file in r:
        print(file)


def rm(fs, *args):
    logger.debug('rm(%s, %s)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs rm", add_help=False)
    parser.add_argument('files', nargs='+')
    args = parser.parse_args(args)
    for file in args.files:
        fs.rm(file)


def rename(fs, *args):
    logger.debug('rename(%s, %s)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs rename", add_help=False)
    parser.add_argument('file')
    parser.add_argument('new')
    args = parser.parse_args(args)
    fs.rename(args.source, args.dest)


def convert(fs, *args):
    logger.debug('convert(%s, %s)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs convert", add_help=False)
    parser.add_argument('--alt')
    parser.add_argument('dir')
    args = parser.parse_args(args)
    alt = getattr(args, 'alt', None)
    fs.convert(args.dir, alt)


def init(*args):
    logger.debug('init(%s)', args)
    parser = argparse.ArgumentParser(prog="hfs init", add_help=False)
    parser.add_argument('root', nargs="?", default=os.getcwd())
    args = parser.parse_args(args)
    HitagiFS.init(args.root)
