# src/main.py

import tkinter as tk
from gui import CompilerApp

def main():
    root = tk.Tk()
    app = CompilerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
