import psycopg2

def validar_item(item: dict) -> bool:
    parsed = item.get("parsed", {})

    obrigatorios = [
        "name",
        "class",
        "item_tier",
        "price"
    ]

    for campo in obrigatorios:
        if campo not in parsed:
            return False

    if not isinstance(parsed["price"], int):
        return False

    if parsed["price"] <= 0:
        return False

    if parsed["class"] == "Unknown":
        return False

    if parsed["item_tier"] == "Unknown":
        return False

    return True


def create_database_if_not_exists():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",  
            user="postgres",
            password="gabrielqs7"  
        )
        
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return
    
    conn.autocommit = True #PRECISA POR ISSO PARA DESLIGAR AS TRANSAÇÕES AUTOMATICAMENTE
    
    cur = conn.cursor()

    cur.execute("""
        SELECT 1 FROM pg_database WHERE datname = 'i_a_h_db';
    """)
    exists = cur.fetchone()

    if not exists:
        cur.execute("CREATE DATABASE i_a_h_db;")
        print(" Banco i_a_h_db criado")
    else:
        pass

    conn.commit()
    cur.close()
    conn.close()

def create_tables():
    
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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS auction_items_valid (
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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS auction_items_invalid (
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
    conn.commit()
    cur.close()
    conn.close()
