import tkinter as tk

class RegionSelector(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        
        # Configurar para ser um overlay interativo e semi-transparente
        self.attributes('-alpha', 0.3)
        self.attributes('-fullscreen', True)
        self.attributes('-topmost', True)
        self.config(cursor="cross")
        
        self.canvas = tk.Canvas(self, cursor="cross", bg="gray")
        self.canvas.pack(fill="both", expand=True)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        # Pressione ESC para cancelar a seleção
        self.bind("<Escape>", lambda e: self.cancel())

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline='red', width=2, fill="black"
        )

    def on_drag(self, event):
        curX, curY = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_release(self, event):
        end_x, end_y = (event.x, event.y)
        
        # Calcular região (tratando casos onde o usuário arrasta da direita para a esquerda ou de baixo para cima)
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        # Ignorar cliques acidentais (áreas muito pequenas)
        if x2 - x1 < 10 or y2 - y1 < 10:
            self.cancel()
            return

        region = {
            "top": y1,
            "left": x1,
            "width": x2 - x1,
            "height": y2 - y1
        }
        
        self.destroy()
        if self.callback:
            self.callback(region)

    def cancel(self):
        self.destroy()
        if self.callback:
            self.callback(None)
