import tkinter as tk
from tkinter import scrolledtext
import getpass
import socket

from config import parse_args, load_config


class ShellEmulator:
    def __init__(self, root, params):
        self.params = params
        self.root = root
        self.root.title(f"Эмулятор - {getpass.getuser()}@{socket.gethostname()}")
        self.root.geometry("800x500")

        self.output = scrolledtext.ScrolledText(
            root, state='disabled', bg='black', fg='white', font=('Consolas', 10))
        self.output.pack(fill='both', expand=True, padx=5, pady=5)

        self.entry = tk.Entry(root, bg='black', fg='white',
                              font=('Consolas', 10), insertbackground='white')
        self.entry.pack(fill='x', padx=5, pady=(0, 5))
        self.entry.bind('<Return>', self.on_enter)

        self.cwd = '/'
        self.script_mode = False

        self.append("Эмулятор оболочки ОС")
        self.print_prompt()

        if params.get('script'):
            self.root.after(500, self.run_script)

    def append(self, text):
        self.output.configure(state='normal')
        self.output.insert('end', text + '\n')
        self.output.see('end')
        self.output.configure(state='disabled')

    def print_prompt(self):
        self.append(f"{getpass.getuser()}@{socket.gethostname()}:{self.cwd}$ ")

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
        """Возвращает 'EXIT' при выходе, True при ошибке, иначе None."""
        parts = line.split()
        if not parts:
            return None
        cmd, args = parts[0], parts[1:]

        if cmd == 'exit':
            return 'EXIT'
        elif cmd in ('ls', 'cd'):
            self.append(f"{cmd}: {args}")
            return None
        else:
            self.append(f"Ошибка: неизвестная команда: {cmd}")
            return True

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


if __name__ == '__main__':
    args = parse_args()
    params = load_config(args)
    root = tk.Tk()
    app = ShellEmulator(root, params)
    root.mainloop()