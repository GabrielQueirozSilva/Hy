import cv2
import numpy as np
from PIL import ImageGrab
import pytesseract
from datetime import datetime
from ultralytics import YOLO
import json
import keyboard
import os #
import re

TIERS = ["legendary", "epic", "rare", "common", "uncommon", "mythic", "special", "divine", "very special"]

PET_TYPES = ["elephant", "blue whale", "enderman", "silverfish","Armadillo","endermite","glacite golem", "scatcha", "bal", "bat", "mole"
             "mithril golem", "rat", "rabbit", "tiger", "grandma wolf", "snail", "wither skeleton", "goblin", "Ankylosaurus", "black cat" 
             "reindeer", "rock", "guardian", "golden dragon", "armadillo", "monkey", "sheep", "mushroom cow", "blaze", "eeire",
             "ender dragon", "ghoul", "golem", "griffin", "horse", "hound", "jerry", "kuudra", "magma cube", "mammoth", "phoenix", "pigman",
             "rift ferret", "skeleton horse", "skeleton", "snowman", "spider", "squid", "tarantula", "spirit", "turtle", "t-rex", "zombie",
             "wolf", "bee", "chicken", "hedgehog", "pig", "slug", "girafe", "lion", "ocelot", "ammonite", "baby yeti", "dolphin", "flying fish",
             "megalodon", "penguin", "spinosarus", "hermit crab", "jellyfish", "parrot", "owl", "bingo", "montezuma", "wisp"]

PRICE_KEYWORDS = ["buy it now:", "now:", "it now:", "coins", "coims", "coms", "by it now:"]
COSMETIC_KEYWORDS = ["pet skins", "change the look", "skin can be active", "this skin"]



