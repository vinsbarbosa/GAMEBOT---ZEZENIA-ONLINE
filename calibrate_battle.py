"""
calibrate_battle.py
Ferramenta de calibragem automatica: captura a zona de battle configurada
e extrai os templates de icone do monstro automaticamente.

Como usar:
1. Abra o jogo com o monstro visivel na Battle List
2. Configure a battle_region no bot normalmente
3. Execute: python calibrate_battle.py
4. Digite 'n' para capturar o icone NORMAL (sera pedido o nome do monstro)
5. Selecione o monstro no jogo (clique nele), depois digite 't' para capturar o TARGET
6. Repita para cada monstro que quiser cadastrar
"""

import cv2
import numpy as np
import json
import mss
import os
import sys

# ----------------------------------------------------------------
# Carrega a regiao de batalha do config
# ----------------------------------------------------------------
if not os.path.exists("config.json"):
    print("ERRO: config.json nao encontrado. Configure o bot primeiro!")
    sys.exit(1)

with open("config.json", "r") as f:
    cfg = json.load(f)

# A battle_region pode estar salva em diferentes chaves dependendo da versao do bot
battle_region = (
    cfg.get("battle_region") or
    cfg.get("battle") or
    cfg.get("regions", {}).get("battle")
)

if not battle_region:
    print("ERRO: 'battle_region' nao encontrado no config.json.")
    print("Chaves disponiveis: {}".format(list(cfg.keys())))
    print()
    print("Configure a zona de battle no bot e salve antes de calibrar.")
    print("Ou informe manualmente abaixo:")
    try:
        left   = int(input("  left   (X inicio da battle zone): "))
        top    = int(input("  top    (Y inicio da battle zone): "))
        width  = int(input("  width  (largura da battle zone):  "))
        height = int(input("  height (altura da battle zone):   "))
        battle_region = {"left": left, "top": top, "width": width, "height": height}
        print("Usando regiao manual: {}".format(battle_region))
    except (ValueError, KeyboardInterrupt):
        print("Cancelado.")
        sys.exit(1)

print("Zona de battle: {}".format(battle_region))
print()

def capture_battle():
    """Captura a zona de battle e retorna a imagem BGR."""
    with mss.mss() as sct:
        sct_img = sct.grab(battle_region)
        img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img

def find_first_monster_row(img):
    """
    Encontra a primeira linha de monstro na battle list
    usando a mascara de HP. Retorna (y_start, y_end) da linha.
    """
    h, w = img.shape[:2]
    hp_mask = (img[:,:,2] > 140) & (img[:,:,0] < 90)

    MIN_RUN = 5
    row_has_bar = np.zeros(h, dtype=bool)
    for y in range(h):
        row = hp_mask[y, :]
        run = 0
        for val in row:
            if val:
                run += 1
                if run >= MIN_RUN:
                    row_has_bar[y] = True
                    break
            else:
                run = 0

    # Encontra o bloco da primeira barra
    start = None
    for y, has in enumerate(row_has_bar):
        if has and start is None:
            start = y
        elif not has and start is not None:
            return start, y
    return None, None

def extract_icon(img, y_end):
    """Extrai o icone do monstro (regiao do avatar: x=0..37, altura da linha)."""
    h, w = img.shape[:2]
    # A linha do monstro tem ~35px de altura, o icone ocupa os primeiros 37px horizontais
    row_h = min(y_end + 10, h)
    row_start = max(0, row_h - 35)
    icon = img[row_start:row_h, 0:37]
    return icon

def extract_full_row(img, y_bar_start, y_bar_end):
    """Extrai a linha completa do monstro para usar como template."""
    h, w = img.shape[:2]
    # Pega uma faixa generosa ao redor da barra
    y_start = max(0, y_bar_start - 20)
    y_end   = min(h, y_bar_end   + 15)
    row = img[y_start:y_end, 0:min(w, 100)]  # primeiros 100px horizontal
    return row

# ----------------------------------------------------------------
# Menu de calibragem
# ----------------------------------------------------------------
print("=== CALIBRADOR DE TEMPLATES DE MONSTRO ===")
print()
print("Comandos:")
print("  n = capturar icone NORMAL (sera pedido o nome do monstro)")
print("  t = capturar icone TARGET (monstro selecionado / fundo vermelho)")
print("  s = mostrar screenshot atual da battle zone")
print("  l = listar monstros cadastrados")
print("  q = sair")
print()

os.makedirs("prints/battle/monsters", exist_ok=True)
os.makedirs("prints/battle/targets", exist_ok=True)
# Compatibility: mantem a pasta antiga tambem
os.makedirs("prints/battle", exist_ok=True)

