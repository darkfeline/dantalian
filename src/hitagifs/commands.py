import argparse

from hitagifs.fs import HitagiFS


def tag(*args):
    parser = argparse.ArgumentParser(prog="hfs tag")
    fs = HitagiFS()


def utag(*args):
    parser = argparse.ArgumentParser(prog="hfs utag")


def find(*args):
    parser = argparse.ArgumentParser(prog="hfs find")


def rm(*args):
    parser = argparse.ArgumentParser(prog="hfs rm")


def rename(*args):
    parser = argparse.ArgumentParser(prog="hfs rename")

__all__ = [tag, utag, find, rm, rename]
