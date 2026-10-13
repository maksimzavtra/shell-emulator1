from vfs import resolve, normalize_path


class CommandError(Exception):
    pass


def cmd_ls(vfs, cwd, args):
    path = args[0] if args else cwd
    node = resolve(vfs, path, cwd)
    if node is None:
        raise CommandError(f"ls: {path}: Нет такого файла или каталога")
    if node.get('type') == 'file':
        return path.rstrip('/').split('/')[-1] or path
    children = node.get('children', {})
    if not children:
        return ""
    lines = []
    for name in sorted(children.keys()):
        child = children[name]
        lines.append(name + ('/' if child.get('type') == 'dir' else ''))
    return '\n'.join(lines)


def cmd_cd(vfs, cwd, args):
    path = args[0] if args else '/'
    node = resolve(vfs, path, cwd)
    if node is None:
        raise CommandError(f"cd: {path}: Нет такого файла или каталога")
    if node.get('type') != 'dir':
        raise CommandError(f"cd: {path}: Не является каталогом")
    return normalize_path(vfs, path, cwd)


def cmd_pwd(vfs, cwd, args):
    return cwd


def cmd_rev(vfs, cwd, args):
    if not args:
        raise CommandError("rev: не указан текст")
    return ' '.join(args)[::-1]


def _du_size(node):
    if node.get('type') == 'file':
        content = node.get('content', '') or ''
        return len(content.encode('utf-8'))
    total = 0
    for child in node.get('children', {}).values():
        total += _du_size(child)
    return total


def cmd_du(vfs, cwd, args):
    path = args[0] if args else cwd
    node = resolve(vfs, path, cwd)
    if node is None:
        raise CommandError(f"du: {path}: Нет такого файла или каталога")
    return f"{_du_size(node)}\t{normalize_path(vfs, path, cwd)}"


def cmd_chown(vfs, cwd, args):
    if len(args) < 2:
        raise CommandError("chown: использование: chown <owner> <path>")
    owner, path = args[0], args[1]
    node = resolve(vfs, path, cwd)
    if node is None:
        raise CommandError(f"chown: {path}: Нет такого файла или каталога")
    node['owner'] = owner
    return f"chown: {normalize_path(vfs, path, cwd)} -> {owner}"