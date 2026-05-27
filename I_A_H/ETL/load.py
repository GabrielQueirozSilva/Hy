import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()
#Aqui ele carrega os dados carregados do mongodb no postgress, ele não chama o mongodb
#pois o progama somente pega os dados carregados localmente pelo extract.py e joga no mongo

def load_data(registros):
    #Essa função funciona da seguinte forma:
    #Primeiramente ela tenta conectar com o postgres
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

    #ao conectar ele prepara os comandos de inserção para adicionar os novos dados, definindo
    # quais dados seram adicionados
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
    #esse on conflict serve para não inserir dados repetidos
    
    #essas váriaveis servem para contar quantos dados foram adicionados(inserted)
    #e quantos foram pulado (skipped)
    inserted = 0
    skipped = 0

    #loop responsavel pela execução da query definida anteriormente e contagem das váriaveis
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
        if cur.rowcount == 1:
            inserted += 1
        else:
            skipped += 1

    #fechamento da conexão e emissão das informações no terminal
    conn.commit()
    cur.close()
    conn.close()
    print(f"{inserted} registros inseridos | {skipped} já existiam (ignorados)")