# Lista monstros ja cadastrados
def list_monsters():
    monsters = []
    d = "prints/battle/monsters"
    if os.path.exists(d):
        monsters = [f[:-4] for f in os.listdir(d) if f.endswith('.png')]
    return monsters


while True:
    cmd = input("Comando (n/t/s/l/q): ").strip().lower()

    if cmd == 'q':
        print("Saindo.")
        break

    elif cmd == 's':
        img = capture_battle()
        cv2.imwrite("debug_battle_capture.png", img)
        print("Screenshot salvo: debug_battle_capture.png ({}x{})".format(img.shape[1], img.shape[0]))

        # Conta monstros
        hp_mask = (img[:,:,2] > 140) & (img[:,:,0] < 90)
        h, w = img.shape[:2]
        MIN_RUN = 5
        row_has_bar = np.zeros(h, dtype=bool)
        for y in range(h):
            row = hp_mask[y, :]
            run = 0
            for val in row:
                if val:
                    run += 1
                    if run >= MIN_RUN:
                        row_has_bar[y] = True
                        break
                else:
                    run = 0
        count = 0
        in_block = False
        for has in row_has_bar:
            if has and not in_block:
                count += 1
                in_block = True
            elif not has and in_block:
                in_block = False
        print("Monstros detectados por cor: {}".format(count))

    elif cmd == 'l':
        cadastrados = list_monsters()
        if cadastrados:
            print("Monstros cadastrados ({}):".format(len(cadastrados)))
            for m in cadastrados:
                tem_target = os.path.exists("prints/battle/targets/{}.png".format(m))
                status = "[icone + target]" if tem_target else "[so icone]"
                print("  - {} {}".format(m, status))
        else:
            print("Nenhum monstro cadastrado ainda. Use o comando 'n' para adicionar.")

    elif cmd == 'n':
        # Pede o nome do monstro
        nome = input("Nome do monstro (ex: dire_boar, giant_beetle): ").strip()
        if not nome:
            print("Nome invalido. Operacao cancelada.")
            continue
        nome = nome.lower().replace(' ', '_')

        print("Capturando icone NORMAL de '{}'...".format(nome))
        img = capture_battle()
        y_start, y_end = find_first_monster_row(img)

        if y_start is None:
            print("ERRO: Nenhum monstro detectado na battle zone!")
            print("Verifique se ha monstros visiveis e se a battle_region esta correta.")
            continue

        print("Primeira barra de HP encontrada em Y={} a Y={}".format(y_start, y_end))

        icon = extract_icon(img, y_end)

        # Salva na pasta de multiplos monstros
        icon_path = "prints/battle/monsters/{}.png".format(nome)
        cv2.imwrite(icon_path, icon)
        cv2.imwrite("debug_monster_icon.png", icon)
        print("Template NORMAL salvo: {} ({}x{})".format(icon_path, icon.shape[1], icon.shape[0]))
        print("Debug salvo: debug_monster_icon.png")
        print("Total de monstros cadastrados: {}".format(len(list_monsters())))

    elif cmd == 't':
        # Pede o nome do monstro
        nome = input("Nome do monstro para o target (mesmo nome usado no 'n'): ").strip()
        if not nome:
            print("Nome invalido. Operacao cancelada.")
            continue
        nome = nome.lower().replace(' ', '_')

        print("Capturando TARGET de '{}' (selecione o monstro no jogo primeiro)...".format(nome))
        img = capture_battle()
        y_start, y_end = find_first_monster_row(img)

        if y_start is None:
            print("AVISO: Nenhuma barra HP detectada. Tentando detectar pelo fundo colorido...")
            avatar_zone = img[:, 0:40]
            red_mask = (avatar_zone[:,:,2] >= 50) & (avatar_zone[:,:,1] < 40) & (avatar_zone[:,:,0] < 40)
            red_rows = np.where(np.any(red_mask, axis=1))[0]
            if len(red_rows) == 0:
                print("ERRO: Nenhum monstro selecionado detectado.")
                continue
            y_start = red_rows[0]
            y_end   = red_rows[-1] + 1

        print("Linha do target em Y={} a Y={}".format(y_start, y_end))

        h, w = img.shape[:2]
        row_y0 = max(0, y_start - 20)
        row_y1 = min(h, y_end + 15)
        target_row = img[row_y0:row_y1, 0:min(w, 100)]

        # Salva na pasta de targets nomeados
        target_path = "prints/battle/targets/{}.png".format(nome)
        cv2.imwrite(target_path, target_row)
        cv2.imwrite("debug_target_lock.png", target_row)
        print("Template TARGET salvo: {} ({}x{})".format(target_path, target_row.shape[1], target_row.shape[0]))
        print("Debug salvo: debug_target_lock.png")

    else:
        print("Comando invalido. Use n, t, s, l ou q.")

