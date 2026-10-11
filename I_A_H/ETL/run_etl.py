"""
Orquestrador Principal do ETL
=============================

Função principal do ETL, responsável por orquestrar as outras funções para o processo completo do ETL.

Routine List
------------
run
    Função principal utilizada para iniciar o ETL.
"""
from I_A_H.ETL.seller import agrupation
from I_A_H.ETL.extract import Extrator
from I_A_H.ETL.transform import classificar_status, marcar_status, transformar_documento
from I_A_H.ETL.schemas import create_database_if_not_exists, create_tables, validar_item
from I_A_H.ETL.load import load_data
from pymongo import MongoClient
import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def run():
    """Função principal utilizada para iniciar o ETL."""
    # Cria as bases caso não existam.
    create_database_if_not_exists()
    create_tables()

    client = MongoClient(os.getenv("MONGO_URI"))
    conn = None
    try:
        db = client[os.getenv("MONGO_DB")]
        collection = db[os.getenv("MONGO_COLLECTION_NAME")]

        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )

        extrator = Extrator()
        documentos_mongo = extrator.extrair_dados()
        print(f"{len(documentos_mongo)} documentos extraidos do MongoDB")

        validados, marcacoes = [], []
        rejeitados = erros = 0
        for doc in documentos_mongo:
            try:
                is_valid, reason = validar_item(doc)
                status = classificar_status(is_valid, reason)
                marcacoes.append((doc["_id"], status, reason))
                if is_valid:
                    validados.append(transformar_documento(doc))
                else:
                    rejeitados += 1
            except Exception as e:
                erros += 1
                print(f"Erro ao processar documento {doc.get('_id')}: {e}")

        print(f"Validados: {len(validados)}")
        print(f"Quarentena/Rejeitados: {rejeitados}")
        print(f"Erros de processamento: {erros}")

        if validados:
            with conn, conn.cursor() as cur:  
                agrupation(validados, cur)
                load_data(validados, cur)
        marcar_status(collection, marcacoes)
        print("ETL finalizado")
    finally:
        if conn is not None:
            conn.close()
        client.close()

if __name__ == "__main__":
    run()