from pymongo import MongoClient
import os
from bson import ObjectId

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
    id = "69856ad5522ed0d0b0e173ea"
    for dado in dados_extraidos:        
        if dado["_id"] == id:
            os.system('clear || cls')
            item_data, sanitized_text = parse_item_data(dado["raw_text"])
            return item_data, dado['parsed'],id,sanitized_text
 

if __name__ == "__main__":
    new, old, id, sanitized_text = main()
    print(f"Texto Sanitizado:\n{sanitized_text}\n\n")
    print(f" \n\n\nATUAL:  item_data: {old}\n\n")
    print(f"NEW:\n Item: {new.get('name', 'N/A')}\n Tier: {new.get('tier', 'N/A')}\n Seller: {new.get('seller', 'N/A')}\n Price: {new.get('price', 'N/A')}")
    print("\n\n\n")
    print("deseja salvar os dados modificados? (s/n)")
    resposta = input().lower()
    if resposta == 's':
        print("Salvando dados modificados...")
        client = MongoClient("mongodb://localhost:27017")
        db = client["hypixel_scans"]
        collection = db["divan_colection"]
        filter_query = {"_id": ObjectId(id)}
        update_data = {"$set": {"parsed": new}}
        result = collection.update_one(filter_query, update_data)
        if result.modified_count > 0:
            print("Dados modificados com sucesso!")
        else:
            print("matched:", result.matched_count)
            print("modified:", result.modified_count)
    else:
        print("Modificações descartadas.")