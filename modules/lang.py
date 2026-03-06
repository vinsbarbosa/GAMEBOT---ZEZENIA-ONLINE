import json
import os

DEFAULT_LANG = "EN"
LANGUAGES = ["PT", "EN", "ES", "PL"]

TRANSLATIONS = {
    "PT": {
        "CALIBRATE": "CALIBRAR",
        "MAP_ZONE": "ZONA MAPA",
        "BATTLE_ZONE": "ZONA BATTLE",
        "HP_BAR": "BARRA HP",
        "MANA_BAR": "BARRA MANA",
        "WALK_ACTION": "ROTA",
        "AUTO_WALK": "auto walk",
        "AUTO_HEAL": "auto heal",
        "AUTO_MANA": "auto mana",
        "AUTO_COMBO": "auto combo",
        "AUTO_SPACE": "auto space",
        "CONFIG": "CONFIG",
        "ALWAYS_ON_TOP": "FIXAR TELA",
        "ON": "ON",
        "OFF": "OFF",
        "CALIBRATED": "CALIBRADO",
        "MODULES": "MÓDULOS",
        "SAVE": "SALVAR",
        "SAVE_PROFILE": "SALVAR PERFIL",
        "LOAD_PROFILE": "CARREGAR PERFIL",
        "HELP": "AJUDA",
        "LANG": "PT-BR",
        "LOG": "HISTÓRICO",
        "TIME_RUNNING": "TEMPO RODANDO:",
        "SAVE_ROUTE": "SALVAR ROTA",
        "LOAD_ROUTE": "CARREGAR ROTA",
        "SHOW_LOG": "MOSTRAR LOG",
        "HIDE_LOG": "OCULTAR LOG",
        "AUTO_LOOT": "auto loot",
        "LOOT_ZONE": "ZONA LOOT"
    },
    "EN": {
        "CALIBRATE": "CALIBRATE",
        "MAP_ZONE": "MAP ZONE",
        "BATTLE_ZONE": "BATTLE ZONE",
        "HP_BAR": "HP BAR",
        "MANA_BAR": "MANA BAR",
        "WALK_ACTION": "WALK ROUTE",
        "AUTO_WALK": "auto walk",
        "AUTO_HEAL": "auto heal",
        "AUTO_MANA": "auto mana",
        "AUTO_COMBO": "auto combo",
        "AUTO_SPACE": "auto space",
        "CONFIG": "CONFIG",
        "ALWAYS_ON_TOP": "ALWAYS ON TOP",
        "ON": "ON",
        "OFF": "OFF",
        "CALIBRATED": "CALIBRATED",
        "MODULES": "MODULES",
        "SAVE": "SAVE",
        "SAVE_PROFILE": "SAVE PROFILE",
        "LOAD_PROFILE": "LOAD PROFILE",
        "HELP": "HELP",
        "LANG": "EN-US",
        "LOG": "LOG",
        "TIME_RUNNING": "TIME RUNNING:",
        "SAVE_ROUTE": "SAVE ROUTE",
        "LOAD_ROUTE": "LOAD ROUTE",
        "SHOW_LOG": "SHOW LOG",
        "HIDE_LOG": "HIDE LOG",
        "AUTO_LOOT": "auto loot",
        "LOOT_ZONE": "LOOT ZONE"
    },
    "ES": {
        "CALIBRATE": "CALIBRAR",
        "MAP_ZONE": "ZONA MAPA",
        "BATTLE_ZONE": "ZONA BATALLA",
        "HP_BAR": "BARRA HP",
        "MANA_BAR": "BARRA MANA",
        "WALK_ACTION": "RUTA",
        "AUTO_WALK": "auto pasear",
        "AUTO_HEAL": "auto curar",
        "AUTO_MANA": "auto mana",
        "AUTO_COMBO": "auto combo",
        "AUTO_SPACE": "auto space",
        "CONFIG": "AJUSTES",
        "ALWAYS_ON_TOP": "SIMPRE VISIBLE",
        "ON": "ON",
        "OFF": "OFF",
        "CALIBRATED": "CALIBRADO",
        "MODULES": "MÓDULOS",
        "SAVE": "GUARDAR",
        "SAVE_PROFILE": "GUARDAR PERFIL",
        "LOAD_PROFILE": "CARGAR PERFIL",
        "HELP": "AYUDA",
        "LANG": "ES-ES",
        "LOG": "REGISTRO",
        "TIME_RUNNING": "TIEMPO:",
        "SAVE_ROUTE": "GUARDAR RUTA",
        "LOAD_ROUTE": "CARGAR RUTA",
        "SHOW_LOG": "MOSTRAR LOG",
        "HIDE_LOG": "OCULTAR LOG",
        "AUTO_LOOT": "auto loot",
        "LOOT_ZONE": "ZONA LOOT"
    },
    "PL": {
        "CALIBRATE": "KALIBRUJ",
        "MAP_ZONE": "STREFA MAPY",
        "BATTLE_ZONE": "STREFA WALKI",
        "HP_BAR": "PASEK HP",
        "MANA_BAR": "PASEK MANY",
        "WALK_ACTION": "TRASA",
        "AUTO_WALK": "auto walk",
        "AUTO_HEAL": "auto heal",
        "AUTO_MANA": "auto mana",
        "AUTO_COMBO": "auto combo",
        "AUTO_SPACE": "auto space",
        "CONFIG": "OPCJE",
        "ALWAYS_ON_TOP": "NA GÓRZE",
        "ON": "WŁ",
        "OFF": "WYŁ",
        "CALIBRATED": "GOTOWE",
        "MODULES": "MODUŁY",
        "SAVE": "ZAPISZ",
        "SAVE_PROFILE": "ZAPISZ PROFIL",
        "LOAD_PROFILE": "WCZYTAJ PROFIL",
        "HELP": "POMOC",
        "LANG": "PL",
        "LOG": "ZDARZENIA",
        "TIME_RUNNING": "CZAS:",
        "SAVE_ROUTE": "ZAPISZ TRASĘ",
        "LOAD_ROUTE": "WCZYTAJ TRASĘ",
        "SHOW_LOG": "POKAŻ LOG",
        "HIDE_LOG": "UKRYJ LOG",
        "AUTO_LOOT": "auto loot",
        "LOOT_ZONE": "STREFA LOOTU"
    }
}

class T:
    current_lang = "EN"
    
    @classmethod
    def load(cls):
        if os.path.exists("lang.txt"):
            with open("lang.txt", "r") as f:
                cls.current_lang = f.read().strip()
                if cls.current_lang not in LANGUAGES:
                    cls.current_lang = DEFAULT_LANG
                    
    @classmethod
    def save(cls):
        with open("lang.txt", "w") as f:
            f.write(cls.current_lang)
            
    @classmethod
    def cycle(cls):
        idx = LANGUAGES.index(cls.current_lang)
        cls.current_lang = LANGUAGES[(idx + 1) % len(LANGUAGES)]
        cls.save()

    @classmethod
    def get(cls, key):
        return TRANSLATIONS[cls.current_lang].get(key, key)
