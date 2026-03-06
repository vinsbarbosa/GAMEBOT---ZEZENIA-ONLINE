import tkinter as tk
import threading

class Overlay(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "black")
        self.config(bg="black")
        self.withdraw() # Inicia escondido
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

    def show_marker(self, x, y, color="red", duration=1000, order_num=""):
        # x, y são posições globais da tela
        size = 20
        self.geometry(f"{size*2+20}x{size*2}+{x-size}+{y-size}")
        
        self.canvas.delete("all")
        # Desenha uma mira
        self.canvas.create_oval(5, 5, size*2-5, size*2-5, outline=color, width=2)
        self.canvas.create_line(size, 0, size, size*2, fill=color, width=2)
        self.canvas.create_line(0, size, size*2, size, fill=color, width=2)
        
        # Desenha o número do step caso passado
        if order_num:
            self.canvas.create_text(size*2 + 8, size, text=str(order_num), fill="yellow", font=("Arial", 12, "bold"))
        
        self.deiconify()
        # Timer para esconder
        self.after(duration, self.withdraw)

    def show_rect(self, x, y, w, h, color="cyan", duration=2000):
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.canvas.delete("all")
        self.canvas.create_rectangle(2, 2, w-2, h-2, outline=color, width=2)
        self.deiconify()
        self.after(duration, self.withdraw)
