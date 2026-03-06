# 🏗️ Architecture Reference

A deep-dive into how Misteremio Bot is structured internally — useful if you want to understand the data flow, extend the bot, or debug a specific behavior.

---

## Overview

```
┌─────────────┐     callbacks      ┌──────────────┐
│   ui.py     │ ◄────────────────► │  bot_core.py │
│  (GUI/UX)   │                    │   (Engine)   │
└─────────────┘                    └──────┬───────┘
                                          │ uses
                              ┌───────────┼───────────┐
                              ▼           ▼           ▼
                         vision.py   actions.py   config.json
                         (See)       (Act)        (State)
```

The bot has a clean **separation of concerns**:
- `ui.py` only knows about buttons and labels — it never directly reads the screen or presses keys
- `bot_core.py` is the brain — it reads from `vision.py` and acts through `actions.py`
- `vision.py` and `actions.py` are stateless utilities — they do one thing each

---

## Module Breakdown

### `main.py` — Entry Point

**Size:** ~25 lines  
**Role:** Initializes DPI awareness, creates the `MainWindow`, and starts the Tkinter event loop.

```python
ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Critical for multi-monitor / scaled displays
app = MainWindow()
app.mainloop()
```

> **When to edit:** Almost never. Only if you need to add startup checks or change DPI handling.

---

### `modules/bot_core.py` — The Brain

**Role:** Runs the bot loop in a **background thread**, orchestrating all modules.

**Key attributes:**
```python
self.vision          # Vision instance (screen reading)
self.actions         # Actions instance (input simulation)
self.running         # bool — controls the main loop
self.auto_walk_enabled
self.auto_heal_enabled
self.auto_mana_enabled
self.auto_combo_enabled
self.auto_space_enabled
self.auto_loot_enabled
self.hp_percent      # Current HP % (0-100)
self.mana_percent    # Current Mana % (0-100)
self.monster_count   # Current enemies in battle list
self.target_locked   # bool — is an enemy targeted?
```

**Main loop flow (every ~100ms):**
```
1. _check_stats()    → reads HP/Mana bars, triggers healers
2. _check_combos()   → fires skill hotkeys if conditions are met
3. _check_battle_state() → detects enemies, fires Auto Space
4. (if walking) → find marker on minimap → click → wait → loot
```

**Callbacks to UI (thread-safe):**
```python
self.ui_callback(text, color)       # Append a line to the log box
self.visual_callback(x, y, color)   # Draw a temporary marker via overlay
self.stats_callback(hp, mana)       # Update HP/Mana % labels in GUI
```

> **When to edit:** When adding new bot behaviors, new state tracking, or new automation logic.

---

### `modules/vision.py` — The Eyes

**Role:** Everything that involves **reading** the screen.

| Method | What it does |
|---|---|
| `get_screen_capture(region)` | Takes a screenshot of a screen region using `mss`. Returns a BGR numpy array. |
| `find_image(path, screen, threshold)` | Template matching — finds one image inside another. Returns `(x, y, confidence)` or `None`. |
| `find_all_images(path, screen, threshold)` | Like above, but returns all matches (used for counting). |
| `find_color(screen, color_name)` | Finds all blobs of a named color (red, green, blue, etc.) via HSV masking. |
| `count_battle_enemies(img)` | Detects monster count and target lock from the Battle List image. Returns `(count, target_locked)`. |
| `get_bar_percentage(img)` | Reads an HP or Mana bar image and returns its fill percentage (0-100). |

**How `count_battle_enemies` works:**

```
1. Apply color mask: pixels where R > 140 AND B < 90 (catches gold/orange/red HP bars)
2. For each row, check if there's a horizontal run of ≥ 5 masked pixels (confirms it's a real bar)
3. Count vertical blocks of "active" rows → each block = 1 monster
4. Check left edge of image (cols 1–36) for dark red background → target_locked = True if > 40% red
```

> **When to edit:** If monster detection is inaccurate, if you want to detect new UI elements, or if Zezenia changes its UI colors.

---

### `modules/actions.py` — The Hands

**Role:** All **output** — mouse movement, mouse clicks, key presses.

Uses `pydirectinput` (DirectInput injection) instead of `pyautogui` because Zezenia uses DirectX and doesn't respond to standard Win32 `SendInput` in some cases.

| Method | What it does |
|---|---|
| `move_mouse(x, y)` | Instantly moves the mouse to absolute screen coordinates |
| `click_mouse(x, y, button)` | Smooth animated move → triple-click (ensures hit registration) |
| `walk_click(x, y, vision)` | Special walk routine: move → double left click → right click → find "Walk Here" → click it |
| `press_key(key)` | Holds a key for 150ms (ensures 100% hit rate on server tick) |
| `perform_loot(region)` | Holds `Shift`, then right-clicks all 8 surrounding tiles in the loot region |

