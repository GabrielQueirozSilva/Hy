from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class Extrator:
    
    def __init__(self, uri=None, db_name=None):
        uri = uri or os.getenv("MONGO_URI")
        db_name = db_name or os.getenv("MONGO_DB")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def extrair_dados(self, collection_name=None):
        collection_name = collection_name or os.getenv("MONGO_COLLECTION_NAME")
        collection = self.db[collection_name]
        return list(collection.find({}))