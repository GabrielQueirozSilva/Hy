import psycopg2
from dotenv import load_dotenv
import os

load_dotenv() 

# TODO: LEMBRA DE MUDAR O NOME DOS BANCOS DE DADOS

#Arquivo responsavel por definir se os dados são validos ou não e caso não sejam, retornar
# o motivo da invalides. Ele retorna um Bool e str/None

def validar_item(item: dict) -> tuple[bool, str | None]:
    #ele funciona principalmente pela parte do parsed que existe no dados, no caso
    #de estiver faltando algo, o código indentifica e retorna o motivo da invalidez para
    #a eventual verificação
    parsed = item.get("parsed")

    if not isinstance(parsed, dict):
        return False, "PARSED_INVALID"
    
    if parsed.get("name") is None:
        return False, "NAME_INVALID"
        
    if parsed.get("class") is None:
        return False, "CLASS_INVALID"

    if parsed.get("tier") is None:
        return False, "TIER_INVALID"
    
    price = parsed.get("price")
    if not isinstance(price, int) or price <= 0:
        return False, "PRICE_INVALID"
    
    return True, None



def create_database_if_not_exists():
    #verifica se existe uma base de dados e depois
    #cria uma base de dados no posgress caso não tenha sido feita nenhuma
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
    
    conn.autocommit = True 
    
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname =%s;",(os.getenv("POSTGRES_DB"),))
    exists = cur.fetchone()

    if not exists:
        cur.execute("CREATE DATABASE %s;",(os.getenv("POSTGRES_DB"),))
        print(" Banco criado")

    conn.commit()
    cur.close()
    conn.close()

def create_tables():
    # Cria a tabela auction_items no postgres caso ela não exista.
    # Ela armazena os dados principais dos itens escaneados, sendo eles:
    # id, source_mongo_id, scan_timestamp, name, class, tier, price, seller, created_at
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