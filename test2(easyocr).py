import cv2
import numpy as np
from PIL import ImageGrab
import easyocr
from datetime import datetime
from ultralytics import YOLO
import json
import keyboard
import os 
import re
from thefuzz import fuzz, process

LIMITE_DE_CONFIANCA_PET = 88 
TIERS = ["legendary", "epic", "rare", "common", "uncommon", "mythic", "special", "divine", "very special"]
PET_TYPES = ["elephant", "blue whale", "enderman", "silverfish","Armadillo","endermite","glacite golem", "scatcha", "bal", "bat", "mole"
             "mithril golem", "rat", "rabbit", "tiger", "grandma wolf", "snail", "wither skeleton", "goblin", "Ankylosaurus", "black cat" 
             "reindeer", "rock", "guardian", "golden dragon", "armadillo", "monkey", "sheep", "mushroom cow", "blaze", "eeire",
             "ender dragon", "ghoul", "golem", "griffin", "horse", "hound", "jerry", "kuudra", "magma cube", "mammoth", "phoenix", "pigman",
             "rift ferret", "skeleton horse", "skeleton", "snowman", "spider", "squid", "tarantula", "spirit", "turtle", "t-rex", "zombie",
             "wolf", "bee", "chicken", "hedgehog", "pig", "slug", "girafe", "lion", "ocelot", "ammonite", "baby yeti", "dolphin", "flying fish",
             "megalodon", "penguin", "spinosarus", "hermit crab", "jellyfish", "parrot", "owl", "bingo", "montezuma", "wisp"]
PRICE_KEYWORDS = ["buy it now:", "now:", "it now:", "coins", "coims", "coms", "by it now:"]
COSMETIC_KEYWORDS = ["skin", "pet skins", "change the look", "skin can be active", "this skin"]
DUNGEDON = ["score:", "gear", "gear score:"]

