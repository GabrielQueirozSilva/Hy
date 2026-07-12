"""
Orquestrador Principal do ETL
=============================

Função principal do ETL, responsável por orquestrar as outras funções para o processo completo do ELT.

Routine List
------------
run
    Função principal utilizada para iniciar o ETL.
"""
from I_A_H.ETL.seller import agrupation
from I_A_H.ETL.extract import Extrator
from I_A_H.ETL.transform import transformar_documento
from I_A_H.ETL.schemas import create_database_if_not_exists, create_tables, validar_item
from I_A_H.ETL.load import load_data
from pymongo import MongoClient
import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def run():
    """Função principal utilizada para iniciar o ETL.
    """
    #Cria as bases caso não existam.
    create_database_if_not_exists()
    create_tables()

    #Se conecta ao mongodb.
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB")]
    collection = db[os.getenv("MONGO_COLLECTION_NAME")]

    #Se conecta ao pg
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    cur = conn.cursor()

    #Extrai os dados do mongodb como uma LISTA de DICIONARIOS.
    extrator = Extrator()
    documentos_mongo = extrator.extrair_dados()
    print(f"{len(documentos_mongo)} documentos extraidos do MongoDB")

    #Valida os dados.
    validados = []
    for doc in documentos_mongo:
        try:
            is_valid, invalid_reason = validar_item(doc)
            #etiqueta o documento no mongodb com o status e o motivo
            transformado = transformar_documento(doc, is_valid, invalid_reason, collection)
            #adiciona o documento na lista de validados caso seja valido
            if is_valid:
                validados.append(transformado)
        except Exception as e:
            print(f"Erro ao processar documento {doc.get('_id')}: {e}")
    print(f"Validados: {len(validados)}")
    print(f"Quarentena/Rejeitados: {len(documentos_mongo) - len(validados)}")

    if validados:
        agrupation(validados, cur)
        conn.commit()
        load_data(validados, cur)
        conn.commit()

    client.close()
    print("ETL finalizado")

if __name__ == "__main__":
    run()