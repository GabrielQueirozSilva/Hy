from pymongo import MongoClient
import os
from bson import ObjectId
import os
from dotenv import load_dotenv
import sys

from I_A_H.parser.item_parser import parse_item_data

load_dotenv() 

collection = "heat_collection"
collection2 = "divan_colection"
collection3 = "divan_collection_lote01" #"geral_collection"

class Extrator:
    
    def __init__(self, uri=None, db_name=None):
        uri = uri or os.getenv("MONGO_URI")
        db_name = db_name or os.getenv("MONGO_DB")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def extrair_dados(self, collection_name=collection3): 
        collection = self.db[collection_name]
        documentos = []

        for doc in collection.find({}):
            doc["_id"] = str(doc["_id"]) 
            documentos.append(doc)

        return documentos

def individual():
    extrator = Extrator()
    dados_extraidos = extrator.extrair_dados()
    id = "69c9b8d4d77aac6fd320cdea"
    for dado in dados_extraidos: 
        if dado["_id"] == id:
            # os.system('clear || cls')
            item_data, sanitized_text = parse_item_data(dado["raw_text"])
            return item_data, dado['parsed'],id,sanitized_text
 
 
def completo():
   extrator = Extrator()
   dados_extraidos = extrator.extrair_dados()
   resultados = []
   for dado in dados_extraidos:
    #    os.system('clear || cls')
       if dado["etl_status"] == "quarantine":
            item_data, sanitized_text = parse_item_data(dado["raw_text"])
            if item_data != dado['parsed']:
                resultados.append((item_data, dado['parsed'], str(dado["_id"]), sanitized_text))
   
   return resultados

if __name__ == "__main__":
    
    print("Deseja rodar o teste individual ou completo? (i/c)")
    resposta = input().lower()
    if resposta == 'i':
        new, old, id, sanitized_text = individual()
        print(f"Texto Sanitizado:\n{sanitized_text}\n\n")
        print(f" \n\n\nATUAL:  item_data: {old}\n\n")
        print(f"NEW:\n Item: {new.get('name', 'N/A')}\n Tier: {new.get('tier', 'N/A')}\n Seller: {new.get('seller', 'N/A')}\n Price: {new.get('price', 'N/A')}\n Class: {new.get('class','N/A')}")
        print("\n\n\n")
        print("Deseja salvar os dados modificados? (s/n)")
        resposta = input().lower()
        if resposta == 's':
            print("Salvando dados modificados...")
            client = MongoClient(os.getenv("MONGO_URI"))
            db = client[os.getenv("MONGO_DB")]
            collection = db[collection]
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
    elif resposta == 'c':
        resultados = completo()
        for new, old, id, sanitized_text in resultados:
            print(f"Texto Sanitizado:\n{sanitized_text}\n\n")
            print(f" \n\n\nATUAL:  item_data: {old}\n\n")
            print(f"NEW:\n Item: {new.get('name', 'N/A')}\n Tier: {new.get('tier', 'N/A')}\n Seller: {new.get('seller', 'N/A')}\n Price: {new.get('price', 'N/A')}")
            print("\n\n\n")
            print("Deseja salvar os dados modificados? (s/n)")
            resposta = input().lower()
            if resposta == 's':
                print("Salvando dados modificados...")
                client = MongoClient(os.getenv("MONGO_URI"))
                db = client[os.getenv("MONGO_DB")]
                collection = db[collection3]
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
    else:
        print("Resposta inválida. Por favor, escolha 'i' para individual ou 'c' para completo.")
 