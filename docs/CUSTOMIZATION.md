# 🔧 Customization Guide

This guide explains **exactly what to change and where** for the most common modifications. No deep Python knowledge required for most of these.

---

## Table of Contents

- [Healing & Mana Rules](#healing--mana-rules)
- [Combo Skills](#combo-skills)
- [Walking Routes](#walking-routes)
- [Monster Detection](#monster-detection)
- [Mouse Speed](#mouse-speed)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Language / UI Text](#language--ui-text)
- [Adding a New Module](#adding-a-new-module)

---

## Healing & Mana Rules

Heal and mana rules are stored in `config.json` under the `"healers"` array.

### Example `config.json` healers section:
```json
"healers": [
  {
    "name": "HEALER",
    "perc": "60%",
    "key": "3"
  },
  {
    "name": "MANA HEAL",
    "perc": "80%",
    "key": "1"
  }
]
```

### Rules:
| Field | What it does | Example |
|---|---|---|
| `"name"` | Label shown in the UI. **If it contains "MANA" or "MP", it's treated as a mana rule.** Otherwise it's an HP rule. | `"HEALER"`, `"MANA RESTORE"` |
| `"perc"` | Trigger threshold — the hotkey fires when HP/Mana **drops to or below** this % | `"60%"` or `60` |
| `"key"` | The keyboard key to press | `"f1"`, `"3"`, `"space"` |

### Where to edit:
- **In the GUI:** Click **CONFIG** → **Healers** tab → add/edit rules there
- **Directly in file:** Edit `config.json` with any text editor (Notepad works fine)

> To add a second heal spell, just add another object to the `"healers"` array.

---

## Combo Skills

Combos are entries in the `"combos"` array in `config.json`.

### Example:
```json
"combos": [
  {
    "name": "Fireball",
    "key": "f5",
    "interval": "3.0",
    "mana": "50",
    "mobs": "1",
    "cond": "Alvo",
    "on": 1
  }
]
```

### Fields:
| Field | Description | Options |
|---|---|---|
| `"name"` | Just a label for your reference | Any string |
| `"key"` | Key to press | `"f1"`–`"f12"`, `"1"`–`"9"`, `"space"`, etc. |
| `"interval"` | Minimum seconds between activations | Any number, e.g. `"2.0"` |
| `"mana"` | Only fires if your current mana % is **above** this value | `"0"` to `"100"` |
| `"mobs"` | Only fires if there are **at least** this many monsters detected | `"0"` = always, `"1"` = needs 1 mob |
| `"cond"` | Extra condition | `"Sempre"` (always) or `"Alvo"` (only when a target is locked) |
| `"on"` | Enable/disable this combo | `1` = enabled, `0` = disabled |

> **Tip:** Set `"mobs": "0"` and `"cond": "Sempre"` for buffs you want to maintain regardless of enemies (e.g. Speed, Haste).

---

## Walking Routes

A walking route is a JSON file saved in the `routes/` folder. The bot follows the waypoints in order, looping back to the start.

### How a route works:

The bot takes a screenshot of your **MAP ZONE** (minimap), then looks for the marker image at each step. When it finds it, it clicks there and walks.

### Creating a route:

1. **Take screenshots of landmarks** on your minimap at each point of your hunting path
2. Save them as PNG files in `prints/markers/` (e.g. `marker_001.png`, `marker_002.png`, ...)
3. Create a route JSON file in `routes/`:

```json
[
  { "image": "marker_001.png", "wait": 3 },
  { "image": "marker_002.png", "wait": 5 },
  { "image": "marker_003.png", "wait": 4 }
]
```

### Fields:
| Field | Description |
|---|---|
| `"image"` | Filename inside `prints/markers/` |
| `"wait"` | Seconds to wait after clicking this waypoint before moving to the next |

> **Tips for good markers:**
> - Use a small, **unique** area of the minimap — a crossroads, a building corner, a river bend
> - Avoid areas that look the same at multiple points in the map
> - The matching threshold is `0.7` (70% similarity). If the bot keeps missing a marker, try a cleaner crop

### Loading a route in the GUI:

Click **CONFIG** → **Route** tab → Browse to your JSON file → Load.

---

## Monster Detection

The bot detects monsters **purely by color** — it looks for horizontal runs of pixels with HP bar colors (gold, orange, red) in the Battle Zone area.

### Where the logic lives:
**`modules/vision.py`** → function `count_battle_enemies()`

### Tuning the detection:

```python
# Line ~172 in vision.py
# Current rule: R channel > 140 AND B channel < 90
hp_mask = (bgr_img[:,:,2] > 140) & (bgr_img[:,:,0] < 90)
```

**If the bot is detecting false positives (seeing monsters when there are none):**
- Raise the `R` threshold: change `140` to `160`
- Lower the minimum run length: find `MIN_RUN = 5` and raise it to `7` or `8`

**If the bot is missing monsters (not detecting them):**
- Lower the `R` threshold: change `140` to `120`
- Lower the `MIN_RUN` value

### Target lock detection:

The bot considers a target "locked" when it detects a red background in the avatar area of the Battle List.

```python
# Line ~226 in vision.py
# Current rule: R >= 50, G < 40, B < 40 (dark red background)
av_red = ((av[:,:,2] >= 50) & (av[:,:,1] < 40) & (av[:,:,0] < 40))

# Trigger threshold: > 40% of the avatar row must be red
target_locked = bool(np.any(row_red_frac > 0.40))
```

**Change `0.40` to a lower value** (e.g. `0.25`) if the bot is not recognizing locked targets.
**Raise it** (e.g. `0.55`) to make it less sensitive.

> 🛠️ To visually debug what the bot is seeing, run `calibrate_battle.py` — it shows a live view of the detection in real time.

---

## Mouse Speed

Mouse speed is a multiplier stored in `config.json`:

```json
"mouse_speed": 1.7
```

| Value | Effect |
|---|---|
| `1.0` | Default speed |
| `0.5` | Slower, more human-like |
| `2.0` | Faster, more aggressive |

You can also change it from the GUI: **CONFIG** → **Mouse Speed** slider.

> Internally, this value divides sleep times in `actions.py`. A higher value = less sleep = faster movement.

---

## Keyboard Shortcuts

Global hotkeys are registered in **`modules/ui.py`**, inside `__init__()`:

```python
# Line ~53 in ui.py
keyboard.add_hotkey('pause', lambda: self.after(0, self.disable_all_modules_ui))
keyboard.add_hotkey('insert', lambda: self.after(0, self.disable_all_modules_ui))
```

**To change the emergency stop key**, replace `'pause'` or `'insert'` with any key name from the [keyboard library docs](https://github.com/boppreh/keyboard#api).

Examples: `'f12'`, `'ctrl+shift+s'`, `'home'`

---

## Language / UI Text

All UI strings are in **`modules/lang.py`** in the `TRANSLATIONS` dictionary.

Currently supported languages: `PT` (Portuguese), `EN` (English), `ES` (Spanish), `PL` (Polish).

### To add a new language (e.g. French):

1. Open `modules/lang.py`
2. Add `"FR"` to the `LANGUAGES` list:
   ```python
   LANGUAGES = ["PT", "EN", "ES", "PL", "FR"]
   ```
3. Add a new dictionary entry under `TRANSLATIONS`:
   ```python
   "FR": {
       "CALIBRATE": "CALIBRER",
       "MAP_ZONE": "ZONE CARTE",
       "BATTLE_ZONE": "ZONE COMBAT",
       "HP_BAR": "BARRE HP",
       "MANA_BAR": "BARRE MANA",
       "AUTO_WALK": "auto marche",
       "AUTO_HEAL": "auto soin",
       "AUTO_MANA": "auto mana",
       "AUTO_COMBO": "auto combo",
       "AUTO_SPACE": "auto space",
       "AUTO_LOOT": "auto butin",
       "LOOT_ZONE": "ZONE BUTIN",
       "CONFIG": "CONFIG",
       "ALWAYS_ON_TOP": "TOUJOURS VISIBLE",
       "ON": "ON",
       "OFF": "OFF",
       "SAVE": "SAUVEGARDER",
       "LANG": "FR",
       # ... copy all keys from the EN block and translate them
   }
   ```

---

## Adding a New Module

The bot is designed to be modular. Here's the pattern to follow if you want to add a new automation (e.g. "Auto Drink Potion"):

### Step 1 — Add the state flag in `bot_core.py`

```python
# In BotCore.__init__()
self.auto_potion_enabled = False
```

### Step 2 — Add the logic in `bot_core.py`

```python
def _check_potion(self):
    """Drinks a potion when HP is below 30%."""
    if not self.auto_potion_enabled:
        return
    if self.hp_percent <= 30:
        self._trigger_hotkey('f6', cooldown=2.0)
```

Then call it inside `_bot_loop()`:
```python
self._check_potion()
```

### Step 3 — Add the UI toggle in `ui.py`

```python
# In MainWindow.__init__()
self.btn_auto_potion = self._create_toggle_btn(
    grid_frame,
    "auto potion: OFF",
    cmd=self.toggle_auto_potion
)

# Add the toggle method:
def toggle_auto_potion(self):
    self.bot_core.auto_potion_enabled = not self.bot_core.auto_potion_enabled
    state = self.bot_core.auto_potion_enabled
    if state:
        self.btn_auto_potion.configure(text="auto potion: ON", fg_color="#58d68d", text_color="black")
    else:
        self.btn_auto_potion.configure(text="auto potion: OFF", fg_color="#e74c3c", text_color="white")
```

### Step 4 — Make sure `disable_all_modules_ui()` turns it off too

```python
def disable_all_modules_ui(self):
    # ... existing code ...
    self.bot_core.auto_potion_enabled = False
    self.btn_auto_potion.configure(text="auto potion: OFF", fg_color="#e74c3c", text_color="white")
```

That's it. The module is fully integrated.

---

```
  ·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·
  X                                                     X
  ·   _ __ ___ (X)___| |_ ___ _ __ ___ _ __ ___ (X) ___  ·
  X  | '_ ` _ \|X/ __| __/ _ \X'X_/ _ \ '_ ` _ \|X|/ _ \ X
  ·  | | | | | |X\__ \ ||  __/X| |  __/ | | | | |X| (X) | ·
  X  |_| |_| |_|X|___/\__\___|X|  \___|_| |_| |_|X|\___/  X
  ·                                                     ·
  ·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·X·
```
