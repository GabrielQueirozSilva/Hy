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

import os
import psycopg2
from psycopg2 import sql, errors
from dotenv import load_dotenv

load_dotenv() 

# TODO: LEMBRA DE MUDAR O NOME DOS BANCOS DE DADOS


_PARAMS = dict(
    host=os.getenv("POSTGRES_HOST"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)


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
    
    if not parsed.get("name"):
        return False, "NAME_INVALID"
        
    if not parsed.get("class"):
        return False, "CLASS_INVALID"

    if not parsed.get("tier"):
        return False, "TIER_INVALID"
    
    price = parsed.get("price")
    if isinstance(price, bool) or not isinstance(price, int) or price <= 0:
        return False, "PRICE_INVALID"
    
    return True, None



def create_database_if_not_exists():
    """Função responsável por criar a base de dados no postgres caso ela não exista."""
    db = os.getenv("POSTGRES_DB")
    if not db:
        raise ValueError("POSTGRES_DB não definido")

    conn = psycopg2.connect(dbname="postgres", **_PARAMS)
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            try:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db)))
                print("Banco criado")
            except errors.DuplicateDatabase:
                pass
    finally:
        conn.close()

def create_tables():
    """Função responsável por criar as tabelas necessárias no postgres caso elas não existam."""
    conn = psycopg2.connect(dbname=os.getenv("POSTGRES_DB"), **_PARAMS)
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS sellers (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                rank TEXT
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS auction_items (
                id SERIAL PRIMARY KEY,
                source_mongo_id TEXT UNIQUE NOT NULL,
                scan_timestamp TIMESTAMP,
                name TEXT NOT NULL,
                class TEXT NOT NULL,
                tier TEXT NOT NULL,
                price BIGINT NOT NULL CHECK (price > 0),
                seller_id INTEGER REFERENCES sellers(id),
                created_at TIMESTAMP DEFAULT NOW()
            );
            """)
    finally:
        conn.close()