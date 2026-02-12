# storage/mongo.py
from pymongo import MongoClient

class MongoStorage:
    def __init__(self, uri="mongodb://localhost:27017"):
        self.client = MongoClient(uri)
        self.col = self.client["hypixel_scans"]["diva_colection"]

    def save(self, document: dict):
        self.col.insert_one(document)
