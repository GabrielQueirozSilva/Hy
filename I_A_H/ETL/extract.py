from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
## Parte referente a extração dos dados do mongo db, ele usa o MONGO_URI e o MONGO_DB para
#efetuar isso 


class Extrator:
    
    def __init__(self, uri=None, db_name=None):
        #init da função o qual é estabelecida a coneção com o mongodb
        uri = uri or os.getenv("MONGO_URI")
        db_name = db_name or os.getenv("MONGO_DB")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def extrair_dados(self, collection_name=None):
        # Retorna todos os documentos da collection, incluindo os já processados.
        # Duplicatas são tratadas pelo ON CONFLICT do load.py
        # A estrutura de cada documento é:
        # '__id': Objecid('id')
        #'scan_timestamp': 'anomesdia_time'
        #'raw_text': string
        #'sanitized_text': string
        #'parsed': {'name': string, 'tier': string, 'seller': string, 'price': int, 'class': string }
        #'bbox': list
        #'confidence': float
        #'etl_erros': None/string (PARSED_INVALID, NAME_INVALID, CLASS_INVALID, TIER_INVALID, PRICE_INVALID)
        #'etl_status': string (validated, quarantine, rejected)
        collection_name = collection_name or os.getenv("MONGO_COLLECTION_NAME")
        collection = self.db[collection_name]
        return list(collection.find({}))
    