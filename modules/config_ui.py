import customtkinter as ctk
import tkinter as tk
import os
import json
from PIL import Image
from datetime import datetime

class ConfigWindow(ctk.CTkToplevel):
    def __init__(self, parent, bot_core):
        super().__init__(parent)
        self.geometry("450x650")
        self.configure(fg_color="#050505")
        self.bot_core = bot_core
        self.main_window = parent
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.T = parent.T
        self.title(self.T.get("CONFIG"))
        
        self.healer_entries = []
        self.combo_entries = []
        self.walk_entries = []
        
        # Header
        header = ctk.CTkFrame(self, fg_color="#111", corner_radius=0)
        header.pack(fill="x", pady=0)
        
        lbl_title = ctk.CTkLabel(header, text=self.T.get("CONFIG"), font=ctk.CTkFont(size=16, weight="bold"), text_color="#00d26a")
        lbl_title.pack(side="left", padx=20, pady=5)
        ctk.CTkButton(header, text="X", width=30, height=30, fg_color="#e74c3c", hover_color="#c0392b", command=self.destroy).pack(side="right", padx=5, pady=5)
        ctk.CTkButton(header, text="?", width=30, height=30, fg_color="#3498db", hover_color="#2980b9", text_color="white", font=ctk.CTkFont(weight="bold"), command=self.main_window.show_help).pack(side="right", pady=5)

        header.bind("<ButtonPress-1>", self.start_move)
        header.bind("<B1-Motion>", self.do_move)
        lbl_title.bind("<ButtonPress-1>", self.start_move)
        lbl_title.bind("<B1-Motion>", self.do_move)
        
        # Footer Global (SALVAR MODULOS/PERFIL) - Fora das tabs
        self.global_footer = ctk.CTkFrame(self, fg_color="transparent")
        self.global_footer.pack(side="bottom", fill="x", padx=10, pady=(5, 10))
        
        self.btn_save = ctk.CTkButton(self.global_footer, text=self.T.get("SAVE"), fg_color="#58d68d", text_color="black", font=ctk.CTkFont(size=12, weight="bold"), height=35, hover_color="#45b39d", command=self.save_all)
        self.btn_save.pack(side="left", expand=True, padx=2)
        self.btn_save_prof = ctk.CTkButton(self.global_footer, text=self.T.get("SAVE_PROFILE"), fg_color="#3498db", text_color="white", font=ctk.CTkFont(size=12, weight="bold"), height=35, hover_color="#2980b9", command=self.save_profile)
        self.btn_save_prof.pack(side="left", expand=True, padx=2)
        self.btn_load_prof = ctk.CTkButton(self.global_footer, text=self.T.get("LOAD_PROFILE"), fg_color="#3498db", text_color="white", font=ctk.CTkFont(size=12, weight="bold"), height=35, hover_color="#2980b9", command=self.load_profile_dialog)
        self.btn_load_prof.pack(side="left", expand=True, padx=2)

        # Label de dias restantes da licença
        expiry_date = datetime(2027, 1, 1)
        days_left = (expiry_date - datetime.now()).days
        if days_left > 0:
            days_text = f"🔑 Licença: {days_left} dia(s) restante(s)"
            days_color = "#f39c12" if days_left <= 5 else "#888"
        elif days_left == 0:
            days_text = "⚠️ Licença: expira hoje!"
            days_color = "#e74c3c"
        else:
            days_text = "❌ Licença expirada!"
            days_color = "#e74c3c"
        self.lbl_days = ctk.CTkLabel(self, text=days_text, font=ctk.CTkFont(size=10), text_color=days_color)
        self.lbl_days.pack(side="bottom", pady=(0, 2))
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tab_modules = self.tabview.add(self.T.get("MODULES"))
        self.tab_route = self.tabview.add(self.T.get("WALK_ACTION"))
        
        # ======== ABA: MÓDULOS (HEALS E COMBOS) ========
        
        # --- DIV CURA ---
        div_cura = ctk.CTkFrame(self.tab_modules, fg_color="#1a1c24", border_width=1, border_color="#333", corner_radius=5)
        div_cura.pack(fill="x", padx=2, pady=2)
        
        cura_header = ctk.CTkFrame(div_cura, fg_color="transparent")
        cura_header.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(cura_header, text="HEALER (%hp - %mp)", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00d26a").pack(side="left")
        ctk.CTkButton(cura_header, text="+ NOVO", width=60, height=22, font=ctk.CTkFont(size=11, weight="bold"), fg_color="#104e8b", hover_color="#1e90ff", text_color="white", command=lambda: self.add_healer_row()).pack(side="right")
        
        self.healers_scroll = ctk.CTkScrollableFrame(div_cura, fg_color="transparent", height=85)
        self.healers_scroll.pack(fill="x", padx=5, pady=(0, 5))
        
        # --- Spacer 2px ---
        ctk.CTkFrame(self.tab_modules, fg_color="transparent", height=2).pack()
        
        # --- DIV COMBO ---
        div_combo = ctk.CTkFrame(self.tab_modules, fg_color="#1a1c24", border_width=1, border_color="#333", corner_radius=5)
        div_combo.pack(fill="both", expand=True, padx=2, pady=2)
        
        combo_header = ctk.CTkFrame(div_combo, fg_color="transparent")
        combo_header.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(combo_header, text="HUNT COMBO", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00d26a").pack(side="left")
        ctk.CTkButton(combo_header, text="+ NOVO", width=60, height=22, font=ctk.CTkFont(size=11, weight="bold"), fg_color="#58d68d", hover_color="#45b39d", text_color="black", command=lambda: self.add_combo_row()).pack(side="right")
        
        self.combos_scroll = ctk.CTkScrollableFrame(div_combo, fg_color="transparent", height=140)
        self.combos_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # ======== ABA: WALK ACTION (ROTA E VELOCIDADE) ========
        speed_frame = ctk.CTkFrame(self.tab_route, fg_color="#111")
        speed_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(speed_frame, text="Mouse Speed", text_color="#00d26a", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10)
        self.slider_speed = ctk.CTkSlider(speed_frame, from_=0.2, to=1.8, width=200, command=self.update_speed, progress_color="#58d68d")
        self.slider_speed.set(1.0)
        self.slider_speed.pack(side="left", padx=5, fill="x", expand=True)
        
        self.walk_frame_bg = ctk.CTkFrame(self.tab_route, fg_color="#8c8c8c", corner_radius=0)
        self.walk_frame_bg.pack(fill="both", expand=True, pady=5)
        
        add_btn = ctk.CTkButton(self.walk_frame_bg, text="➕ Mapear Printscreen", height=30, fg_color="#333", text_color="white", hover_color="#7a7a7a", font=ctk.CTkFont(size=14, weight="bold"), command=self.open_marker_selector)
        add_btn.pack(side="bottom", fill="x", pady=2)
        
        self.walk_list_scroll = ctk.CTkScrollableFrame(self.walk_frame_bg, fg_color="transparent", corner_radius=0, orientation="vertical")
        self.walk_list_scroll.pack(fill="both", expand=True)

        # Carregar dados salvos
        self.load_settings()

    def update_speed(self, value):
        from modules.actions import Actions
        # Invertemos o slider visualmente na classe Actions: Quanto maior, mais veloz (menor divisor/tempo)
        # O slider vai de 0.2 a 1.8. 
        Actions.mouse_speed = float(value)

    def add_healer_row(self, name="HEALER", perc="80%", key="f1"):
        row_id = len(self.healer_entries)
        row_frame = ctk.CTkFrame(self.healers_scroll, fg_color="#1a1c24", border_width=1, border_color="#333")
        row_frame.pack(fill="x", pady=2)
        
        name_label = ctk.CTkLabel(row_frame, text=name, width=100, fg_color="#10fd10", text_color="black", font=ctk.CTkFont(size=11, weight="bold"))
        name_label.pack(side="left", padx=5)
        
        entry_perc = ctk.CTkEntry(row_frame, width=65, fg_color="white", text_color="black")
        entry_perc.insert(0, str(perc))
        entry_perc.pack(side="left", padx=5)
        
        entry_key = ctk.CTkEntry(row_frame, width=45, fg_color="white", text_color="black")
        entry_key.insert(0, key)
        entry_key.pack(side="left", padx=5)
        
        del_btn = ctk.CTkButton(row_frame, text="DEL", width=40, fg_color="#8b0000", hover_color="#5a0000", text_color="white", 
                               command=lambda f=row_frame: self.remove_row(f, "healer"))
        del_btn.pack(side="right", padx=5)
        
        self.healer_entries.append({
            "frame": row_frame,
            "name": name,
            "perc": entry_perc,
            "key": entry_key
        })

    def add_combo_row(self, data=None):
        if data is None:
            data = {"name": "Inferno", "key": "f5", "interval": "2.0", "mana": "40", "mobs": "1", "cond": "Sempre", "on": True}
            
        row_frame = ctk.CTkFrame(self.combos_scroll, fg_color="#1a1c24", border_width=1, border_color="#10fd10")
        row_frame.pack(fill="x", pady=5)
        
        line1 = ctk.CTkFrame(row_frame, fg_color="transparent")
        line1.pack(fill="x", padx=5, pady=2)
        
        e_name = ctk.CTkEntry(line1, placeholder_text="Spell Name", width=120, fg_color="white", text_color="black")
        e_name.insert(0, data["name"])
        e_name.pack(side="left", padx=5)
        
        ctk.CTkButton(line1, text="DEL", width=35, fg_color="red", hover_color="#aa0000", 
                     command=lambda f=row_frame: self.remove_row(f, "combo")).pack(side="left", padx=2)
        
        e_key = ctk.CTkEntry(line1, width=50, fg_color="white", text_color="black")
        e_key.insert(0, data["key"])
        e_key.pack(side="right", padx=5)
        ctk.CTkLabel(line1, text="HOTKEY", text_color="white", font=ctk.CTkFont(size=10)).pack(side="right", padx=2)
        
        line2 = ctk.CTkFrame(row_frame, fg_color="#333")
        line2.pack(fill="x", padx=5, pady=(0, 5))
        
        ctk.CTkLabel(line2, text="CD(s)", font=ctk.CTkFont(size=9)).pack(side="left", padx=2)
        e_int = ctk.CTkEntry(line2, width=35, fg_color="white", text_color="black")
        e_int.insert(0, data["interval"])
        e_int.pack(side="left", padx=2)
        
        ctk.CTkLabel(line2, text="MANA", font=ctk.CTkFont(size=9)).pack(side="left", padx=2)
        e_mana = ctk.CTkEntry(line2, width=35, fg_color="white", text_color="black")
        e_mana.insert(0, data["mana"])
        e_mana.pack(side="left", padx=2)
        
        ctk.CTkLabel(line2, text="MOBS >=", font=ctk.CTkFont(size=9, weight="bold"), text_color="#10fd10").pack(side="left", padx=(10, 2))
        e_mobs = ctk.CTkEntry(line2, width=30, fg_color="white", text_color="black")
        e_mobs.insert(0, data["mobs"])
        e_mobs.pack(side="left", padx=2)

        s_cond = ctk.CTkOptionMenu(line2, values=["Sempre", "Alvo", "Vida <"], width=80, fg_color="#444", button_color="#10fd10", button_hover_color="#08a008", text_color="white", dropdown_fg_color="black")
        s_cond.set(data["cond"])
        s_cond.pack(side="left", padx=5)
        
        s_on = ctk.CTkSwitch(line2, text="ON", width=40, progress_color="#10fd10")
        if data["on"]: s_on.select()
        else: s_on.deselect()
        s_on.pack(side="right", padx=5)
        
        self.combo_entries.append({
            "frame": row_frame,
            "name": e_name,
            "key": e_key,
            "interval": e_int,
            "mana": e_mana,
            "mobs": e_mobs,
            "cond": s_cond,
            "on": s_on
        })

    def remove_row(self, frame, type):
        if type == "healer":
            self.healer_entries = [e for e in self.healer_entries if e["frame"] != frame]
        else:
            self.combo_entries = [e for e in self.combo_entries if e["frame"] != frame]
        frame.destroy()

    def get_dump_data(self):
        data = {"healers": [], "combos": [], "mouse_speed": getattr(self.slider_speed, 'get', lambda: 1.0)()}
        for e in self.healer_entries:
            data["healers"].append({"name": e["name"], "perc": e["perc"].get(), "key": e["key"].get()})
        for e in self.combo_entries:
            data["combos"].append({
                "name": e["name"].get(),
                "key": e["key"].get(),
                "interval": e["interval"].get(),
                "mana": e["mana"].get(),
                "mobs": e["mobs"].get(),
                "cond": e["cond"].get(),
                "on": e["on"].get()
            })
        return data

    def save_all(self):
        data = self.get_dump_data()
        
        with open("config.json", "w") as f:
            json.dump(data, f, indent=4)
            
        # Força o motor principal a recarregar o arquivo que acabou de ser salvo
        if hasattr(self, 'bot_core') and self.bot_core:
            self.bot_core.load_config()
        
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("Configurações salvas (config.json) com sucesso!", "#10fd10")
        self.destroy()

    def save_profile(self):
        dialog = ctk.CTkInputDialog(text="Digite o nome do Perfil:", title="Salvar Perfil")
        name = dialog.get_input()
        if not name: return
        os.makedirs("profiles", exist_ok=True)
        data = self.get_dump_data()
        with open(f"profiles/{name}.json", "w") as f:
            json.dump(data, f, indent=4)
            
        if hasattr(self.main_window, 'set_active_profile'):
            self.main_window.set_active_profile(name)
            
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Perfil '{name}' salvo em disco!", "#3498db")

    def load_profile_dialog(self):
        os.makedirs("profiles", exist_ok=True)
        files = [f for f in os.listdir("profiles") if f.endswith(".json")]
        if not files:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Nenhum perfil encontrado.", "red")
            return
            
        popup = ctk.CTkToplevel(self)
        popup.title("Carregar Perfil")
        popup.geometry("300x400")
        popup.attributes("-topmost", True)
        
        scroll = ctk.CTkScrollableFrame(popup)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        for f in files:
            prof_name = f.replace(".json", "")
            btn = ctk.CTkButton(scroll, text=prof_name, fg_color="#333", hover_color="#555",
                                command=lambda n=f: [self.apply_profile(n), popup.destroy()])
            btn.pack(pady=5, fill="x")
            
    def apply_profile(self, filename):
        try:
            with open(f"profiles/{filename}", "r") as f:
                data = json.load(f)
            
            # Limpa tudo antes de carregar
            for e in list(self.healer_entries):
                self.remove_row(e["frame"], "healer")
            for e in list(self.combo_entries):
                self.remove_row(e["frame"], "combo")
                
            for h in data.get("healers", []):
                self.add_healer_row(h["name"], h["perc"], h["key"])
            for c in data.get("combos", []):
                self.add_combo_row(c)
                
            if hasattr(self.main_window, 'set_active_profile'):
                self.main_window.set_active_profile(filename.replace('.json', ''))
                
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Perfil '{filename}' carregado. Clique em SALVAR para confirmar.", "yellow")
        except Exception as e:
            print(f"Erro ao carregar perfil: {e}")

    def load_settings(self):
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    data = json.load(f)
                
                speed = data.get("mouse_speed", 1.0)
                if hasattr(self, 'slider_speed'):
                    self.slider_speed.set(speed)
                    self.update_speed(speed)
                    
                for h in data.get("healers", []):
                    self.add_healer_row(h["name"], h["perc"], h["key"])
                for c in data.get("combos", []):
                    self.add_combo_row(c)
                return
            except:
                pass
        
        # Padrões se não houver arquivo
        self.add_healer_row("HEALER", "80%", "f2")
        self.add_healer_row("MANA HEAL", "80%", "f1")

    # ==========================
    # WALKER (ROTA) LOGIC
    # ==========================
    def open_marker_selector(self):
        popup = tk.Toplevel(self)
        popup.title("Select Marker")
        popup.geometry("360x400")
        popup.configure(bg="#1a1c24")
        popup.attributes("-topmost", True)
        
        scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        markers_dir = "prints/markers"
        if not os.path.exists(markers_dir): return
        
        files = [f for f in os.listdir(markers_dir) if f.endswith(".png")]
        
        row_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        row_frame.pack(fill="x")
        
        col = 0
        for f in files:
            img = Image.open(os.path.join(markers_dir, f))
            ctk_img = ctk.CTkImage(light_image=img, size=(32, 32))
            
            btn = ctk.CTkButton(row_frame, text="", image=ctk_img, width=40, height=40, fg_color="#333", hover_color="#555",
                                command=lambda name=f: [self.add_walk_step(name), popup.destroy()])
            btn.pack(side="left", padx=2, pady=2)
            
            col += 1
            if col > 6:
                col = 0
                row_frame = ctk.CTkFrame(scroll, fg_color="transparent")
                row_frame.pack(fill="x")

    def add_walk_step(self, marker_image_name="marker_001.png", wait="10"):
        count = len(self.walk_entries) + 1
        
        icon_path = os.path.join("prints/markers", marker_image_name)
        icon_img = None
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            icon_img = ctk.CTkImage(light_image=img, size=(20, 20))
            
        row_frame = ctk.CTkFrame(self.walk_list_scroll, fg_color="transparent", height=30)
        row_frame.pack(fill="x", pady=2)
        
        lbl_count = ctk.CTkLabel(row_frame, text=f"{count}", text_color="black", font=ctk.CTkFont(weight="bold"))
        lbl_count.pack(side="left", padx=5)
        
        if icon_img:
            lbl_icon = ctk.CTkLabel(row_frame, text="", image=icon_img)
            lbl_icon.image = icon_img
            lbl_icon.pack(side="left", padx=5)
            
        ctk.CTkLabel(row_frame, text="WALK", text_color="black", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        del_btn = ctk.CTkButton(row_frame, text="DEL", width=40, height=20, fg_color="#8b0000", hover_color="#5a0000", text_color="white", command=lambda f=row_frame: self.remove_walk_row(f))
        del_btn.pack(side="right", padx=5)
        
        wait_entry = ctk.CTkComboBox(row_frame, values=["1", "3", "5", "7", "10", "15"], width=60, height=20, fg_color="white", text_color="black", button_color="black", dropdown_text_color="white")
        wait_entry.set(str(wait))
        wait_entry.pack(side="right", padx=5)
        
        self.walk_entries.append({
            "frame": row_frame,
            "image": marker_image_name,
            "wait": wait_entry
        })
        self._sync_walker_sequence()
        
    def on_mouse_wheel(self, event):
        self.walk_list_scroll._parent_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # Handlers p/ arrastar janela sem borda
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def remove_walk_row(self, frame):
        self.walk_entries = [e for e in self.walk_entries if e["frame"] != frame]
        frame.destroy()
        self._sync_walker_sequence()

    def _sync_walker_sequence(self):
        """Atualiza o motor do Bot (na RAM) com a lista atual da interface"""
        if not self.bot_core: return
        self.bot_core.walker_sequence = []
        for e in self.walk_entries:
            val = int(e["wait"].get())
            self.bot_core.walker_sequence.append({"image": e["image"], "wait": val})
            
    def save_route(self):
        dialog = ctk.CTkInputDialog(text="Digite o nome da Rota:", title="Salvar Rota")
        name = dialog.get_input()
        if not name: return
        os.makedirs("routes", exist_ok=True)
        
        data = []
        for e in self.walk_entries:
            data.append({"image": e["image"], "wait": e["wait"].get()})
            
        with open(f"routes/{name}.json", "w") as f:
            json.dump({"route": data}, f, indent=4)
            
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Rota '{name}' salva com sucesso!", "#1e90ff")

    def load_route_dialog(self):
        os.makedirs("routes", exist_ok=True)
        files = [f for f in os.listdir("routes") if f.endswith(".json")]
        if not files:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Nenhuma rota encontrada.", "red")
            return
            
        popup = ctk.CTkToplevel(self)
        popup.title("Carregar Rota")
        popup.geometry("300x400")
        popup.attributes("-topmost", True)
        
        scroll = ctk.CTkScrollableFrame(popup)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        for f in files:
            route_name = f.replace(".json", "")
            btn = ctk.CTkButton(scroll, text=route_name, fg_color="#333", hover_color="#555",
                                command=lambda n=f: [self.apply_route(n), popup.destroy()])
            btn.pack(pady=5, fill="x")
            
    def apply_route(self, filename):
        try:
            with open(f"routes/{filename}", "r") as f:
                data = json.load(f)
                
            for e in list(self.walk_entries):
                self.remove_walk_row(e["frame"])
                
            for step in data.get("route", []):
                self.add_walk_step(step["image"], step["wait"])
                
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Rota '{filename}' carregada direto no motor.", "yellow")
        except Exception as e:
            print(f"Erro ao carregar rota: {e}")