**Human-like movement implementation:**
```python
# Interpolates from current cursor position to target in 15 steps
for i in range(1, steps + 1):
    cur_x = int(start_x + (x - start_x) * (i / steps))
    cur_y = int(start_y + (y - start_y) * (i / steps))
    pydirectinput.moveTo(cur_x, cur_y)
    time.sleep(0.01 / Actions.mouse_speed)
```

> **When to edit:** If click timing needs adjustment, if you want faster/slower movement, or if you need to add new interaction types (e.g., drag).

---

### `modules/ui.py` — The Face

**Role:** The main application window. Built with **CustomTkinter** (dark themed, frameless).

**Key design decisions:**
- Window has no native title bar (`overrideredirect(True)`) — the custom title bar inside the window handles dragging
- All bot state changes go through `bot_core` attributes — the UI never runs its own logic
- All UI updates from the bot thread use `self.after(0, ...)` to be thread-safe with Tkinter

**Window sections (top to bottom):**
```
[Custom title bar]  ← draggable, has close button
[CALIBRATE]         ← region calibration buttons
[TOGGLES]           ← module on/off buttons
[AUTO SPACE]        ← full-width space toggle
[CONFIG + ON TOP]   ← utility buttons
[Logo + Lang + Restart]
[Log box]           ← scrolling activity log
```

> **When to edit:** To add new toggle buttons, change the layout, or add new calibration zones.

---

### `modules/config_ui.py` — The Settings Panel

**Role:** A popup window for managing healers, combos, mouse speed, and route loading.

Reads from and writes to `config.json` directly. Also calls `bot_core.load_config()` after saving to apply changes without a restart.

> **When to edit:** To add new config sections (e.g. a new type of rule or parameter).

---

### `modules/overlay.py` — The Visor

**Role:** A transparent, click-through window that draws colored markers on screen to visualize what the bot is doing.

When the bot finds a waypoint marker, it calls:
```python
self.visual_callback(tx, ty, "red", order_num=step_number)
```
...which triggers the overlay to draw a temporary dot at that location on screen.

> **When to edit:** To change overlay appearance, color coding, or add new visual feedback types.

---

### `modules/region_selector.py` — The Zone Picker

**Role:** A full-screen transparent window. Click and drag to select a screen region. The selected region `{top, left, width, height}` is passed back via a callback.

Used by all calibration buttons in the main UI.

> **When to edit:** Rarely. Only if you want to change the selection UX (e.g. add a preview or snapping).

---

### `modules/lang.py` — The Translator

**Role:** A static key-value i18n system. No external files — all translations are hardcoded in the dictionary.

```python
T.load()          # Reads 'lang.txt' to find saved language preference
T.get("AUTO_WALK") # Returns localized string for current language
T.cycle()          # Cycles to next language and saves preference
```

> **When to edit:** To add a new language or new UI string key. See [CUSTOMIZATION.md → Language](CUSTOMIZATION.md#language--ui-text).

---

## Data Flow Diagram

```
Screen (game)
     │
     │ mss screenshot
     ▼
vision.py
  ├── get_bar_percentage() → hp_percent, mana_percent
  ├── count_battle_enemies() → monster_count, target_locked
  └── find_image() → waypoint position (x, y)
     │
     │ data fed into
     ▼
bot_core.py (_bot_loop thread)
  ├── _check_stats() → if hp low → actions.press_key(heal_key)
  ├── _check_combos() → if conditions met → actions.press_key(skill_key)
  ├── _check_battle_state() → if enemy, no target → actions.press_key('space')
  └── walker → if marker found → actions.walk_click(x, y)
                                         │
                                         │ DirectInput
                                         ▼
                                  Game window (Zezenia)
```

---

## Configuration File (`config.json`)

Auto-generated at runtime. Structure:

```json
{
  "healers": [ ... ],        // Heal/mana rules
  "combos": [ ... ],         // Skill combo rules
  "mouse_speed": 1.7,        // Click speed multiplier
  "battle_region": { ... },  // Calibrated battle list zone
  "map_region": { ... },     // Calibrated minimap zone
  "hp_region": { ... },      // Calibrated HP bar zone
  "mana_region": { ... },    // Calibrated mana bar zone
  "loot_region": { ... }     // Calibrated loot zone
}
```

Each region object:
```json
{
  "top": 55,
  "left": 6,
  "width": 209,
  "height": 319
}
```

> **Important:** These coordinates are **absolute screen pixel positions**. If you move the game window, resize it, or change monitor resolution, you need to recalibrate.

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