class HypixelItemAnalyzer:
    def __init__(self, yolo_model_path, conf_threshold=0.9):
        self.model = YOLO(yolo_model_path)
        self.conf_threshold = conf_threshold
        self.running = True
        self.save_requested = False
        
        print("Carregando modelo EasyOCR na memória...")
        self.reader = easyocr.Reader(['en']) 
        print("Modelo EasyOCR carregado com sucesso.")

        self.output_folder = "detections"
        os.makedirs(self.output_folder, exist_ok=True)
    
    def reconstruir_texto_por_posicao(self, ocr_results, y_tolerance=5):
        """
        Agrupa os resultados do EasyOCR em linhas baseadas na sua posição vertical (Y).
        """
        if not ocr_results:
            return ""

        ocr_results.sort(key=lambda res: res[0][0][1])

        lines = []
        current_line = []
        last_y = ocr_results[0][0][0][1]

        for res in ocr_results:
            bbox, text, prob = res
            current_y = bbox[0][1]

            if abs(current_y - last_y) < y_tolerance:
                current_line.append(res)
            else:
                if current_line:
                    current_line.sort(key=lambda r: r[0][0][0]) # Ordena por X (esquerda para direita)
                    lines.append(" ".join([r[1] for r in current_line]))
                
                current_line = [res]
                last_y = current_y
        
        if current_line:
            current_line.sort(key=lambda r: r[0][0][0])
            lines.append(" ".join([r[1] for r in current_line]))

        return "\n".join(lines)
    
    def parse_item_data(self, text):
        item_data = {}
        lines = text.splitlines()

        if lines:
            item_data['name'] = lines[0].strip()
            
        if len(lines) >= 5: 
            # Pega a quinta última linha para o TIER
            quinta_ultima_linha = lines[-5].strip().lower()
            for tier in TIERS:
                if tier in quinta_ultima_linha:
                    item_data['item_tier'] = tier
                    break
                
            # Pega a quarta última linha para o SELLER   
            quarta_ultima_linha = lines[-4].strip()
            partes = quarta_ultima_linha.split(maxsplit=1)
            if len(partes) == 2:
                chave,valor = partes[0], partes[1]  
                chave_normalizada = chave.lower().replace('-', ':')
                if fuzz.ratio(chave_normalizada, "seller:") >= 80:
                    item_data['seller'] = valor.strip()
            
            # Pega a terceira última linha para o PRICE    
            terceira_ultima_linha = lines[-3].strip().lower()
            try:
                parte_do_preco = terceira_ultima_linha.split(':', 1)[1]
                price_str = re.sub(r'[^\d]', '', parte_do_preco)
                if price_str:
                    item_data['price'] = int(price_str)
            except (IndexError, ValueError):
                item_data['price'] = None      


        # 1. TENTATIVA DE CLASSIFICAR COMO PET PELO NOME (ALTA PRIORIDADE)
  
        nome_limpo = item_data['name'].lower()
        melhor_pontuacao_pet = 0
        melhor_match_pet = None
            
        for pet_type in PET_TYPES:
            pontuacao = fuzz.partial_ratio(pet_type, nome_limpo)
            if pontuacao > melhor_pontuacao_pet:
                melhor_pontuacao_pet = pontuacao
                melhor_match_pet = pet_type

        if melhor_pontuacao_pet >= LIMITE_DE_CONFIANCA_PET:
            item_data['class'] = "Pet"
            item_data['pet_type'] = melhor_match_pet
        
        #FUNÇÃO DE BACKUP(CASO NÃO TENHA ENCONTRADO VALORES AINDA)
        for line in lines[1:]: # Começa da segunda linha
            line_clean = line.strip().lower()
            if not line_clean:
                continue

            if 'price' not in item_data and any(keyword in line_clean for keyword in PRICE_KEYWORDS):
                try:
                    parte_do_preco = line.split(':', 1)[1]
                    price_str = re.sub(r'[^\d]', '', parte_do_preco)
                    if price_str:
                        item_data['price'] = int(price_str)
                except (IndexError, ValueError):
                    pass

            if 'class' not in item_data: 
                if any(keyword in line_clean for keyword in DUNGEDON):
                    item_data['class'] = "Item"
                elif any(keyword in line_clean for keyword in COSMETIC_KEYWORDS):
                    item_data['class'] = "Cosmetic"
                                    
                        
        return item_data

    def extract_roi_text(self, image, bbox):
        x1, y1, x2, y2 = bbox
        roi = image[y1:y2, x1:x2]
        
        results = self.reader.readtext(roi)
        
        full_text = self.reconstruir_texto_por_posicao(results)
        
        return full_text.strip()
        
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
        base_filename = f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        full_path = os.path.join(self.output_folder, base_filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(detection, f, ensure_ascii=False, indent=2)
        print(f"💾 Detecção salva em: {full_path}")

    def start_realtime_analysis(self):
        print("🎮 Hypixel Item Analyzer - YOLO + EasyOCR")
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

    def display_analysis_overlay(self, frame, analysis):
        if not analysis: return
        det = max(analysis, key=lambda x: x['confidence'])
        item_data = det.get('item_data', {})
        y_offset = 50
        info_lines = [ f"Time: {det['timestamp']}", f"Conf: {det['confidence']:.2f}", f"Item: {item_data.get('name', 'N/A')}", f"Price: {item_data.get('price', 'N/A')}", f"Seller: {item_data.get('seller', 'N/A')}"]
        for line in info_lines:
            cv2.putText(frame, line, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 25

if __name__ == "__main__":
    MODEL_PATH = r"C:\Users\gabri\Desktop\aprendendo\hypixel\comercialhelper-20250925T190655Z-1-001\comercialhelper\MODEL-3, after 20\weights\best.pt"
    
    analyzer = HypixelItemAnalyzer(yolo_model_path=MODEL_PATH)
    analyzer.setup_keyboard_listeners()
    analyzer.start_realtime_analysis()