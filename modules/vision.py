import cv2
import mss
import numpy as np
import threading

class Vision:
    def __init__(self):
        # NOTA: Não inicializamos o mss aqui no construtor para evitar o erro de Thread
        # Cada thread (UI e Bot) deve ter sua própria instância ou reinicializar
        self._sct = None

    @property
    def sct(self):
        if self._sct is None:
            self._sct = mss.mss()
        return self._sct

    def get_screen_capture(self, region=None):
        """
        Captura monitor ou região específica.
        region = {"top": 100, "left": 100, "width": 800, "height": 600}
        """
        try:
            if region:
                sct_img = self.sct.grab(region)
            else:
                sct_img = self.sct.grab(self.sct.monitors[1])
            
            img = np.array(sct_img)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img
        except Exception as e:
            print(f"Erro na captura: {e}")
            self._sct = None # Força reinicialização se der erro
            return None
        
    def find_color(self, screen_img, color_name):
        """Procura centros de massa de uma cor específica no HSV."""
        if screen_img is None: return None
        
        hsv = cv2.cvtColor(screen_img, cv2.COLOR_BGR2HSV)
        
        # Ranges calibrados para os marcadores do Zezenia
        ranges = {
            "red": ([0, 150, 50], [10, 255, 255]),
            "green": ([40, 150, 50], [80, 255, 255]),
            "blue": ([100, 150, 50], [130, 255, 255]),
            "purple": ([130, 150, 50], [160, 255, 255]),
            "orange": ([10, 150, 50], [25, 255, 255]),
            "cyan": ([85, 150, 50], [100, 255, 255])
        }
        
        if color_name not in ranges:
            return None
            
        lower = np.array(ranges[color_name][0])
        upper = np.array(ranges[color_name][1])
        
        mask = cv2.inRange(hsv, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        results = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 2: 
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    results.append((cX, cY))
                    
        return results

    def find_image(self, target_image_path, screen_img, threshold=0.7):
        """Procura o template dentro na screen_img fornecida (Suporta Transparência/Alpha)."""
        if screen_img is None: return None
        try:
            template = cv2.imread(target_image_path, cv2.IMREAD_UNCHANGED) # -1 para carregar canal alpha
            if template is None:
                return None
            
            mask = None
            if len(template.shape) == 3 and template.shape[2] == 4:
                # Possui canal Alpha (Fundo removido)
                bgr_template = template[:, :, :3]
                mask = template[:, :, 3]
                template_to_use = bgr_template
            else:
                template_to_use = template

            if mask is not None:
                # Com máscara, DEVE usar TM_CCORR_NORMED (Ou SQDIFF)
                result = cv2.matchTemplate(screen_img, template_to_use, cv2.TM_CCORR_NORMED, mask=mask)
            else:
                # Busca padrao de caixas solidas
                result = cv2.matchTemplate(screen_img, template_to_use, cv2.TM_CCOEFF_NORMED)
                
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                h, w = template_to_use.shape[:-1]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                return (center_x, center_y, max_val)
            else:
                return None
        except Exception as e:
            print(f"Erro em find_image: {e}")
            return None

    def find_all_images(self, target_image_path, screen_img, threshold=0.7):
        """Procura todas as ocorrências de uma imagem e retorna a contagem e lista de posições."""
        if screen_img is None: return []
        try:
            template = cv2.imread(target_image_path, cv2.IMREAD_UNCHANGED)
            if template is None: return []
            
            # Setup similar ao find_image
            mask = None
            if len(template.shape) == 3 and template.shape[2] == 4:
                bgr_template = template[:, :, :3]
                mask = template[:, :, 3]
                template_to_use = bgr_template
            else:
                template_to_use = template

            if mask is not None:
                result = cv2.matchTemplate(screen_img, template_to_use, cv2.TM_CCORR_NORMED, mask=mask)
            else:
                result = cv2.matchTemplate(screen_img, template_to_use, cv2.TM_CCOEFF_NORMED)

            locs = np.where(result >= threshold)
            h, w = template_to_use.shape[:-1]
            
            points = []
            for pt in zip(*locs[::-1]):
                # Agrupar pontos próximos para não contar o mesmo monstro várias vezes
                is_new = True
                for p in points:
                    if abs(p[0] - pt[0]) < w//2 and abs(p[1] - pt[1]) < h//2:
                        is_new = False
                        break
                if is_new:
                    points.append((pt[0] + w//2, pt[1] + h//2))
            return points
        except Exception as e:
            print(f"Erro em find_all_images: {e}")
            return []

    def count_battle_enemies(self, bgr_img):
        """
        Detecta monstros na Battle List do Zezenia.
        
        Calibrado para barras de HP de qualquer cor:
          - Dourado/Amarelo (HP cheio): R=220, G=131, B=41  (Dire Boar)
          - Laranja         (HP medio): R alto, G medio, B baixo
          - Vermelho        (HP baixo): R alto, G baixo, B baixo
        
        Lógica: hp_mask = R>140 & B<90.
        Para cada linha, verifica se ha um run HORIZONTAL de >= 5 pixels consecutivos
        com essa cor (garante que e uma barra real, nao ruido).
        Blocos verticais de linhas com barra = 1 monstro por bloco.
        
        100% numpy — sem loops Python para maxima performance.
        """
        if bgr_img is None: return 0, False
        
        h, w = bgr_img.shape[:2]
        if h == 0 or w == 0: return 0, False
        
        # --- CONTAGEM DE MONSTROS ---
        # Mascara: R alto(>140) + B baixo(<90) = qualquer tom de barra HP Zezenia
        hp_mask = (bgr_img[:,:,2] > 140) & (bgr_img[:,:,0] < 90)  # shape (h, w)
        
        # Deteccao de runs horizontais >= 5px usando numpy:
        # Para cada linha, calcula o cumsum e encontra runs de True >= MIN_RUN
        MIN_RUN = 5
        
        # Converte para int para calculo de cumsum
        m = hp_mask.astype(np.int32)  # (h, w)
        
        # Diferenca entre colunas: +1 = inicio de run, -1 = fim de run
        # Adiciona coluna de zeros no inicio e no fim para detectar bordas
        padded = np.pad(m, ((0,0),(1,1)), mode='constant', constant_values=0)
        diff = np.diff(padded, axis=1)  # (h, w+1)
        
        # Para cada linha, encontra tamanho max do run
        # Usamos cumsum para calcular comprimentos dos runs
        row_has_bar = np.zeros(h, dtype=bool)
        
        # Abordagem: se qualquer elemento da soma acumulada com reset atingir MIN_RUN, a linha tem barra
        # Implementação eficiente: calcula comprimento maximo de run por linha
        cumsum = np.cumsum(m, axis=1)  # (h, w)
        
        # Para cada inicio de run (diff == 1), o tamanho do run em (y, x_start) e
        # cumsum[y, x_end] - cumsum[y, x_start - 1]
        # Alternativa mais simples: verifica se existe janela deslizante de MIN_RUN pixels todos True
        # Via erosao horizontal (equivale a AND de MIN_RUN pixels consecutivos)
        if w >= MIN_RUN:
            kernel = np.ones((1, MIN_RUN), dtype=np.uint8)
            hp_uint8 = hp_mask.astype(np.uint8)
            import cv2 as _cv2
            eroded = _cv2.erode(hp_uint8, kernel)  # True onde ha MIN_RUN pixels True consecutivos
            row_has_bar = np.any(eroded > 0, axis=1)  # (h,)
        else:
            # Imagem muito estreita: qualquer pixel colorido conta
            row_has_bar = np.any(hp_mask, axis=1)
        
        # Conta blocos verticais (cada bloco = 1 monstro)
        # Usando diff do array booleano
        rb_int = row_has_bar.astype(np.int8)
        # Adiciona bordas para detectar blocos no inicio/fim
        rb_padded = np.pad(rb_int, 1, mode='constant', constant_values=0)
        edges = np.diff(rb_padded.astype(np.int8))
        count = int(np.sum(edges > 0))  # numero de transicoes 0->1 = numero de blocos
        
        # --- DETECCAO DE TARGET LOCKED ---
        # Quando monstro e selecionado, a zona do avatar (col 1..36) fica com fundo
        # vermelho escuro: R>=50, G<40, B<40 (valor real: R=78, G=18, B=18)
        #
        # Analisa LINHA POR LINHA: uma linha selecionada tem >40% de seus pixels
        # vermelhos naquela linha especifica. Isso funciona independente de quantos
        # monstros ha no painel (1 ou 20 monstros — sempre funciona).
        avatar_end = min(36, w)
        if avatar_end > 1:
            av = bgr_img[:, 1:avatar_end]
            av_red = ((av[:,:,2] >= 50) & (av[:,:,1] < 40) & (av[:,:,0] < 40)).astype(np.float32)
            # Para cada linha, calcula a fracao de pixels vermelhos
            row_red_frac = av_red.mean(axis=1)  # shape (h,)
            # Se QUALQUER linha tiver >40% vermelho = alvo selecionado
            target_locked = bool(np.any(row_red_frac > 0.40))
        else:
            target_locked = False
        
        return count, target_locked

    def get_bar_percentage(self, bgr_img):
        """Calcula a porcentagem da barra isolando pixels intensamente coloridos (HP/Mana) x fundo escuro (vazio)"""
        if bgr_img is None: return 0
        
        h, w, c = bgr_img.shape
        if w == 0 or h == 0: return 0
        
        # Pega a linha central
        row = bgr_img[h // 2, :, :]
        
        B = row[:, 0].astype(int)
        G = row[:, 1].astype(int)
        R = row[:, 2].astype(int)
        
        # Condições infalíveis de pixels de cor (Azul dominou, Vermelho dominou ou Verde dominou)
        is_colored = ((B > R + 20) & (B > G + 20)) | \
                     ((R > B + 20) & (R > G + 20)) | \
                     ((G > R + 20) & (G > B + 20))
                     
        # Condição de barra vazia (fundo escuro acinzentado da barra)
        is_empty = (R < 50) & (G < 50) & (B < 50) & (np.abs(R - G) < 10) & (np.abs(B - G) < 10)
        
        # Pixels válidos são apenas os coloridos ou o fundo vazio da barra
        valid_pixels = is_colored | is_empty
        valid_indices = np.where(valid_pixels)[0]
        
        if len(valid_indices) == 0: return 0
        
        start = valid_indices[0]
        end = valid_indices[-1]
        
        bar_width = end - start + 1
        if bar_width <= 0: return 0
        
        # Quantos pixels coloridos existem dentro do limite da barra?
        colored_count = np.count_nonzero(is_colored[start:end+1])
        
        percent = int((colored_count / bar_width) * 100)
        return max(0, min(100, percent))
