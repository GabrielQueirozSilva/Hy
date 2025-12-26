import psycopg2
from datetime import datetime

def load_data(registros, validade):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="i_a_h_db",
            user="postgres",
            password="gabrielqs7"
        )
        
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return
    
    
    cur = conn.cursor()

    if validade:
        insert_query = """
        INSERT INTO auction_items_valid (
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
    else:
        insert_query = """
        INSERT INTO auction_items_invalid (
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
