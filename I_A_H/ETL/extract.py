from pymongo import MongoClient

class Extrator:
    
    def __init__(self, uri="mongodb://localhost:27017", db_name="hypixel_scans"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def extrair_dados(self, collection_name="items"): #lembra de mudar items para raws_items dps
        collection = self.db[collection_name]
        documentos = []

        for doc in collection.find({}):
            doc["_id"] = str(doc["_id"])  # NORMALIZA A FRONTEIRA
            documentos.append(doc)

        return documentos
