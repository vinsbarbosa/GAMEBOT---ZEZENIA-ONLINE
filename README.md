# 🤖 Misteremio Bot — Zezenia Online Automation Bot

> A modular, open-source Python bot for **Zezenia Online** with a GUI, visual overlay, and human-like input simulation via DirectInput.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🗂️ Table of Contents

- [What it does](#-what-it-does)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [How to Customize](#-how-to-customize)
- [Module Reference](#-module-reference)
- [FAQ](#-faq)
- [Disclaimer](#️-disclaimer)

---

## ✨ What it does

Misteremio Bot automates repetitive tasks in Zezenia Online. Every feature is a toggle — you can turn them on/off independently at runtime.

| Module | What it does |
|---|---|
| **Auto Walk** | Follows a waypoint route on the minimap using image template matching |
| **Auto Space** | Detects monsters in the Battle List by HP bar color and presses `Space` to target them |
| **Auto Heal** | Reads your HP bar percentage and triggers a heal hotkey when HP drops below a threshold |
| **Auto Mana** | Same as Auto Heal, but for your Mana bar |
| **Auto Combo** | Fires configured skills/spells on a cooldown, with conditions (monster count, mana %, target lock) |
| **Auto Loot** | After each walking step, `Shift+Right-clicks` all 8 surrounding tiles to collect loot |

---

## 📁 Project Structure

```
Misteremio Bot/
│
├── main.py                  # App entry point — launches the GUI
├── run.bat                  # Windows launcher (requests Admin privileges automatically)
├── requirements.txt         # Python dependencies
├── config.json              # Auto-generated at runtime: stores calibrated zones & hotkey rules
│
├── modules/                 # All bot logic lives here (one file = one responsibility)
│   ├── bot_core.py          # 🧠 Main bot engine: orchestrates all modules in a background thread
│   ├── vision.py            # 👁️  Screen capture, template matching, bar % reading, enemy detection
│   ├── actions.py           # 🖱️  Mouse & keyboard input (DirectInput, human-like movement)
│   ├── ui.py                # 🖥️  Main GUI window (CustomTkinter)
│   ├── config_ui.py         # ⚙️  Config popup: healers, combos, mouse speed
│   ├── overlay.py           # 🎯 Transparent overlay that draws markers on screen
│   ├── region_selector.py   # 🔲 Click-and-drag screen region picker
│   └── lang.py              # 🌐 i18n system — supports PT, EN, ES, PL
│
├── prints/
│   ├── markers/             # PNG images the walker uses to find waypoints on the minimap
│   └── walkHere.png         # Template for the "Walk Here" right-click menu item
│
├── profiles/                # Saved healer/combo configurations (JSON)
└── routes/                  # Saved walker routes (JSON)
```

> **The golden rule:** each file in `modules/` has a single job. If you want to change how the bot *sees* the screen → edit `vision.py`. If you want to change how it *clicks* → edit `actions.py`. If you want to add a new UI button → edit `ui.py`.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Windows 10 or 11**
- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
- **Git** (optional, for cloning) — [git-scm.com](https://git-scm.com)

### 2. Install

```bash
git clone https://github.com/YOUR_USERNAME/Misteremio Bot.git
cd Misteremio Bot

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Run

**Always run as Administrator** — required for DirectInput to inject mouse/keyboard events into the game.

```bash
# Double-click this file or run from terminal:
run.bat
```

### 4. First-time setup inside the bot

1. Click **BATTLE ZONE** → drag a rectangle over Zezenia's Battle List panel
2. Click **HP BAR** → drag over your HP bar
3. Click **MANA BAR** → drag over your Mana bar
4. Click **MAP ZONE** → drag over the minimap *(only needed for Auto Walk)*
5. Click **CONFIG** → set up your heal hotkeys and skill combos
6. Press **PAUSE** or **INSERT** at any time for an emergency stop

> Calibrated zones are saved to `config.json` automatically — you don't need to redo this every session.

---

## 🔧 How to Customize

See the detailed guide: **[docs/CUSTOMIZATION.md](docs/CUSTOMIZATION.md)**

Quick links:
- [Change heal/mana hotkeys and thresholds](docs/CUSTOMIZATION.md#healing--mana-rules)
- [Add or modify skill combos](docs/CUSTOMIZATION.md#combo-skills)
- [Build a walking route](docs/CUSTOMIZATION.md#walking-routes)
- [Adjust monster detection sensitivity](docs/CUSTOMIZATION.md#monster-detection)
- [Change mouse speed](docs/CUSTOMIZATION.md#mouse-speed)
- [Add a new bot module](docs/CUSTOMIZATION.md#adding-a-new-module)

---

## 📖 Module Reference

See **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for a full breakdown of every module, how data flows between them, and what to edit for each use case.

---

## ❓ FAQ

**Q: The bot clicks in the wrong place / misses targets.**
> Re-calibrate your screen regions. If you changed your game window size or monitor resolution, the saved coordinates in `config.json` will be wrong. Delete `config.json` and calibrate again.

**Q: The bot doesn't react to monsters.**
> Make sure the **BATTLE ZONE** is calibrated to cover Zezenia's battle list panel exactly. The detection is color-based (HP bar orange/red/gold tone). Run `calibrate_battle.py` for a visual debug.

**Q: Auto Walk isn't working.**
> You need marker images in `prints/markers/`. Each waypoint in your route must correspond to a PNG screenshot of a unique landmark visible on your minimap.

**Q: I get a `pydirectinput` error.**
> Run as Administrator. DirectInput requires elevated privileges.

**Q: Can I run this on Linux/Mac?**
> No. It uses Win32 API (`win32gui`, `pydirectinput`) and DirectInput, which are Windows-exclusive.

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. Using bots may violate Zezenia Online's Terms of Service and could result in a ban. Use at your own risk. The author is not responsible for any consequences.

---

## 📄 License

MIT License — free to use, modify, and distribute. See [LICENSE](LICENSE).

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
