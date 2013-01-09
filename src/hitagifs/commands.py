import argparse

__all__ = ['tag', 'untag', 'find', 'rm', 'rename', 'init']


def tag(fs, *args):
    parser = argparse.ArgumentParser(prog="hfs tag")
    parser.add_argument('tag')
    parser.add_argument('file')
    args = parser.parse_args(args)
    fs.tag(args.file, args.tag)


def untag(fs, *args):
    parser = argparse.ArgumentParser(prog="hfs utag")
    parser.add_argument('tag')
    parser.add_argument('file')
    args = parser.parse_args(args)
    fs.untag(args.file, args.tag)


def find(fs, *args):
    parser = argparse.ArgumentParser(prog="hfs find")
    parser.add_argument('tags', nargs='+')
    args = parser.parse_args(args)
    r = fs.find(args.tags)
    for file in r:
        print(file)


def rm(fs, *args):
    parser = argparse.ArgumentParser(prog="hfs rm")
    parser.add_argument('files', nargs='+')
    args = parser.parse_args(args)
    for file in args.files:
        fs.rm(file)


def rename(fs, *args):
    parser = argparse.ArgumentParser(prog="hfs rename")
    args = parser.parse_args(args)


def init(fs, *args):
    parser = argparse.ArgumentParser(prog="hfs init")
    args = parser.parse_args(args)
