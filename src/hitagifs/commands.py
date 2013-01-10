import argparse
import logging

from hitagifs import fs

__all__ = ['tag', 'untag', 'find', 'rm', 'rename', 'mount']
logger = logging.getLogger(__name__)


def tag(fs, *args):
    logger.debug('tag(%s, %s)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs tag")
    parser.add_argument('tag')
    parser.add_argument('file')
    args = parser.parse_args(args)
    fs.tag(args.file, args.tag)


def untag(fs, *args):
    logger.debug('untag(%s, %s)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs utag")
    parser.add_argument('tag')
    parser.add_argument('file')
    args = parser.parse_args(args)
    fs.untag(args.file, args.tag)


def find(fs, *args):
    logger.debug('find(%s, %s)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs find")
    parser.add_argument('tags', nargs='+')
    args = parser.parse_args(args)
    r = fs.find(args.tags)
    for file in r:
        print(file)


def rm(fs, *args):
    logger.debug('rm(%s, %s)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs rm")
    parser.add_argument('files', nargs='+')
    args = parser.parse_args(args)
    for file in args.files:
        fs.rm(file)


def rename(fs, *args):
    logger.debug('rename(%s, %s)', fs, args)
    parser = argparse.ArgumentParser(prog="hfs rename")
    parser.add_argument('source')
    parser.add_argument('dest')
    args = parser.parse_args(args)
    fs.rename(args.source, args.dest)


def mount(*args):
    logger.debug('mount(%s)', args)
    parser = argparse.ArgumentParser(prog="hfs mount")
    parser.add_argument('root')
    args = parser.parse_args(args)
    fs.mount(args.root)
