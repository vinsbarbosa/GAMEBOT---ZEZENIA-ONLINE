import json
import os
from modules.vision import Vision
from modules.actions import Actions
import time
import threading

class BotCore:
    def __init__(self, ui_callback=None, visual_callback=None, stats_callback=None):
        self.running = False
        self.ui_callback = ui_callback
        self.visual_callback = visual_callback
        self.stats_callback = stats_callback
        self.thread = None
        
        # Módulos
        self.vision = Vision()
        self.actions = Actions()
        
        self.walker_sequence = []
        self.map_region = None
        self.battle_region = None
        self.hp_region = None
        self.mana_region = None
        self.loot_region = None
        
        # State de Módulos
        self.auto_walk_enabled = False
        self.auto_heal_enabled = False
        self.auto_mana_enabled = False
        self.auto_combo_enabled = False
        self.auto_space_enabled = False
        self.auto_loot_enabled = False
        
        # Stats iniciais
        self.hp_percent = 100
        self.mana_percent = 100
        self.monster_count = 0
        
        # Configs
        self.healers_config = []
        self.combos_config = []
        self.last_casts = {}
        
    def disable_all_modules(self):
        self.auto_walk_enabled = False
        self.auto_heal_enabled = False
        self.auto_mana_enabled = False
        self.auto_combo_enabled = False
        self.auto_space_enabled = False
        self.auto_loot_enabled = False
        
        # Reseta os status visuais (Mas mantem a configuracao intacta na re-ativacao)
        self.hp_percent = 100
        self.mana_percent = 100
        self.monster_count = 0

    def load_config(self):
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    data = json.load(f)
                    self.healers_config = data.get("healers", [])
                    self.combos_config  = data.get("combos", [])
                    # Regioes calibradas: carrega automaticamente para nao precisar recalibrar a cada sessao
                    if data.get("battle_region") and not self.battle_region:
                        self.battle_region = data["battle_region"]
                        print(f"[Config] battle_region carregada: {self.battle_region['width']}x{self.battle_region['height']}")
                    if data.get("map_region") and not self.map_region:
                        self.map_region = data["map_region"]
                    if data.get("hp_region") and not self.hp_region:
                        self.hp_region = data["hp_region"]
                    if data.get("mana_region") and not self.mana_region:
                        self.mana_region = data["mana_region"]
                    if data.get("loot_region") and not self.loot_region:
                        self.loot_region = data["loot_region"]
            except Exception as e:
                print(f"Erro ao carregar config: {e}")


    def log(self, text, color="#00ff00"):
        if self.ui_callback:
            self.ui_callback(text, color)

    def start(self):
        if not self.running:
            self.load_config()
            self.running = True
            self.start_time = time.time()
            self.thread = threading.Thread(target=self._bot_loop, daemon=True)
            self.thread.start()
            
    def stop(self):
        self.running = False

    def _bot_loop(self):
        self.log("Engine de captura iniciada.", "cyan")
        
        current_step_idx = 0
        self.last_battle_state = "UNKNOWN"
        self.last_attack_time = 0
        self.last_stats_check = 0
        
        while self.running:
            now = time.time()
            
            # 0. Check Stats e Healers
            if now - self.last_stats_check > 0.1: 
                self._check_stats()
                self._check_combos()
                self.last_stats_check = now

            # 1. Checar Walker (Processo bloqueante parcial, mas com checagem interna)
            if self.auto_walk_enabled and self.walker_sequence and self.map_region:
                # ... (Lógica do walker mantida)
                step = self.walker_sequence[current_step_idx % len(self.walker_sequence)]
                marker_img = step.get("image")
                wait_time = step["wait"]() if callable(step["wait"]) else int(step["wait"])
                order_num = (current_step_idx % len(self.walker_sequence)) + 1
                
                img = self.vision.get_screen_capture(region=self.map_region)
                if img is not None:
                    points = self.vision.find_image(f"prints/markers/{marker_img}", img, threshold=0.7)
                    if points:
                        rel_tx, rel_ty, _ = points
                        tx = rel_tx + self.map_region['left']
                        ty = rel_ty + self.map_region['top']
                        if self.visual_callback:
                            self.visual_callback(tx, ty, "red", order_num=order_num)
                        
                        # --- MODULO FAST AUTO-LOOT ---
                        if self.auto_loot_enabled and self.loot_region:
                            self.log(f"Coletando Loot...", "#3498db")
                            self.actions.perform_loot(self.loot_region)
                        # -----------------------------

                        self.log(f"Walk Menu em Marcador {order_num}", "cyan")
                        self.actions.walk_click(tx, ty, vision=self.vision)
                        
                        # Loop de caminhada checando batalha E status
                        for _ in range(int(wait_time * 5)):
                            if not self.running: break
                            self._check_stats()
                            self._check_battle_state()
                            self._check_combos()
                            time.sleep(0.2)
                        
                        current_step_idx += 1 
                    else:
                        time.sleep(0.2)
            
            # 2. Battle State (Roda sempre que não estiver ocupado no loop do walker)
            self._check_battle_state()
            
            time.sleep(0.1) # Loop mais rápido para maior precisão
            
        self.log("Bot Loop encerrado.", "red")

    def _check_battle_state(self):
        """
        Detecta monstros e alvo na Battle List usando EXCLUSIVAMENTE cor.
        
        - Contagem de monstros: barras de HP (dourado/laranja/vermelho) na imagem
        - Target locked: fundo vermelho na zona do icone (>25% da area)
        
        Funciona com QUALQUER monstro sem necessidade de calibrar templates.
        """
        if not self.battle_region: return
        
        b_img = self.vision.get_screen_capture(region=self.battle_region)
        if b_img is None: return
        
        monster_count, target_locked = self.vision.count_battle_enemies(b_img)
        
        self.monster_count = monster_count
        self.target_locked = target_locked
        
        state = "NO ENEMIES"
        if target_locked:
            state = "ALVO MARCADO"
        elif monster_count > 0:
            state = "ENEMY DETECTED"
            
        # Loga mudancas de estado
        if state != self.last_battle_state or (state == "ENEMY DETECTED" and monster_count != getattr(self, 'last_monster_count', 0)):
            self.log(f"{state} ({monster_count} mobs)", "orange" if monster_count > 0 else "gray")
            self.last_battle_state = state
            self.last_monster_count = monster_count
            
            if self.visual_callback:
                bx = self.battle_region['left'] + 50
                by = self.battle_region['top'] + 10
                self.visual_callback(bx, by, "cyan", order_num=f"Mobs: {monster_count}")
            
        # AutoSpace: pressiona Space se ha monstros mas nenhum alvo selecionado ainda
        if self.auto_space_enabled and state == "ENEMY DETECTED" and not target_locked:
            curr_time = time.time()
            if curr_time - self.last_attack_time >= 1.0:
                self.actions.press_key('space')
                self.last_attack_time = curr_time





    def _check_stats(self):
        """Monitora HP e MANA a partir das zonas calibradas."""
        updated = False
        if self.hp_region:
            hp_img = self.vision.get_screen_capture(region=self.hp_region)
            new_hp = self.vision.get_bar_percentage(hp_img)
            if new_hp != self.hp_percent:
                self.hp_percent = new_hp
                updated = True
                
        if self.mana_region:
            mana_img = self.vision.get_screen_capture(region=self.mana_region)
            new_mana = self.vision.get_bar_percentage(mana_img)
            if new_mana != self.mana_percent:
                self.mana_percent = new_mana
                updated = True
                
        if updated and self.stats_callback:
            self.stats_callback(self.hp_percent, self.mana_percent)
            
        # --- Lógica de cura automática ---
        if self.auto_heal_enabled or self.auto_mana_enabled:
            for rule in self.healers_config:
                name = rule.get("name", "").upper()
                try:
                    trigger_perc = int(str(rule.get("perc", "80")).replace("%", ""))
                except:
                    trigger_perc = 80
                    
                key = str(rule.get("key", "f1")).lower()
                
                # Se NO NOME contiver MANA ou MP, é regra de mana. Senão, é Vida.
                is_mana = "MANA" in name or "MP" in name
                
                # Regras de cura (HP)
                if self.auto_heal_enabled and not is_mana:
                    if self.hp_percent <= trigger_perc:
                        self.log(f"HP ({self.hp_percent}%) <= Trigger ({trigger_perc}%) -> Apertando [{key.upper()}]", "#32cd32")
                        self._trigger_hotkey(key, cooldown=1.0)
                
                # Regras de mana
                if self.auto_mana_enabled and is_mana:
                    if self.mana_percent <= trigger_perc:
                        self.log(f"MANA ({self.mana_percent}%) <= Trigger ({trigger_perc}%) -> Apertando [{key.upper()}]", "#1e90ff")
                        self._trigger_hotkey(key, cooldown=1.0)

    def _check_combos(self):
        """Executa os combos configurados"""
        if not self.auto_combo_enabled: return
        
        for combo in self.combos_config:
            if not combo.get("on", True): continue
            
            try:
                min_mobs = int(combo.get("mobs", "1"))
                mana_min = int(combo.get("mana", "0"))
                interval = float(combo.get("interval", "2.0"))
                key = combo.get("key", "f5").lower()
                cond = combo.get("cond", "Sempre")
                
                # Validação de condições
                if self.monster_count < min_mobs: continue
                if self.mana_percent < mana_min: continue
                
                if cond == "Alvo" and not getattr(self, 'target_locked', False): continue
                
                # Executa com cooldown
                self._trigger_hotkey(key, cooldown=interval)
            except:
                continue

    def _trigger_hotkey(self, key, cooldown):
        now = time.time()
        if key not in self.last_casts or (now - self.last_casts[key]) >= cooldown:
            self.actions.press_key(key)
            self.last_casts[key] = now
