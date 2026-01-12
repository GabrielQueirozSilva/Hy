import psycopg2

def validar_item(item: dict) -> bool:
    parsed = item.get("parsed")

    if not isinstance(parsed, dict):
        return False

    obrigatorios = ["name", "class", "tier", "price"]

    for campo in obrigatorios:
        if campo not in parsed:
            return False

    if not isinstance(parsed["name"], str) or not parsed["name"].strip():
        return False

    if not isinstance(parsed["class"], str) or parsed["class"] == "Unknown":
        return False

    if not isinstance(parsed["tier"], str) or parsed["tier"] == "Unknown":
        return False

    if not isinstance(parsed["price"], int) or parsed["price"] <= 0:
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
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)
    conn.commit()
    cur.close()
    conn.close()
