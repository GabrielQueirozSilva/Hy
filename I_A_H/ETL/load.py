"""
ETL - Load
===================

Parte responsável por carregar os dados transformados para o banco de dados postgres, evitando a inscrição de dados duplicados.

Routine List
------------
load_data
    Função principal para carregar os dados transformados para o banco de dados postgres.
    
Notes
-----
O programa não chama o mongodb diretamente, ele somente pega os dados carregados localmente pelo extract.py e joga no postgres.
"""
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os
from I_A_H.ETL.seller import similaridade, SIMILARITY_THRESHOLD, extrair_vendor_rank
load_dotenv()

def resolver_seller_id(seller_raw, cur):
    vendor, _ = extrair_vendor_rank(seller_raw)
    if not vendor or vendor == "indisponivel":
        return None
    cur.execute("SELECT id, name FROM sellers")
    existentes = cur.fetchall()
    for seller_id, name in existentes:
        if similaridade(vendor, name) >= SIMILARITY_THRESHOLD:
            return seller_id
    return None


def load_data(registros, cur):
    insert_query = """
    INSERT INTO auction_items (
        source_mongo_id,
        scan_timestamp,
        name,
        class,
        tier,
        price,
        seller_id,
        created_at
    )
    VALUES (
        %(source_mongo_id)s,
        %(scan_timestamp)s,
        %(name)s,
        %(class)s,
        %(tier)s,
        %(price)s,
        %(seller_id)s,
        %(created_at)s
    )
    ON CONFLICT (source_mongo_id) DO NOTHING;
    """
    inserted = 0
    skipped = 0
    for item in registros:
        cur.execute(insert_query, {
            "source_mongo_id": item["id"],
            "scan_timestamp": item.get("scan_timestamp"),
            "name": item["parsed"].get("name"),
            "class": item["parsed"].get("class"),
            "tier": item["parsed"].get("tier"),
            "price": item["parsed"].get("price"),
            "seller_id": resolver_seller_id(item["parsed"].get("seller", ""), cur),
            "created_at": datetime.utcnow()
        })
        if cur.rowcount == 1:
            inserted += 1
        else:
            skipped += 1
    print(f"{inserted} registros inseridos | {skipped} já existiam (ignorados)")