import customtkinter as ctk
import threading
from modules.ui import MainWindow
import sys
import ctypes

# Força o Windows a usar coordenadas de pixels reais (Ignora Escala de 125%/150%)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass


if __name__ == "__main__":
    # Configurar aparencia global do tkinter
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    # Criar e rodar o app
    app = MainWindow()
    app.mainloop()
