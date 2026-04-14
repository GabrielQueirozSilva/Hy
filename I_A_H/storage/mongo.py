# storage/mongo.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv() 

class MongoStorage:
    def __init__(self, uri=None, db_name=None, co=None):
        uri = uri or os.getenv("MONGO_URI")
        db_name = db_name or os.getenv("MONGO_DB")
        co = co or os.getenv("MONGO_COLLECTION_NAME")
        self.client = MongoClient(uri)
        self.col = self.client[db_name][co]

    def save(self, document: dict):
        self.col.insert_one(document)
