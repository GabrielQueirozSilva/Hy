import psycopg2
from datetime import datetime

def load_data(registros):
    conn = psycopg2.connect(
        host="localhost",
        database="I_A_H_DB",
        user="postgres",
        password="gabrielqs7"
    )
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS auction_items (
        id SERIAL PRIMARY KEY,
        source_mongo_id TEXT UNIQUE,
        scan_timestamp TIMESTAMP,
        name TEXT,
        class TEXT,
        tier TEXT,
        price BIGINT,
        seller TEXT,
        confidence FLOAT,
        is_valid BOOLEAN,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)

    insert_query = """
    INSERT INTO auction_items (
        source_mongo_id,
        scan_timestamp,
        name,
        class,
        tier,
        price,
        seller,
        confidence,
        is_valid,
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
        %(confidence)s,
        %(is_valid)s,
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
            "tier": item["parsed"].get("item_tier"),
            "price": item["parsed"].get("price"),
            "seller": item["parsed"].get("seller"),
            "confidence": item.get("confidence"),
            "is_valid": item.get("is_valid", True),
            "created_at": datetime.utcnow()
        })

    conn.commit()
    cur.close()
    conn.close()

    print(f"{len(registros)} registros carregados no PostgreSQL")
