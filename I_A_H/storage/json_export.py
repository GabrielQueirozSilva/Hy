# storage/json_export.py
import json
import os

def save_json(document: dict, folder="detections_divan"):
    os.makedirs(folder, exist_ok=True)
    filename = f"detection_{document['scan_timestamp']}.json"
    path = os.path.join(folder, filename)

    json_safe = document.copy()
    json_safe.pop("_id", None)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_safe, f, ensure_ascii=False, indent=2)

    print(f"💾 JSON salvo: {path}")
