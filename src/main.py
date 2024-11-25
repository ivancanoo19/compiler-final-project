# src/main.py

import tkinter as tk
from gui import CompilerApp

def main():
    root = tk.Tk()          # Costrulle la ventana base para la interfaz grafica 
    app = CompilerApp(root) # Instancia el objeto que configura la ventana principal 
    root.mainloop()         # Bucle que atiende los eventos en la interfaz 

if __name__ == "__main__":
    main()
