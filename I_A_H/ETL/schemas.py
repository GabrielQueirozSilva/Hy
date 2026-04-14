import psycopg2
from dotenv import load_dotenv
import os

load_dotenv() 

#LEMBRA DE MUDAR O NOME DOS BANCOS DE DADOS

def validar_item(item: dict) -> tuple[bool, str | None]:
    parsed = item.get("parsed")

    if not isinstance(parsed, dict):
        return False, "PARSED_MISSING"
    
    if parsed.get("name") is None:
        return False, "NAME_MISSING"
        
    if parsed.get("class") is None:
        return False, "CLASS_INVALID"

    if parsed.get("tier") is None:
        return False, "TIER_INVALID"
    
    price = parsed.get("price")
    if not isinstance(price, int) or price <= 0:
        return False, "PRICE_INVALID"
    
    return True, None



def create_database_if_not_exists():
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
    
    conn.autocommit = True #PRECISA POR ISSO PARA DESLIGAR AS TRANSAÇÕES AUTOMATICAMENTE
    
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname =%s;",(os.getenv("POSTGRES_DB"),))
    exists = cur.fetchone()

    if not exists:
        cur.execute("CREATE DATABASE %s;",(os.getenv("POSTGRES_DB"),))
        print(" Banco criado")
    else:
        pass

    conn.commit()
    cur.close()
    conn.close()

def create_tables():
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
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)
    conn.commit()
    cur.close()
    conn.close()