import tkinter as tk
from tkinter import scrolledtext
import getpass
import socket


class ShellEmulator:
    def __init__(self, root):
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

        # --- ИСПРАВЛЕНИЕ: фокус на поле ввода ---
        self.entry.focus_set()
        self.root.after(100, self.entry.focus_force)

        # клик по любому месту окна возвращает фокус в entry
        self.root.bind('<Button-1>', lambda e: self.entry.focus_set())
        # ---------------------------------------------------

        self.cwd = '/'
        self.print_prompt()

    def append(self, text):
        self.output.configure(state='normal')
        self.output.insert('end', text + '\n')
        self.output.see('end')
        self.output.configure(state='disabled')

    def print_prompt(self):
        self.append(f"{getpass.getuser()}@{socket.gethostname()}:{self.cwd}$ ")

    def on_enter(self, event):
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
        elif cmd in ('ls', 'cd'):
            self.append(f"{cmd}: {args}")
        else:
            self.append(f"Ошибка: неизвестная команда: {cmd}")
        return None


if __name__ == '__main__':
    root = tk.Tk()
    app = ShellEmulator(root)
    root.mainloop()