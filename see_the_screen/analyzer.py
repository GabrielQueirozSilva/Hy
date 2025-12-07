# analyzer.py
import cv2
import numpy as np
from PIL import ImageGrab
import easyocr
from datetime import datetime
from ultralytics import YOLO
import json
import keyboard
import os
from item_parser import parse_item_data 
from pymongo import MongoClient
import re

class HypixelItemAnalyzer:
    def __init__(self, yolo_model_path, conf_threshold=0.9):
        self.model = YOLO(yolo_model_path)
        self.conf_threshold = conf_threshold
        self.running = True
        self.save_requested = False
        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client["hypixel_scans"]
        self.col = self.db["items"]
        
        print("Carregando modelo EasyOCR na memória...")
        self.reader = easyocr.Reader(['en']) 
        print("Modelo EasyOCR carregado com sucesso.")

        self.output_folder = "detections"
        os.makedirs(self.output_folder, exist_ok=True)
    
    def reconstruir_texto_por_posicao(self, ocr_results, y_tolerance=5):
        if not ocr_results: return ""
        ocr_results.sort(key=lambda res: res[0][0][1])
        lines, current_line = [], []
        last_y = ocr_results[0][0][0][1]
        for res in ocr_results:
            bbox, text, prob = res
            current_y = bbox[0][1]
            if abs(current_y - last_y) < y_tolerance:
                current_line.append(res)
            else:
                if current_line:
                    current_line.sort(key=lambda r: r[0][0][0])
                    lines.append(" ".join([r[1] for r in current_line]))
                current_line = [res]
                last_y = current_y
        if current_line:
            current_line.sort(key=lambda r: r[0][0][0])
            lines.append(" ".join([r[1] for r in current_line]))
        return "\n".join(lines)
    
    def extract_roi_text(self, image, bbox):
        x1, y1, x2, y2 = bbox
        roi = image[y1:y2, x1:x2]
        results = self.reader.readtext(roi)
        return self.reconstruir_texto_por_posicao(results).strip()
    
    def setup_keyboard_listeners(self):
        keyboard.add_hotkey('v', self.request_save)
        keyboard.add_hotkey('x', self.stop_analysis)
        print("⌨️  Escutador de teclado configurado. Pressione 'v' para salvar e 'x' para sair.")

    def start_realtime_analysis(self):
        print("🎮 Hypixel Item Analyzer - YOLO + EasyOCR")
        cv2.namedWindow("Hypixel Item Analysis", cv2.WINDOW_NORMAL)
        while self.running:
            screen = cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2BGR)
            display_frame = screen.copy()
            detections = self.detect_description_boxes(screen)
            current_analysis = []

            for det in detections:
                bbox = det['bbox']
                identified_text = self.extract_roi_text(screen, bbox) 

                item_data, sanitized_text = parse_item_data(identified_text) 
                
                current_analysis.append({'bbox': bbox, 'confidence': det['confidence'], 'raw_text': identified_text, 'sanitized_text': sanitized_text, 'item_data': item_data, 'timestamp': datetime.now().strftime("%H:%M:%S")})
                cv2.rectangle(display_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                cv2.putText(display_frame, f'Item: {det["confidence"]:.2f}', (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if self.save_requested and current_analysis:
                self.save_detection(current_analysis[0])
                self.save_requested = False
            
            self.display_analysis_overlay(display_frame, current_analysis)
            cv2.imshow("Hypixel Item Analysis", display_frame)
            
            if cv2.waitKey(1) & 0xFF == 27: break
        
        cv2.destroyAllWindows()
        keyboard.unhook_all()
        print("Análise encerrada.")
    
    def request_save(self): self.save_requested = True
    
    def stop_analysis(self): self.running = False
    
    def save_detection(self, detection):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        document = {
            "scan_timestamp": timestamp,
            "raw_text": detection.get("raw_text"),
            "sanitized_text": detection.get("sanitized_text"),
            "parsed": detection.get("item_data"),
            "bbox": detection.get("bbox"),
            "confidence": detection.get("confidence")
        }

        # manter versão sem _id para o JSON
        json_safe_document = document.copy()

        self.col.insert_one(document)

        os.makedirs(self.output_folder, exist_ok=True)
        filename = f"detection_{timestamp}.json"
        filepath = os.path.join(self.output_folder, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_safe_document, f, ensure_ascii=False, indent=2)

        print(f"💾 JSON salvo: {filepath}")
        print("🗄️ MongoDB: item inserido com sucesso.")


        
    def detect_description_boxes(self, image):
        results = self.model.predict(source=image, conf=self.conf_threshold, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({'bbox': (x1, y1, x2, y2), 'confidence': float(box.conf[0])})
        return detections
    
    def display_analysis_overlay(self, frame, analysis):
        if not analysis: return
        det = max(analysis, key=lambda x: x['confidence'])
        item_data = det.get('item_data', {})
        y_offset, x_offset = 50, 10
        info_lines = [
            f"Time: {det['timestamp']}",
            f"Conf: {det['confidence']:.2f}",
            f"Name: {item_data.get('name', 'N/A')}",
            f"Class: {item_data.get('class', 'N/A')}",
            f"Tier: {item_data.get('item_tier', 'N/A')}",
            f"Price: {item_data.get('price', 'N/A')}",
            f"Seller: {item_data.get('seller', 'N/A')}"
        ]
        for line in info_lines:
            cv2.putText(frame, line, (x_offset, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 25