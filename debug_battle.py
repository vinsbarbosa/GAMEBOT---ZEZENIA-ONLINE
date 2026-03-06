"""
debug_battle.py - Analisa em tempo real o painel de batalha capturado
Salva o screenshot e mostra os pixels para calibragem.
"""
import cv2
import numpy as np
import json
import mss
import os

# Carrega a regiao de batalha do config
battle_region = None
if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        cfg = json.load(f)
        battle_region = cfg.get("battle_region")

if not battle_region:
    print("ERRO: 'battle_region' nao encontrado no config.json")
    print("Configure a regiao de batalha no bot primeiro!")
    exit(1)

print("Regiao de batalha: {}".format(battle_region))

# Captura a tela
with mss.mss() as sct:
    sct_img = sct.grab(battle_region)
    img = np.array(sct_img)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

h, w, _ = img.shape
print("Screenshot capturado: {}x{}".format(w, h))

# Salva o screenshot para visual
cv2.imwrite("debug_battle_capture.png", img)
print("Screenshot salvo em: debug_battle_capture.png")

# Analisa linha por linha
print()
print("=== ANALISE LINHA A LINHA (col 30-50) ===")
for y in range(h):
    row_info = []
    for x in range(25, min(60, w)):
        b, g, r = img[y, x]
        is_hp = r > 150 and b < 80
        flag = " <<HP" if is_hp else ""
        row_info.append("x{}:({},{},{}){}".format(x, r, g, b, flag))
    print("  y={:3d}: {}".format(y, " | ".join(row_info)))

# Simulacao da mascara de HP
print()
print("=== SIMULACAO count_battle_enemies ===")
hp_mask = (img[:,:,2] > 150) & (img[:,:,0] < 80)
print("Total pixels HP detectados: {}".format(np.count_nonzero(hp_mask)))

# Onde estao os pixels de HP?
ys, xs = np.where(hp_mask)
if len(ys) > 0:
    print("Pixels HP em Y: {} a {}".format(ys.min(), ys.max()))
    print("Pixels HP em X: {} a {}".format(xs.min(), xs.max()))
    # Mostra por coluna
    for x in range(25, min(60, w)):
        col_hp = np.count_nonzero(hp_mask[:, x])
        if col_hp > 0:
            ys_col = np.where(hp_mask[:, x])[0]
            print("  col x={}: {} pixels HP em linhas {}".format(x, col_hp, list(ys_col[:5])))

# Verifica nas colunas 38-45
safe_s = min(38, w-1)
safe_e = min(45, w)
if safe_s < w and safe_e <= w and safe_s < safe_e:
    proj = np.any(hp_mask[:, safe_s:safe_e], axis=1)
    count = 0
    in_block = False
    for val in proj:
        if val and not in_block:
            count += 1
            in_block = True
        elif not val and in_block:
            in_block = False
    print("Monstros detectados (col {}-{}): {}".format(safe_s, safe_e, count))
else:
    print("AVISO: Imagem muito estreita para varrer col 38-45 (largura={}px)".format(w))

# Testa avatar zone para target_locked
avatar_zone = img[:, 2:min(38, w)]
av_red = (avatar_zone[:,:,2] > 60) & (avatar_zone[:,:,1] < 60) & (avatar_zone[:,:,0] < 60)
red_count = np.count_nonzero(av_red)
print("Pixels vermelhos no avatar: {} (target_locked = {})".format(red_count, red_count > 80))

print()
print("=== DIAGNOSTICO FINAL ===")
if w < 50:
    print("PROBLEMA: Painel de battle muito estreito ({}px). Precisa ter pelo menos 50px de largura!".format(w))
elif h < 25:
    print("PROBLEMA: Painel de battle muito baixo ({}px). Precisa ter pelo menos 25px de altura por monstro!".format(h))
else:
    print("Tamanho OK ({}x{})".format(w, h))
