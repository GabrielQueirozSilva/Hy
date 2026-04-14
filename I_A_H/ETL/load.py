import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()

def load_data(registros):
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        print(repr(e))
        return

    cur = conn.cursor()

    insert_query = """
    INSERT INTO auction_items (
        source_mongo_id,
        scan_timestamp,
        name,
        class,
        tier,
        price,
        seller,
        created_at
    )
    VALUES (
        %(source_mongo_id)s,
        %(scan_timestamp)s,
        %(name)s,
        %(class)s,
        %(tier)s,
        %(price)s,
        %(seller)s,
        %(created_at)s
    )
    ON CONFLICT (source_mongo_id) DO NOTHING;
    """

    for item in registros:
        cur.execute(insert_query, {
            "source_mongo_id": item["id"],
            "scan_timestamp": item.get("scan_timestamp"),
            "name": item["parsed"].get("name"),
            "class": item["parsed"].get("class"),
            "tier": item["parsed"].get("tier"),
            "price": item["parsed"].get("price"),
            "seller": item["parsed"].get("seller"),
            "created_at": datetime.utcnow()
        })

    conn.commit()
    cur.close()
    conn.close()
    print(f"{len(registros)} registros carregados no PostgreSQL")