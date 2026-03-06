import pydirectinput
import pyautogui
import time
import win32gui

class Actions:
    mouse_speed = 1.0

    @staticmethod
    def _focus_game():
        """Tenta encontrar a janela do Zezenia e dar foco nela"""
        try:
            hwnd = win32gui.FindWindow(None, "Zezenia Online")
            if hwnd:
                if win32gui.GetForegroundWindow() != hwnd:
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.1)
        except:
            pass

    @staticmethod
    def move_mouse(x, y, duration=0.1):
        """Move o mouse usando o sistema do pydirectinput"""
        Actions._focus_game()
        pydirectinput.moveTo(int(x), int(y))
        time.sleep(0.05)

    @staticmethod
    def click_mouse(x=None, y=None, button='left'):
        """Cliques processados pelo DirectX com Movimentação Suave e Triplo Clique."""
        Actions._focus_game()
        import win32api
        
        if x is not None and y is not None:
            # Movimentação Acelerada e Suave (Não empurra bot detection)
            start_x, start_y = win32api.GetCursorPos()
            steps = 15
            for i in range(1, steps + 1):
                cur_x = int(start_x + (x - start_x) * (i / steps))
                cur_y = int(start_y + (y - start_y) * (i / steps))
                pydirectinput.moveTo(cur_x, cur_y)
                time.sleep(0.01 / Actions.mouse_speed)
            
            # Wiggle de Confirmação (Pequena tremida na seta pro motor gráfico acordar a entidade visual sob ele)
            pydirectinput.moveTo(int(x) - 2, int(y) - 2)
            time.sleep(0.05)
            pydirectinput.moveTo(int(x), int(y))
            time.sleep((0.15 / Actions.mouse_speed)) # Espera hover acender no jogo
            
        # PRIMEIRO CLIQUE (Garante que a tela retome o Controle ou seleciona algo embaixo)
        pydirectinput.mouseDown(button=button)
        time.sleep(0.08)
        pydirectinput.mouseUp(button=button)
        
        time.sleep(0.12) # Pausa natural da mão humana
        
        # SEGUNDO CLIQUE (Confirma a Ação Física de Andar)
        pydirectinput.mouseDown(button=button)
        time.sleep(0.15)
        pydirectinput.mouseUp(button=button)
        
        time.sleep(0.10) # Pausa leve
        
        # TERCEIRO CLIQUE (Garante a Leitura da Ação Pelo Jogo em caso de perca de tickrate)
        pydirectinput.mouseDown(button=button)
        time.sleep(0.12)
        pydirectinput.mouseUp(button=button)
        
    @staticmethod
    def walk_click(x, y, vision=None):
        """Método Exclusivo para Andar: Move, Clica Direito, Encontra Módulo de Imagem 'Walk Here' e Clica."""
        Actions._focus_game()
        import win32api
        
        if x is not None and y is not None:
            start_x, start_y = win32api.GetCursorPos()
            steps = 15
            for i in range(1, steps + 1):
                cur_x = int(start_x + (x - start_x) * (i / steps))
                cur_y = int(start_y + (y - start_y) * (i / steps))
                pydirectinput.moveTo(cur_x, cur_y)
                time.sleep(0.01 / Actions.mouse_speed)
                
            pydirectinput.moveTo(int(x), int(y))
            time.sleep((0.15 / Actions.mouse_speed)) # Delay hover
        
        # 1. DUPLO CLIQUE ESQUERDO
        for _ in range(2):
            pydirectinput.mouseDown(button='left')
            time.sleep(0.05)
            pydirectinput.mouseUp(button='left')
            time.sleep(0.08)

        # 2. CLIQUE BOTÃO DIREITO
        pydirectinput.mouseDown(button='right')
        time.sleep(0.12)
        pydirectinput.mouseUp(button='right')
        
        # 3. ESPERA MENU ABRIR
        time.sleep(0.3)
        
        found_walk = False
        # Fallback atualizado: se 40 cai no 'Remove' (2ª opcão), 65 deve cair na 3ª (Walk Here)
        walk_option_x, walk_option_y = int(x) + 5, int(y) + 65 
        
        if vision is not None:
            try:
                import cv2
                import numpy as np
                rx, ry = max(0, int(x) - 50), max(0, int(y) - 50)
                region = {"top": ry, "left": rx, "width": 300, "height": 300}
                img = vision.get_screen_capture(region=region)
                if img is not None:
                    # Binariza a imagem para achar somente os pixels cláros da fonte ('Walk Here')
                    mask = cv2.inRange(img, (180, 180, 180), (255, 255, 255))
                    img[mask == 0] = 0
                    
                    # Threshold muito relaxado para achar estrutura de font (60% ou mais garante o acerto da palavra)
                    import os as _os
                    _wh = _os.path.join("prints", "walkHere.png")
                    pt = vision.find_image(_wh, img, threshold=0.55) if _os.path.exists(_wh) else None
                    if pt:
                        walk_option_x = rx + pt[0]
                        walk_option_y = ry + pt[1]
                        found_walk = True
                        print(f"-> Walk Here LIDO POR IA (Confianca: {pt[2]:.2f})")
                    else:
                        print(f"-> Walk Here NAO ENCONTRADO na leitura de pixels. Usando Fallback Y+65.")
            except Exception as e:
                print("Erro ao achar Walk Here menu:", e)

        # Movimento Natural pro Menu
        current_x, current_y = win32api.GetCursorPos()
        stepsm = 5
        for i in range(1, stepsm + 1):
            cx = int(current_x + (walk_option_x - current_x) * (i / stepsm))
            cy = int(current_y + (walk_option_y - current_y) * (i / stepsm))
            pydirectinput.moveTo(cx, cy)
            time.sleep(0.01 / Actions.mouse_speed)
            
        pydirectinput.moveTo(walk_option_x, walk_option_y)
        time.sleep(0.1)
        
        # 5. CLICA ESQUERDO
        pydirectinput.mouseDown(button='left')
        time.sleep(0.15)
        pydirectinput.mouseUp(button='left')
        
    @staticmethod
    def press_key(key):
        """Pressionamento completo simulando input humano através de DX"""
        key = str(key).lower()
        if key == "space": 
            key = "space"
            
        Actions._focus_game()
        
        try:
            # Pressiona de forma rústica, simulando o peso do dedo em milissegundos
            pydirectinput.keyDown(key)
            time.sleep(0.15) # Segura a tecla forte (150ms) para 100% de hit rate na rede
            pydirectinput.keyUp(key)
        except Exception as e:
            print("Erro no pydirectinput:", e)

    @staticmethod
    def loot_shift_right(x, y):
        """Loot complexo usando teclado e mouse do pydirectinput"""
        Actions._focus_game()
        pydirectinput.moveTo(int(x), int(y))
        time.sleep(0.05)
        pydirectinput.keyDown('shift')
        time.sleep(0.05)
        pydirectinput.mouseDown(button='right')
        time.sleep(0.08)
        pydirectinput.mouseUp(button='right')
        time.sleep(0.05)
        pydirectinput.keyUp('shift')

    @staticmethod
    def perform_loot(region):
        """Clica segurando Shift + Botão Direito nas 8 partes periféricas da região do Personagem"""
        Actions._focus_game()
        if not region: return
        
        # Pega as margens da Região de Loot que o Usuário Marcou
        # Geralmente 1 SQM do boneco equivale a aprox. 32x32px ou 40x40.
        # Adicionamos pequena margem para garantir clique nos corpos
        offset_y = max(10, region['height'] // 3)
        offset_x = max(10, region['width'] // 3)
        
        cx = region['left'] + region['width'] // 2
        cy = region['top'] + region['height'] // 2
        
        pts = [
            (cx - offset_x, cy - offset_y), # Top-Left
            (cx, cy - offset_y),            # Top-Center
            (cx + offset_x, cy - offset_y), # Top-Right
            (cx - offset_x, cy),            # Left
            (cx + offset_x, cy),            # Right
            (cx - offset_x, cy + offset_y), # Bottom-Left
            (cx, cy + offset_y),            # Bottom-Center
            (cx + offset_x, cy + offset_y), # Bottom-Right
        ]
        
        # O Motor trava o Shift apenas uma vez, e metralha botão direito nos corpos em volta
        pydirectinput.keyDown('shift')
        time.sleep(0.05)
        
        for p in pts:
            # Movimento hiper veloz
            pydirectinput.moveTo(int(p[0]), int(p[1]))
            time.sleep(0.01)
            pydirectinput.mouseDown(button='right')
            time.sleep(0.02)
            pydirectinput.mouseUp(button='right')
            time.sleep(0.01)
            
        time.sleep(0.05)
        pydirectinput.keyUp('shift')
