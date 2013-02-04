import os.path

__all__ = ['FSNode', 'TagNode']


class FSNode:

    def __init__(self):
        self.children = {}

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, key):
        return self.children[key]

    def __setitem__(self, key, value):
        self.children[key] = value


class TagNode(FSNode):

    def __init__(self, fs_root, tags):
        super().__init__()
        self.root = fs_root
        self.tags = tags

    def __getitem__(self, key):
        try:
            super().__getitem__(key)
        except KeyError:
            return self.tagged()[key]

    def tagged(self):
        return _uniqmap(self.root.find(self.tags))


def _uniqmap(files):
    map = {}
    unique = set(os.path.basename(f) for f in files)
    files = dict((f, os.path.basename(f)) for f in files)
    for f in unique:
        map[f] = files.pop(f)
    for f in files:
        file, ext = os.path.splitext(f)
        new = ''.join([file, ".{}", ext])
        i = 1
        while True:
            newi = new.format(i)
            if newi in map:
                i += 1
                continue
            else:
                map[newi] = files[f]
    return map
