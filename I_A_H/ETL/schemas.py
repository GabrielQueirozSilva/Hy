"""
ETL - Schemas
=============

Parte responsável por definir as funções de validação dos dados extraídos do mongodb, além de criar a base de 
dados e as tabelas necessárias no postgres para o armazenamento dos dados transformados.

Routine List
------------
validar_item
    Função responsável por validar os dados extraídos do mongodb, retornando um Bool indicando a validade 
    dos dados e uma string indicando o motivo da invalidez, caso os dados sejam considerados inválidos.
create_database_if_not_exists
    Função responsável por criar a base de dados no postgres caso ela não exista.
create_tables
    Função responsável por criar as tabelas necessárias no postgres caso elas não existam.
"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv() 

# TODO: LEMBRA DE MUDAR O NOME DOS BANCOS DE DADOS

def validar_item(item: dict) -> tuple[bool, str | None]:
    """Função responsável por validar os dados extraídos do mongodb.
    
    Parameters
    ----------
    item: dict
        O item extraído do mongodb a ser validado.
    
    Returns
    -------
    tuple: bool, str | None
        Uma tupla contendo um Bool indicando a validade dos dados e uma string indicando o motivo da invalidez,
        caso os dados sejam considerados inválidos. Caso os dados sejam considerados válidos, a string será None.
    
    Notes
    -----
    Funciona principalmente usando o parsed nos dados, caso estiver faltando, já é considerado invalido
    """
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
    """Função responsável por criar a base de dados no postgres caso ela não exista.
    """
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
    """Função responsável por criar as tabelas necessárias no postgres caso elas não existam.
    
    Notes
    -----
    Ela armazena os dados principais do item.
    """
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
    CREATE TABLE IF NOT EXISTS sellers (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE,
        rank TEXT);
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS auction_items (
        id SERIAL PRIMARY KEY,
        source_mongo_id TEXT UNIQUE,
        scan_timestamp TIMESTAMP,
        name TEXT,
        class TEXT,
        tier TEXT,
        price BIGINT,
        seller_id INTEGER REFERENCES sellers(id),
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)   
    conn.commit()
    cur.close()
    conn.close()