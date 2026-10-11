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
from I_A_H.ETL.seller import extrair_vendor_rank, vendor_valido, encontrar_seller

def carregar_sellers(cur):
    """Carrega (id, name) de todos os vendedores uma única vez."""
    cur.execute("SELECT id, name FROM sellers")
    return cur.fetchall()


def resolver_seller_id(seller_raw, sellers, cache):
    """Retorna o id do vendedor mais similar acima do limiar, ou None."""
    vendor, _ = extrair_vendor_rank(seller_raw)
    if not vendor_valido(vendor):
        return None
    if vendor not in cache:
        cache[vendor] = encontrar_seller(vendor, sellers)
    return cache[vendor]


def load_data(registros, cur):
    insert_query = """
    INSERT INTO auction_items (
        source_mongo_id, scan_timestamp, name, class, tier, price, seller_id
    )
    VALUES (
        %(source_mongo_id)s, %(scan_timestamp)s, %(name)s,
        %(class)s, %(tier)s, %(price)s, %(seller_id)s
    )
    ON CONFLICT (source_mongo_id) DO NOTHING;
    """
    sellers = carregar_sellers(cur)
    cache = {}
    inserted = skipped = sem_vendedor = 0

    for item in registros:
        parsed = item["parsed"]
        seller_id = resolver_seller_id(parsed.get("seller"), sellers, cache)
        cur.execute(insert_query, {
            "source_mongo_id": str(item["id"]),
            "scan_timestamp": item.get("scan_timestamp"),
            "name": parsed.get("name"),
            "class": parsed.get("class"),
            "tier": parsed.get("tier"),
            "price": parsed.get("price"),
            "seller_id": seller_id,
        })
        if cur.rowcount == 1:
            inserted += 1
            if seller_id is None:
                sem_vendedor += 1
        else:
            skipped += 1

    print(f"{inserted} registros inseridos | {skipped} já existiam (ignorados)")
    print(f"{sem_vendedor} inseridos sem vendedor associado")