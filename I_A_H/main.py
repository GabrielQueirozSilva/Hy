import cv2
import keyboard
from datetime import datetime

from I_A_H.analyzer.screen_analyzer import ScreenAnalyzer
from I_A_H.parser.item_parser import parse_item_data
from I_A_H.storage.mongo import MongoStorage
from I_A_H.storage.json_export import save_json
from I_A_H.ui.overlay import draw_overlay

def main():
    analyzer = ScreenAnalyzer(r"I_A_H\IA\best.pt")
    mongo = MongoStorage()

    running = True
    save_requested = False

    def request_save():
        nonlocal save_requested
        save_requested = True

    def stop():
        nonlocal running
        running = False

    keyboard.add_hotkey('v', request_save)
    keyboard.add_hotkey('x', stop)

    print("Pressione 'v' para salvar | 'x' para sair")

    while running:
        frame = analyzer.grab_screen()
        detections = analyzer.detect_boxes(frame)

        for det in detections:
            raw_text = analyzer.extract_text(frame, det["bbox"])
            item_data, sanitized_text = parse_item_data(raw_text)

            detection = {
                "scan_timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "raw_text": raw_text,
                "sanitized_text": sanitized_text,
                "parsed": item_data,
                "bbox": det["bbox"],
                "confidence": det["confidence"]
            }

            draw_overlay(frame, detection)

            if save_requested:
                mongo.save(detection)
                save_json(detection)
                save_requested = False

            x1, y1, x2, y2 = det["bbox"]
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)

        cv2.imshow("Hypixel Item Analyzer", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
    keyboard.unhook_all()
    print("Análise encerrada.")

if __name__ == "__main__":
    main()
