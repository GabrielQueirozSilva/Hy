import json
import os
from pymongo import MongoClient
name = "detections_divan"


class MongoStorage:
    def __init__(self, uri="mongodb://localhost:27017"):
        self.client = MongoClient(uri)
        self.col = self.client["hypixel_scans"]["diva_colection"]

    def save(self, document: dict):
        self.col.insert_one(document)

    def save_many(self, documents: list):
        self.col.insert_many(documents)


def read_all_jsons(folder: str = name) -> list[dict]:
    all_data = []
    
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            filepath = os.path.join(folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_data.append(data)
    
    return all_data


def main():
    data = read_all_jsons()
    mongo = MongoStorage()
    mongo.save_many(data)


if __name__ == "__main__":
    main()