class HypixelItemAnalyzer:
    def __init__(self, yolo_model_path, conf_threshold=0.9):
        self.model = YOLO(yolo_model_path)
        self.conf_threshold = conf_threshold
        self.running = True
        self.save_requested = False

        # --- 2. Define e cria a pasta de saída ---
        self.output_folder = "detections"  # Nome da pasta onde os arquivos serão salvos
        os.makedirs(self.output_folder, exist_ok=True) # Cria a pasta se ela não existir

    def parse_item_data(self, text):
        item_data = {}
        lines = text.splitlines()

        for line in lines:
            # Usamos o line original para preservar o case (maiúsculas/minúsculas) se precisarmos,
            # e o line_clean para fazer as verificações.
            line_clean = line.strip().lower()
            if not line_clean:
                continue

                # --- Extração de Preço ---
                # Verificamos apenas uma vez para evitar reprocessamento
            if 'price' not in item_data and any(keyword in line_clean for keyword in PRICE_KEYWORDS):
                try:
                    # 1. Divide a linha no ':' para pegar a parte com o valor.
                    parte_do_preco = line.split(':', 1)[1]
                    
                    # 2. Da parte do valor, remove TUDO que não for um dígito.
                    price_str = re.sub(r'[^\d]', '', parte_do_preco)
                    print(f"Debug: Extraído price_str='{price_str}' da linha='{line}'")

                    # 3. Tenta converter a string de dígitos para um número.
                    if price_str:
                        price_str = price_str.replace('8', '0')
                        item_data['price'] = int(price_str)
                    else:
                        item_data['price'] = None
                except (IndexError, ValueError):
                    # Se o split falhar (sem ':') ou a conversão falhar, o preço é nulo.
                    item_data['price'] = None

            # --- Extração do Vendedor ---
            # CORREÇÃO: Usamos elif para não verificar desnecessariamente e split para pegar só o nome
            elif 'seller:' in line_clean:
                # Pegamos o texto DEPOIS de "seller:" e removemos espaços
                try:
                    # Usamos o 'line' original para manter o nome do vendedor com o case correto
                    seller_name = line.split(':', 1)[1].strip()
                    item_data['seller'] = seller_name
                except IndexError:
                    pass # Linha continha "seller:" mas nada depois

            # --- Extração de Tier ---
            # OTIMIZAÇÃO: Só procuramos o tier se ainda não o encontramos
            elif 'item_tier' not in item_data and any(tier in line_clean for tier in TIERS):
                for tier in TIERS:
                    if tier in line_clean:
                        item_data['item_tier'] = tier
                        break # Para o laço assim que encontra o primeiro

            # --- Classificação do Item ---
            # MELHORIA: A lógica de classificação agora usa 'elif' para evitar sobrescritas
            elif 'class' not in item_data:
                if "gear score:" in line_clean: # Corrigido para minúsculas
                    item_data['class'] = "Item"
                elif any(keyword in line_clean for keyword in COSMETIC_KEYWORDS):
                    item_data['class'] = "Cosmetic"
                else:
                    for pet in PET_TYPES:
                        if pet in line_clean:
                            item_data['class'] = "Pet"
                            item_data['pet_type'] = pet
                            break # Encontrou um pet, não precisa mais procurar


            
        return item_data

    # As outras funções (request_save, stop_analysis, etc.) continuam iguais
    def request_save(self):
        print("[AÇÃO] Tecla 'v' pressionada. Salvamento solicitado...")
        self.save_requested = True

    def stop_analysis(self):
        print("[AÇÃO] Tecla 'x' pressionada. Encerrando...")
        self.running = False

    def setup_keyboard_listeners(self):
        keyboard.add_hotkey('v', self.request_save)
        keyboard.add_hotkey('x', self.stop_analysis)
        print("⌨️  Escutador de teclado configurado. Pressione 'v' para salvar e 'x' para sair a qualquer momento.")

    def save_detection(self, detection):
        """Salva detecção para análise posterior DENTRO DA PASTA 'detections'."""
        
        # --- 3. Cria o caminho completo para o arquivo ---
        base_filename = f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # os.path.join() junta a pasta e o nome do arquivo de forma segura
        # Ex: "detections" + "detection_...json" -> "detections/detection_...json"
        full_path = os.path.join(self.output_folder, base_filename)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(detection, f, ensure_ascii=False, indent=2)
            
        # Imprime o caminho completo para você saber exatamente onde foi salvo
        print(f"💾 Detecção salva em: {full_path}")


    # O resto do seu código permanece exatamente igual...
    def start_realtime_analysis(self):
        print("🎮 Hypixel Item Analyzer - YOLO + OCR(versão easyocr)")
        cv2.namedWindow("Hypixel Item Analysis", cv2.WINDOW_NORMAL)
        while self.running:
            screen = self.capture_screen()
            display_frame = screen.copy()
            detections = self.detect_description_boxes(screen)
            current_analysis = []
            for det in detections:
                bbox = det['bbox']
                conf = det['confidence']
                x1, y1, x2, y2 = bbox
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(display_frame, f'Item: {conf:.2f}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                text = self.extract_roi_text(screen, bbox)
                item_data = self.parse_item_data(text)
                current_analysis.append({'bbox': bbox, 'confidence': conf, 'text': text, 'item_data': item_data, 'timestamp': datetime.now().strftime("%H:%M:%S")})
            
            if self.save_requested and current_analysis:
                self.save_detection(current_analysis[0])
                self.save_requested = False
            
            self.display_analysis_overlay(display_frame, current_analysis)
            cv2.imshow("Hypixel Item Analysis", display_frame)
            
            if cv2.waitKey(1) & 0xFF == 27:
                break
        
        cv2.destroyAllWindows()
        keyboard.unhook_all()
        print("Análise encerrada.")
        
    def capture_screen(self):
        screenshot = ImageGrab.grab()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def detect_description_boxes(self, image):
        results = self.model.predict(source=image, conf=self.conf_threshold, verbose=False)
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                detections.append({'bbox': (x1, y1, x2, y2), 'confidence': conf, 'class': cls})
        return detections

    def extract_roi_text(self, image, bbox):
        x1, y1, x2, y2 = bbox
        roi = image[y1:y2, x1:x2]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(binary, lang='eng', config='--psm 6')
        return text.strip()

    def display_analysis_overlay(self, frame, analysis):
        if not analysis: return
        det = max(analysis, key=lambda x: x['confidence'])
        item_data = det['item_data']
        y_offset = 50
        info_lines = [ f"Time: {det['timestamp']}", f"Conf: {det['confidence']:.2f}", f"Item: {item_data.get('name', 'N/A')}", f"Price: {item_data.get('price', 'N/A')}", f"Seller: {item_data.get('seller', 'N/A')}"]
        for line in info_lines:
            cv2.putText(frame, line, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 25


# O bloco de execução continua o mesmo
if __name__ == "__main__":
    MODEL_PATH = r"C:\Users\gabri\Desktop\aprendendo\hypixel\comercialhelper-20250925T190655Z-1-001\comercialhelper\MODEL-3, after 20\weights\best.pt"
    
    analyzer = HypixelItemAnalyzer(yolo_model_path=MODEL_PATH)
    analyzer.setup_keyboard_listeners()
    analyzer.start_realtime_analysis()