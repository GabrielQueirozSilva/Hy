import cv2
import numpy as np
from PIL import ImageGrab
import easyocr
from ultralytics import YOLO

class ScreenAnalyzer:
    def __init__(self, yolo_model_path, conf_threshold=0.9):
        self.model = YOLO(yolo_model_path)
        self.conf_threshold = conf_threshold
        self.reader = easyocr.Reader(['en'])

    def grab_screen(self):
        return cv2.cvtColor(
            np.array(ImageGrab.grab()),
            cv2.COLOR_RGB2BGR
        )

    def detect_boxes(self, image):
        results = self.model.predict(
            source=image,
            conf=self.conf_threshold,
            verbose=False
        )

        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    "bbox": (x1, y1, x2, y2),
                    "confidence": float(box.conf[0])
                })
        return detections

    def extract_text(self, image, bbox):
        x1, y1, x2, y2 = bbox
        roi = image[y1:y2, x1:x2]
        results = self.reader.readtext(roi)
        return self._rebuild_text(results)

    def _rebuild_text(self, ocr_results, y_tolerance=5):
        if not ocr_results:
            return ""

        # pega o Y do primeiro ponto da bbox
        last_y = ocr_results[0][0][0][1]

        lines = []
        current = []

        for bbox, text, prob in ocr_results:
            # bbox é [[x,y], [x,y], [x,y], [x,y]]
            y = bbox[0][1]  # <-- AQUI está a correção

            if abs(y - last_y) < y_tolerance:
                current.append((bbox, text))
            else:
                current.sort(key=lambda r: r[0][0][0])
                lines.append(" ".join(t for _, t in current))
                current = [(bbox, text)]
                last_y = y

        if current:
            current.sort(key=lambda r: r[0][0][0])
            lines.append(" ".join(t for _, t in current))

        return "\n".join(lines)

