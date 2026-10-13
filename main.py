import tkinter as tk
from config import parse_args, load_config
from gui import ShellEmulator

if __name__ == '__main__':
    args = parse_args()
    params = load_config(args)
    root = tk.Tk()
    app = ShellEmulator(root, params)
    root.mainloop()