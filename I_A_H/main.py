import cv2
import keyboard
import winsound
from datetime import datetime
from I_A_H.analyzer.screen_analyzer import ScreenAnalyzer
from I_A_H.parser.item_parser import parse_item_data
from I_A_H.storage.mongo import MongoStorage
from I_A_H.storage.json_export import save_json
from I_A_H.ui.overlay import draw_overlay
import threading


def beep_async(freq, duration):
    threading.Thread(target=winsound.Beep, args=(freq, duration), daemon=True).run()



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

    prev_detection_count = 0

    while running:
        frame = analyzer.grab_screen()
        detections = analyzer.detect_boxes(frame)

        # aviso sonoro quando começa a detectar algo
        if len(detections) > 0:
            beep_async(3000, 1000)  # frequência 1000hz, duração 200ms

        prev_detection_count = len(detections)

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)

            if save_requested:
                raw_text = analyzer.extract_text(frame, det["bbox"])
                if not raw_text.strip():
                    continue
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
                mongo.save(detection)
                save_json(detection)
                # aviso sonoro ao salvar
                beep_async(1500, 1000)

        save_requested = False

        scale = 0.5
        frame_display = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
        cv2.imshow("Hypixel Item Analyzer", frame_display)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
    keyboard.unhook_all()
    print("Análise encerrada.")

if __name__ == "__main__":
    main()