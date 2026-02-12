from pymongo import MongoClient
import os

from I_A_H.parser.item_parser import parse_item_data

class Extrator:
    
    def __init__(self, uri="mongodb://localhost:27017", db_name="hypixel_scans"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def extrair_dados(self, collection_name="divan_colection"): 
        collection = self.db[collection_name]
        documentos = []

        for doc in collection.find({}):
            doc["_id"] = str(doc["_id"]) 
            documentos.append(doc)

        return documentos

#errado
# 69856a69522ed0d0b0e173e2
#correto
# 698569c6c200b2b7a04fd418
def main():
    extrator = Extrator()
    dados_extraidos = extrator.extrair_dados()
    id = "69856ae6522ed0d0b0e173eb"
    for dado in dados_extraidos:        
        if dado["_id"] == id:
            os.system('clear || cls')
            print(f" \n\n\nATUAL:  item_data: {dado['parsed']}\n\n")
            item_data, sanitized_text = parse_item_data(dado["raw_text"])
            print(f"NEW:\n Item: {item_data.get('name', 'N/A')}\n Tier: {item_data.get('tier', 'N/A')}\n Seller: {item_data.get('seller', 'N/A')}\n Price: {item_data.get('price', 'N/A')}")
            return
 

if __name__ == "__main__":
    main()