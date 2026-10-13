import json
import hashlib
import os


class VFS:
    def __init__(self, path):
        self.path = path
        self.raw = None
        self.data = None
        self.name = None
        self.load()

    def load(self):
        try:
            with open(self.path, 'rb') as f:
                self.raw = f.read()
        except FileNotFoundError:
            raise RuntimeError(f"VFS не найден: {self.path}")
        try:
            self.data = json.loads(self.raw.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise RuntimeError(f"Неверный формат VFS: {e}")
        self.name = self.data.get('name', os.path.basename(self.path))

    def sha256(self):
        return hashlib.sha256(self.raw).hexdigest()

    def get_root(self):
        return self.data['root']


def split_path(path):
    return [p for p in path.split('/') if p]


def resolve(vfs, path, cwd='/'):
    if not path:
        parts = split_path(cwd)
    elif path.startswith('/'):
        parts = split_path(path)
    else:
        parts = split_path(cwd) + split_path(path)

    result = []
    for p in parts:
        if p == '.':
            continue
        if p == '..':
            if result:
                result.pop()
        else:
            result.append(p)

    node = vfs.get_root()
    for p in result:
        if node.get('type') != 'dir':
            return None
        children = node.get('children', {})
        if p not in children:
            return None
        node = children[p]
    return node


def normalize_path(vfs, path, cwd='/'):
    if not path:
        parts = split_path(cwd)
    elif path.startswith('/'):
        parts = split_path(path)
    else:
        parts = split_path(cwd) + split_path(path)

    result = []
    for p in parts:
        if p == '.':
            continue
        if p == '..':
            if result:
                result.pop()
        else:
            result.append(p)
    return '/' + '/'.join(result)