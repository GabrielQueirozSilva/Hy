from I_A_H.ETL.extract import Extrator
from I_A_H.ETL.transform import transformar_documento
from I_A_H.ETL.schemas import create_database_if_not_exists, create_tables, validar_item
from I_A_H.ETL.load import load_data
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

#Aqui é o código principal do ETL, ele roda todos os outros códigos para realizar o ETL

def run():
    #Primeiramente ele cria a base de dados e as tabelas, caso não existam no postgres,
    #essas funções vem do schemas.py
    create_database_if_not_exists()
    create_tables()

    #apos isto ele se conecta com o mongodb
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB")]
    collection = db[os.getenv("MONGO_COLLECTION_NAME")]

    #e então ele usa a classe extractor do extract.py para pegar os dados do mongodb,
    #para saber o formato dos dados leia a documentação presente no extract.py.
    extrator = Extrator()
    documentos_mongo = extrator.extrair_dados()
    print(f"{len(documentos_mongo)} documentos extraidos do MongoDB")


    #Nesta parte ele define quais dados são validos ou invalidos a partir do schemas.py
    # e transform.py
    validados = []

    for doc in documentos_mongo:
        try:
            #valida o documento e retorna o status e o motivo da invalidade
            is_valid, invalid_reason = validar_item(doc)
            #etiqueta o documento no mongodb com o status e o motivo
            transformado = transformar_documento(doc, is_valid, invalid_reason, collection)
            #adiciona o documento na lista de validados caso seja valido
            if is_valid:
                validados.append(transformado)
        except Exception as e:
            print(f"Erro ao processar documento {doc.get('_id')}: {e}")
    #apos tudo isto é informado no terminal como foi a execução do programa
    print(f"Validados: {len(validados)}")
    print(f"Quarentena/Rejeitados: {len(documentos_mongo) - len(validados)}")

    if validados:
        load_data(validados)

    client.close()
    print("ETL finalizado")

if __name__ == "__main__":
    run()