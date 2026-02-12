import psycopg2

def validar_item(item: dict) -> tuple[bool, str | None]:
    parsed = item.get("parsed")

    if not isinstance(parsed, dict):
        return False, "PARSED_MISSING"
    
    if not parsed.get("name"):
        return False, "NAME_MISSING"
        
    if parsed.get("class") in (None, "Unknown"):
        return False, "CLASS_INVALID"

    if parsed.get("tier") in (None, "Unknown"):
        return False, "TIER_INVALID"
    
    price = parsed.get("price")
    if not isinstance(price, int) or price <= 0:
        return False, "PRICE_INVALID"
    
    return True, None



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
        is_valid BOOLEAN,
        invalid_reason TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)
    conn.commit()
    cur.close()
    conn.close()
