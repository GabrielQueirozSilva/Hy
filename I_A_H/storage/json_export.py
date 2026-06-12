"""
Módulo para exportar documentos de detecção em formato JSON.
===========================================================
Este módulo fornece uma função para salvar um documento de detecção em um arquivo JSON. 

Routine_List
------------
save_json
    Salva um documento de detecção em um arquivo JSON, garantindo que o campo "_id" seja removido para compatibilidade com JSON.

"""
import json
import os


def save_json(document: dict, folder="detections_divan_new"):
    """Função para salvar o documento de detecção em um arquivo JSON
    
    Parameters
    ----------
    document: dict
        O documento de detecção a ser salvo.
    folder: str
        O nome da pasta onde o arquivo JSON será salvo. O padrão é "detections_divan_new".
    """
    os.makedirs(folder, exist_ok=True)
    filename = f"detection_{document['scan_timestamp']}.json"
    path = os.path.join(folder, filename)

    json_safe = document.copy()
    json_safe.pop("_id", None)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_safe, f, ensure_ascii=False, indent=2)

    print(f"JSON salvo: {path}")
