import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from PIL import Image
from modules.bot_core import BotCore
from modules.overlay import Overlay
from modules.region_selector import RegionSelector
from modules.config_ui import ConfigWindow
import os
import keyboard
from modules.lang import T

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Inicia e Lê Linguagem
        T.load()
        self.T = T
        
        # Configurar Janela sem borda do Windows para visual customizado
        self.geometry("140x535")
        self.title("Misteremio Bot - Zezenia Online")
        self.overrideredirect(True) # Remove barra superior padrao
        self.configure(fg_color="#050505") # Fundo preto
        
        # Mudar o icone da janela (usando tk.PhotoImage, perfeito para PNG)
        try:
            icon_img = tk.PhotoImage(file=os.path.join("prints", "markers", "marker_054.png"))
            self.iconphoto(True, icon_img)
            self.wm_iconphoto(True, icon_img)
        except Exception as e:
            print("Aviso: icone marker_054 não encontrado:", e)
        
        # Força o Windows a desenhar o App na Barra de Tarefas mesmo sem borda
        self.update_idletasks()
        self.after(20, self.set_appwindow)
        
        # Overlay Visual e Bot Core
        self.overlay = Overlay(self)
        # Callbacks visuais do bot core para UI
        self.bot_core = BotCore()
        self.bot_core.ui_callback = self.log_message
        self.bot_core.visual_callback = self.visualize_point
        self.bot_core.stats_callback = self.update_stats_ui
        
        # Inicia a thread do motor em pano de fundo imediatamente
        self.bot_core.start()
        self.start_timer = None
        self.elapsed_seconds = 0
        
        # --- TECLA DE PAUSE/BREAK GLOBAL (Thread Safe) ---
        keyboard.add_hotkey('pause', lambda: self.after(0, self.disable_all_modules_ui))
        keyboard.add_hotkey('insert', lambda: self.after(0, self.disable_all_modules_ui))
        
        # --- TITLE BAR CUSTOMIZADA ---
        self.title_bar = tk.Frame(self, bg="black", relief="raised", bd=0, height=25)
        self.title_bar.pack(fill="x", side="top")
        
        # Arrastar janela pelo title bar
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        
        self.title_label = tk.Label(self.title_bar, text="MistBot", fg="white", bg="black", font=("Arial", 9, "bold"))
        self.title_label.pack(side="left", padx=2)
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)

        self.profile_label = tk.Label(self.title_bar, text="None", fg="#3498db", bg="black", font=("Arial", 7, "bold"))
        self.profile_label.pack(side="left", padx=2)
        self.profile_label.bind("<ButtonPress-1>", self.start_move)
        self.profile_label.bind("<B1-Motion>", self.do_move)

        # Botoões Janela
        self.btn_close = tk.Button(self.title_bar, text="X", bg="#cc0000", fg="black", font=("Arial", 8, "bold"), bd=0, width=3, command=self.close_app)
        self.btn_close.pack(side="right", padx=1, pady=1)

        # --- SEÇÃO: CALIBRATE ---
        calib_label = ctk.CTkLabel(self, text="CALIBRATE", text_color="#00d26a", font=ctk.CTkFont(size=12, weight="bold"))
        calib_label.pack(pady=(2, 0))

        calib_frame = ctk.CTkFrame(self, fg_color="transparent")
        calib_frame.pack(fill="x", padx=5, pady=2)

        fnt = ctk.CTkFont(size=11, weight="bold")
        self.btn_cal_map = ctk.CTkButton(calib_frame, text=self.T.get("MAP_ZONE"), width=130, height=22, font=fnt, fg_color="#58d68d", hover_color="#45b39d", text_color="black", corner_radius=0, command=self.start_map_calibration)
        self.btn_cal_map.pack(pady=1)
        self.btn_cal_battle = ctk.CTkButton(calib_frame, text=self.T.get("BATTLE_ZONE"), width=130, height=22, font=fnt, fg_color="#58d68d", hover_color="#45b39d", text_color="black", corner_radius=0, command=self.start_battle_calibration)
        self.btn_cal_battle.pack(pady=1)
        self.btn_cal_hp = ctk.CTkButton(calib_frame, text=self.T.get("HP_BAR"), width=130, height=22, font=fnt, fg_color="#58d68d", hover_color="#45b39d", text_color="black", corner_radius=0, command=self.start_hp_calibration)
        self.btn_cal_hp.pack(pady=1)
        self.btn_cal_mana = ctk.CTkButton(calib_frame, text=self.T.get("MANA_BAR"), width=130, height=22, font=fnt, fg_color="#58d68d", hover_color="#45b39d", text_color="black", corner_radius=0, command=self.start_mana_calibration)
        self.btn_cal_mana.pack(pady=1)
        
        self.btn_cal_loot = ctk.CTkButton(calib_frame, text=self.T.get("LOOT_ZONE"), width=130, height=22, font=fnt, fg_color="#58d68d", hover_color="#45b39d", text_color="black", corner_radius=0, command=self.start_loot_calibration)
        self.btn_cal_loot.pack(pady=1)

        self._draw_separator(2)

        # --- SEÇÃO: TOGGLES (MODULOS) ---
        toggles_frame = ctk.CTkFrame(self, fg_color="transparent")
        toggles_frame.pack(pady=2, padx=5, fill="x")

        # Top: Vertical 1x4
        grid_frame = ctk.CTkFrame(toggles_frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=2)
        
        self.btn_auto_walk = self._create_toggle_btn(grid_frame, f"{self.T.get('AUTO_WALK')}: {self.T.get('OFF')}", cmd=self.toggle_automations)
        self.btn_auto_loot = self._create_toggle_btn(grid_frame, f"{self.T.get('AUTO_LOOT')}: {self.T.get('OFF')}", cmd=self.toggle_auto_loot)
        self.btn_auto_heal = self._create_toggle_btn(grid_frame, f"{self.T.get('AUTO_HEAL')}: {self.T.get('OFF')}", cmd=self.toggle_auto_heal)
        self.btn_auto_mana = self._create_toggle_btn(grid_frame, f"{self.T.get('AUTO_MANA')}: {self.T.get('OFF')}", cmd=self.toggle_auto_mana)
        self.btn_auto_combo = self._create_toggle_btn(grid_frame, f"{self.T.get('AUTO_COMBO')}: {self.T.get('OFF')}", cmd=self.toggle_auto_combo)

        # Centro: AUTO SPACE grande (Horizontal)
        self.btn_auto_space = ctk.CTkButton(toggles_frame, text=f"{self.T.get('AUTO_SPACE')}\n{self.T.get('OFF')}", width=130, height=26, fg_color="#e74c3c", hover_color="#c0392b", text_color="white", corner_radius=0, command=self.toggle_auto_space)
        self.btn_auto_space.pack(pady=1, fill="x")

        self._draw_separator(4)

        # Bottom
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(fill="x", padx=5)
        
        self.btn_config = ctk.CTkButton(right_frame, text=self.T.get("CONFIG"), width=130, height=22, font=ctk.CTkFont(size=11, weight="bold"), fg_color="#58d68d", hover_color="#45b39d", text_color="black", corner_radius=0, command=self.open_config_window)
        self.btn_config.pack(pady=1)
        self.btn_on_top = ctk.CTkButton(right_frame, text=self.T.get("ALWAYS_ON_TOP").replace("\n", " "), width=130, height=22, font=ctk.CTkFont(size=11, weight="bold"), fg_color="#3498db", hover_color="#2980b9", text_color="white", corner_radius=0, command=self.toggle_on_top)
        self.btn_on_top.pack(pady=1)

        # --- LOGOMARCA BOTTOM ---
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.bottom_frame.pack(fill="x", pady=(5, 0))
        self.bottom_frame.pack_propagate(False)
        try:
            img = Image.open(os.path.join("prints", "markers", "marker_054.png"))
            ctk_img = ctk.CTkImage(light_image=img, size=(30, 30))
            self.logo_label = ctk.CTkLabel(self.bottom_frame, text="", image=ctk_img, cursor="hand2")
            self.logo_label.image = ctk_img
            self.logo_label.place(relx=0.5, y=20, anchor="center")
            self.logo_label.bind("<Button-1>", lambda e: self.toggle_log())
            
            # Botões inferiors auxiliares (Lang e Restart)
            self.btn_lang = ctk.CTkButton(self.bottom_frame, text=self.T.get("LANG")[:2], width=30, height=20, fg_color="#3498db", hover_color="#2980b9", text_color="white", font=ctk.CTkFont(weight="bold", size=10), corner_radius=3, command=self.cycle_lang)
            self.btn_lang.place(relx=0.15, y=20, anchor="w")
            
            self.btn_restart = ctk.CTkButton(self.bottom_frame, text="⟳", width=30, height=20, fg_color="#ffa500", hover_color="#e69500", text_color="black", font=ctk.CTkFont(weight="bold", size=14), corner_radius=3, command=self.restart_app)
            self.btn_restart.place(relx=0.85, y=20, anchor="e")
            
            self.logo_anim_offset = 0
            self.logo_anim_dir = 1
            self.animate_logo()
        except Exception as e:
            print("Logo não carregada na interface:", e)

        self._draw_separator(2)

        # --- SEÇÃO: LOG ---
        self.log_visible = True

        self.log_box = ctk.CTkTextbox(self, fg_color="black", text_color="white", corner_radius=0, height=80, font=ctk.CTkFont(family="Consolas", size=9))
        self.log_box.pack(fill="x", padx=5, pady=(5, 5))
        self.log_message("> Misteremio Bot initialized!", "#00ff00")

        self.on_top_state = False

    def _draw_separator(self, pady=5):
        sep = tk.Frame(self, bg="white", height=2)
        sep.pack(fill="x", padx=15, pady=pady)
        
    def animate_logo(self):
        if hasattr(self, 'logo_label'):
            # Verifica se QUALQUER módulo está ativo
            modulos = ['auto_walk_enabled', 'auto_heal_enabled', 'auto_mana_enabled', 'auto_combo_enabled', 'auto_space_enabled']
            ativo = any([getattr(self.bot_core, m, False) for m in modulos])
            
            if ativo:
                # Efeito Levitando (Pra cima e pra baixo)
                self.logo_anim_offset += self.logo_anim_dir * 0.5
                if self.logo_anim_offset > 5:
                    self.logo_anim_dir = -1
                elif self.logo_anim_offset < -5:
                    self.logo_anim_dir = 1
                self.logo_label.place_configure(y=20 + self.logo_anim_offset)
            else:
                # Volta para o Centro quando Pausado
                self.logo_anim_offset = 0
                self.logo_label.place_configure(y=20)
                
            self.after(30, self.animate_logo) # Loop a 30fps

    def _create_toggle_btn(self, parent, text, cmd=None):
        btn = ctk.CTkButton(parent, text=text, width=130, height=22, fg_color="#e74c3c", hover_color="#c0392b", corner_radius=0, text_color="white", font=ctk.CTkFont(size=11), command=cmd)
        btn.pack(pady=1)
        return btn

    def toggle_on_top(self):
        self.on_top_state = not self.on_top_state
        self.after(0, lambda: self.attributes("-topmost", self.on_top_state))
        new_color = "#58d68d" if self.on_top_state else "#3498db"
        text_color = "black" if self.on_top_state else "white"
        self.after(0, lambda: self.btn_on_top.configure(fg_color=new_color, text_color=text_color))
        self.log_message(f"Always on top: {'ON' if self.on_top_state else 'OFF'}")

    def toggle_auto_combo(self):
        self.bot_core.auto_combo_enabled = not getattr(self.bot_core, 'auto_combo_enabled', False)
        state = self.bot_core.auto_combo_enabled
        if state:
            self.btn_auto_combo.configure(text=f"{self.T.get('AUTO_COMBO')}: {self.T.get('ON')}", fg_color="#58d68d", text_color="black")
            self.log_message(f"Auto Combo {self.T.get('ON')}", "#58d68d")
        else:
            self.btn_auto_combo.configure(text=f"{self.T.get('AUTO_COMBO')}: {self.T.get('OFF')}", fg_color="#e74c3c", text_color="white")
            self.log_message(f"Auto Combo {self.T.get('OFF')}", "red")

    def toggle_auto_space(self):
        self.bot_core.auto_space_enabled = not getattr(self.bot_core, 'auto_space_enabled', False)
        state = self.bot_core.auto_space_enabled
        if state:
            self.btn_auto_space.configure(text=f"{self.T.get('AUTO_SPACE')}\n{self.T.get('ON')}", fg_color="#58d68d", text_color="black")
            self.log_message(f"Auto Space {self.T.get('ON')}", "#58d68d")
        else:
            self.btn_auto_space.configure(text=f"{self.T.get('AUTO_SPACE')}\n{self.T.get('OFF')}", fg_color="#e74c3c", text_color="white")
            self.log_message(f"Auto Space {self.T.get('OFF')}", "red")

    def toggle_auto_heal(self):
        self.bot_core.auto_heal_enabled = not getattr(self.bot_core, 'auto_heal_enabled', False)
        state = self.bot_core.auto_heal_enabled
        if state:
            self.btn_auto_heal.configure(fg_color="#58d68d", text_color="black")
            self.log_message(f"Auto Heal {self.T.get('ON')}", "#58d68d")
        else:
            self.btn_auto_heal.configure(fg_color="#e74c3c", text_color="white")
            self.log_message(f"Auto Heal {self.T.get('OFF')}", "red")
        self.update_stats_ui(self.bot_core.hp_percent, self.bot_core.mana_percent)

    def toggle_auto_mana(self):
        self.bot_core.auto_mana_enabled = not getattr(self.bot_core, 'auto_mana_enabled', False)
        state = self.bot_core.auto_mana_enabled
        if state:
            self.btn_auto_mana.configure(fg_color="#58d68d", text_color="black")
            self.log_message(f"Auto Mana {self.T.get('ON')}", "#58d68d")
        else:
            self.btn_auto_mana.configure(fg_color="#e74c3c", text_color="white")
            self.log_message(f"Auto Mana {self.T.get('OFF')}", "red")
        self.update_stats_ui(self.bot_core.hp_percent, self.bot_core.mana_percent)

    def toggle_automations(self):
        if not self.bot_core.auto_walk_enabled:
            self.bot_core.auto_walk_enabled = True
            self.btn_auto_walk.configure(text=f"{self.T.get('AUTO_WALK')}: {self.T.get('ON')}", fg_color="#58d68d", text_color="black")
            self.log_message(f"Auto Walk {self.T.get('ON')}", "#58d68d")
        else:
            self.bot_core.auto_walk_enabled = False
            self.btn_auto_walk.configure(text=f"{self.T.get('AUTO_WALK')}: {self.T.get('OFF')}", fg_color="#e74c3c", text_color="white")
            self.log_message(f"Auto Walk {self.T.get('OFF')}", "red")

    def toggle_auto_loot(self):
        self.bot_core.auto_loot_enabled = not getattr(self.bot_core, 'auto_loot_enabled', False)
        state = self.bot_core.auto_loot_enabled
        if state:
            self.btn_auto_loot.configure(text=f"{self.T.get('AUTO_LOOT')}: {self.T.get('ON')}", fg_color="#58d68d", text_color="black")
            self.log_message(f"Auto Loot {self.T.get('ON')}", "#58d68d")
        else:
            self.btn_auto_loot.configure(text=f"{self.T.get('AUTO_LOOT')}: {self.T.get('OFF')}", fg_color="#e74c3c", text_color="white")
            self.log_message(f"Auto Loot {self.T.get('OFF')}", "red")

    def disable_all_modules_ui(self):
        self.bot_core.disable_all_modules()
        self.btn_auto_walk.configure(text=f"{self.T.get('AUTO_WALK')}: {self.T.get('OFF')}", fg_color="#e74c3c", text_color="white")
        self.btn_auto_loot.configure(text=f"{self.T.get('AUTO_LOOT')}: {self.T.get('OFF')}", fg_color="#e74c3c", text_color="white")
        self.btn_auto_heal.configure(text=f"{self.T.get('AUTO_HEAL')}: {self.T.get('OFF')} - {self.bot_core.hp_percent}%", fg_color="#e74c3c", text_color="white")
        self.btn_auto_mana.configure(text=f"{self.T.get('AUTO_MANA')}: {self.T.get('OFF')} - {self.bot_core.mana_percent}%", fg_color="#e74c3c", text_color="white")
        self.btn_auto_combo.configure(text=f"{self.T.get('AUTO_COMBO')}: {self.T.get('OFF')}", fg_color="#e74c3c", text_color="white")
        self.btn_auto_space.configure(text=f"{self.T.get('AUTO_SPACE')}\n{self.T.get('OFF')}", fg_color="#e74c3c", text_color="white")
        self.log_message("[PauseBreak] Todos os módulos OFF", "orange")

    def log_message(self, message, color="#ffffff"):
        self.after(0, lambda: self._log_to_box(message, color))

    def _log_to_box(self, message, color):
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")
        
    def toggle_log(self):
        if self.log_visible:
            self.log_box.pack_forget()
            self.geometry("140x445") # Limite exato da linha branca abaixo da logo
            self.log_visible = False
        else:
            self.log_box.pack(fill="x", padx=5, pady=(5, 5))
            self.geometry("140x535")
            self.log_visible = True

    def update_stats_ui(self, hp, mana):
        """Atualiza os textos dos botões com a % de vida/mana (Thread Safe)."""
        self.after(0, lambda: self._refresh_stats_labels(hp, mana))

    def _refresh_stats_labels(self, hp, mana):
        heal_state = self.T.get("ON") if getattr(self.bot_core, 'auto_heal_enabled', False) else self.T.get("OFF")
        self.btn_auto_heal.configure(text=f"{self.T.get('AUTO_HEAL')}: {heal_state} - {hp}%")
        
        mana_state = self.T.get("ON") if getattr(self.bot_core, 'auto_mana_enabled', False) else self.T.get("OFF")
        self.btn_auto_mana.configure(text=f"{self.T.get('AUTO_MANA')}: {mana_state} - {mana}%")

    def open_config_window(self):
        ConfigWindow(self, self.bot_core)

    def visualize_point(self, x, y, color, order_num=""):
        self.after(0, lambda: self.overlay.show_marker(x, y, color, order_num=order_num))

    def start_map_calibration(self):
        self.log_message(f"[{self.T.get('MAP_ZONE')}] Calibrating...")
        self.withdraw()
        RegionSelector(self, self.on_region_selected)

    def on_region_selected(self, region):
        self.deiconify()
        if region:
            self.bot_core.map_region = region
            self.btn_cal_map.configure(text=f"{self.T.get('MAP_ZONE')} OK", fg_color="#58d68d", text_color="black")
            self.log_message(f"Mapa OK: L:{region['left']}, T:{region['top']}", "#58d68d")
        else:
            self.log_message("Abortado.")

    def start_battle_calibration(self):
        self.withdraw()
        RegionSelector(self, self.on_battle_region_selected)

    def on_battle_region_selected(self, region):
        self.deiconify()
        if region:
            self.bot_core.battle_region = region
            self.btn_cal_battle.configure(text=f"{self.T.get('BATTLE_ZONE')} OK", fg_color="#58d68d", text_color="black")
            self.log_message(f"Battle OK: {region['width']}x{region['height']}", "#58d68d")
            # Persiste no config.json para ferramentas externas (calibrate_battle.py etc.)
            self._save_region_to_config("battle_region", region)

    def start_hp_calibration(self):
        self.withdraw()
        RegionSelector(self, self.on_hp_region_selected)

    def on_hp_region_selected(self, region):
        self.deiconify()
        if region:
            self.bot_core.hp_region = region
            self.btn_cal_hp.configure(text=f"{self.T.get('HP_BAR')} OK", fg_color="#58d68d", text_color="black")
            self.log_message("HP OK", "#58d68d")

    def start_mana_calibration(self):
        self.withdraw()
        RegionSelector(self, self.on_mana_region_selected)

    def on_mana_region_selected(self, region):
        self.deiconify()
        if region:
            self.bot_core.mana_region = region
            self.btn_cal_mana.configure(text=f"{self.T.get('MANA_BAR')} OK", fg_color="#58d68d", text_color="black")
            self.log_message("Mana OK.", "#58d68d")

    def start_loot_calibration(self):
        self.withdraw()
        RegionSelector(self, self.on_loot_region_selected)

    def on_loot_region_selected(self, region):
        self.deiconify()
        if region:
            self.bot_core.loot_region = region
            self.btn_cal_loot.configure(text=f"{self.T.get('LOOT_ZONE')} OK", fg_color="#58d68d", text_color="black")
            self.log_message("Loot Zone OK.", "#58d68d")

    def _save_region_to_config(self, key, region):
        """Persiste uma regiao calibrada no config.json."""
        import json
        cfg = {}
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    cfg = json.load(f)
            except Exception:
                pass
        cfg[key] = region
        try:
            with open("config.json", "w") as f:
                json.dump(cfg, f, indent=2)
        except Exception as e:
            self.log_message(f"Aviso: nao foi possivel salvar {key}: {e}", "orange")

    def set_active_profile(self, name):
        """Atualiza a TopBar com o nome do perfil de cacada carregado."""
        self.profile_label.config(text=f"{name[:15]}")  # Truncado p/ evitar text wrap

    def cycle_lang(self):
        self.T.cycle()
        prompt = tk.messagebox.showinfo("Language", f"Language set to {self.T.current_lang}.\nClick the [ ⟳ ] button at the bottom to restart the bot.")
        self.btn_lang.configure(text=self.T.get("LANG")[:2])

    def show_help(self):
        help_win = ctk.CTkToplevel(self)
        help_win.title(self.T.get("HELP"))
        help_win.geometry("500x350")
        help_win.attributes("-topmost", True)
        
        tabview = ctk.CTkTabview(help_win)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        langs = ["PT", "EN", "ES", "PL"]
        texts = {
            "PT": "------ Misteremio Bot TIPS ------\n\n1. CALIBRATE: Clique para mapear zonas. Para recalibrar, clique novamente.\n\n2. EMERGENCY STOP: Pressione PAUSE BREAK ou INSERT no teclado. Desativa todos os módulos de uma vez!\n\n3. AUTO SPACE: Pressiona a tecla ESPAÇO até focar um inimigo (barra vermelha da Battle Zone).\n\n4. AUTO COMBO: Lança magias configuradas se as condições do config baterem (mana, monstros, alvo).\n\n5. WALK ACTION: O robô caminha pelos prints na ZONA DE MAPA. O clique usa Injeção DX humana (double tap).",
            "EN": "------ Misteremio Bot TIPS ------\n\n1. CALIBRATE: Click to map zones. Click again to recalibrate.\n\n2. EMERGENCY STOP: Press PAUSE BREAK or INSERT on your keyboard to disable all modules instantly!\n\n3. AUTO SPACE: Spams SPACE key until an enemy is targeted (red background in Battle Zone).\n\n4. AUTO COMBO: Casts configured spells based on mana, monsters count and target.\n\n5. WALK ACTION: Robot walks through map prints. Clicks use human-like DX injection (double tap).",
            "ES": "------ Misteremio Bot TIPS ------\n\n1. CALIBRATE: Clic para mapear. Clic de nuevo para recalibrar.\n\n2. EMERGENCY STOP: Presiona PAUSE BREAK o INSERT en el teclado para desactivar todos los módulos al instante!\n\n3. AUTO SPACE: Pulsa ESPACIO hasta apuntar a un enemigo (fondo rojo en Battle Zone).\n\n4. AUTO COMBO: Lanza hechizos si la mana, los monstruos y el objetivo coinciden.\n\n5. WALK ACTION: Robot camina por los marcadores. Clic usa Inyección Humana DX (double tap).",
            "PL": "------ Misteremio Bot TIPS ------\n\n1. CALIBRATE: Kliknij, aby zmapować strefy. Kliknij ponownie, aby przekalibrować.\n\n2. EMERGENCY STOP: Naciśnij PAUSE BREAK lub INSERT na klawiaturze, aby natychmiast wyłączyć wszystkie moduły!\n\n3. AUTO SPACE: Spamuje spację, aż namierzy wroga (czerwone tło w strefie walki).\n\n4. AUTO COMBO: Rzuca czary w oparciu o mane, liczbę potworów i cel.\n\n5. WALK ACTION: Bot chodzi po znacznikach. Kliknięcia używają injekcji DX (double tap)."
        }
        
        for lang in langs:
            tabview.add(lang)
            txt = ctk.CTkTextbox(tabview.tab(lang), wrap="word", fg_color="black", text_color="white", font=ctk.CTkFont(size=12))
            txt.pack(fill="both", expand=True, padx=5, pady=5)
            txt.insert("0.0", texts[lang])
            txt.configure(state="disabled")

    def setup_walker_controls(self):
        pass

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

    def close_app(self):
        self.bot_core.stop()
        self.destroy()

    def restart_app(self):
        import sys
        self.bot_core.stop()
        self.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def toggle_maximize(self):
        if self.winfo_width() == self.winfo_screenwidth():
            # Restaurar tamanho normal
            self.geometry("450x550")
        else:
            # Maximizar
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            self.geometry(f"{w}x{h}+0+0")

    def minimize_app(self):
        # Em janelas com overrideredirect(True), o minimize (.iconify()) pode sumir com o app ou bugar
        # A forma mais estável no Windows é devolver o controle as bordas brevemente, minimizar, e reativar quando focar
        self.overrideredirect(False)
        self.iconify()
        self.bind("<Map>", self._on_deiconify)

    def _on_deiconify(self, event):
        self.unbind("<Map>")
        self.overrideredirect(True)
        self.set_appwindow()

    def set_appwindow(self):
        """Usa a ponte do Windows para injetar o flag AppWindow e desenhar o ícone na Taskbar!"""
        try:
            import ctypes
            from ctypes import wintypes
            
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            
            # Pega o ponteiro C nativo da janela customTkinter
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            
            # Remove o flag de feramenta e injeta o flag de App Normal
            style = style & ~WS_EX_TOOLWINDOW
            style = style | WS_EX_APPWINDOW
            
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            
            # Avisa o windows das mudanças visuais
            self.wm_withdraw()
            self.wm_deiconify()
        except Exception as e:
            print("Não foi possível forçar na taskbar:", e)

