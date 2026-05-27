import json
import os
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import sys

load_dotenv() 

pasta = "detections_divan_lote02"

class MongoStorage:
    def __init__(self, uri=None, db=None, collection=None):
        uri = uri or os.getenv("MONGO_URI")
        db = db or os.getenv("MONGO_DB")
        collection = collection or os.getenv("MONGO_COLLECTION_NAME")
        self.client = MongoClient(uri)
        self.col = self.client[db][collection]

    def save(self, document: dict):
        self.col.insert_one(document)

    def save_many(self, documents: list):
        self.col.insert_many(documents)


def read_all_jsons(folder: str = pasta) -> list[dict]:
    all_data = []
    
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            filepath = os.path.join(folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_data.append(data)
    
    return all_data


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else pasta
    data = read_all_jsons(folder)
    mongo = MongoStorage()
    mongo.save_many(data)


if __name__ == "__main__":
    main()