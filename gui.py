import tkinter as tk
from tkinter import scrolledtext
import getpass
import socket

from vfs import VFS, resolve, normalize_path
from commands import (
    CommandError, cmd_ls, cmd_cd, cmd_pwd, cmd_rev, cmd_du,
)

HANDLERS = {
    'ls': cmd_ls,
    'cd': cmd_cd,
    'pwd': cmd_pwd,
    'rev': cmd_rev,
    'du': cmd_du,
}


class ShellEmulator:
    def __init__(self, root, params):
        self.params = params
        self.root = root
        self.root.title(f"Эмулятор - {getpass.getuser()}@{socket.gethostname()}")
        self.root.geometry("800x500")

        self.output = scrolledtext.ScrolledText(
            root, state='disabled', bg='black', fg='white',
            font=('Consolas', 10)
        )
        self.output.pack(fill='both', expand=True, padx=5, pady=5)

        self.entry = tk.Entry(root, bg='black', fg='white',
                              font=('Consolas', 10), insertbackground='white')
        self.entry.pack(fill='x', padx=5, pady=(0, 5))
        self.entry.bind('<Return>', self.on_enter)

        # фокус на поле ввода
        self.entry.focus_set()
        self.root.after(100, self.entry.focus_force)
        self.root.bind('<Button-1>', lambda e: self.entry.focus_set())

        self.cwd = '/'
        self.script_mode = False
        self.vfs = None

        self.append("Эмулятор оболочки ОС")
        self.load_vfs()
        self.print_prompt()

        if params.get('script'):
            self.root.after(500, self.run_script)

    # ---------- VFS ----------
    def load_vfs(self):
        path = self.params.get('vfs')
        if not path:
            self.append("VFS не указан")
            return
        try:
            self.vfs = VFS(path)
            self.append(f"VFS загружен: {self.vfs.name}")
        except RuntimeError as e:
            self.append(f"Ошибка загрузки VFS: {e}")
            self.vfs = None

    # ---------- Вывод ----------
    def append(self, text):
        self.output.configure(state='normal')
        self.output.insert('end', text + '\n')
        self.output.see('end')
        self.output.configure(state='disabled')

    def print_prompt(self):
        self.append(f"{getpass.getuser()}@{socket.gethostname()}:{self.cwd}$ ")

    # ---------- Обработка ввода ----------
    def on_enter(self, event):
        if self.script_mode:
            return
        line = self.entry.get()
        self.entry.delete(0, 'end')
        self.append(line)
        if self.execute(line) == 'EXIT':
            self.root.destroy()
            return
        self.print_prompt()

    def execute(self, line):
        parts = line.split()
        if not parts:
            return None
        cmd, args = parts[0], parts[1:]

        if cmd == 'exit':
            return 'EXIT'

        if cmd == 'vfs-info':
            if self.vfs is None:
                self.append("Ошибка: VFS не загружен")
                return True
            self.append(f"VFS: {self.vfs.name}")
            self.append(f"SHA-256: {self.vfs.sha256()}")
            return None

        if self.vfs is None:
            self.append(f"Ошибка: VFS не загружен, команда '{cmd}' недоступна")
            return True

        handler = HANDLERS.get(cmd)
        if handler is None:
            self.append(f"Ошибка: неизвестная команда: {cmd}")
            return True

        try:
            result = handler(self.vfs, self.cwd, args)
        except CommandError as e:
            self.append(str(e))
            return True

        if cmd == 'cd':
            self.cwd = result
        elif result is not None and result != "":
            self.append(result)
        return None

    # ---------- Стартовый скрипт ----------
    def run_script(self):
        path = self.params.get('script')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = [l.rstrip('\n') for l in f]
        except Exception as e:
            self.append(f"Ошибка чтения скрипта: {e}")
            return

        self.script_mode = True
        self.append(f"--- Скрипт: {path} ---")

        def run_next(idx):
            if idx >= len(lines):
                self.append("--- Скрипт завершён ---")
                self.script_mode = False
                self.print_prompt()
                return

            line = lines[idx].strip()
            if not line or line.startswith('#'):
                self.root.after(50, run_next, idx + 1)
                return

            self.append(line)
            result = self.execute(line)
            if result == 'EXIT':
                self.root.destroy()
                return
            if result is True:
                self.append("--- Скрипт остановлен из-за ошибки ---")
                self.script_mode = False
                return

            self.root.after(300, run_next, idx + 1)

        self.root.after(300, run_next, 0)