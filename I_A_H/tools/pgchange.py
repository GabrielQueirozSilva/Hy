import psycopg2
from dotenv import load_dotenv
import os
from I_A_H.parser.sanitizer import item_sanitizer

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
    raise

cur = conn.cursor()

# 1. Busca só o necessário
cur.execute("SELECT id, seller FROM auction_items")
rows = cur.fetchall()

# 2. Aplica o sanitizer em cada seller individualmente
atualizacoes = []
for id_, seller in rows:
    if seller is not None:
        seller_corrigido = item_sanitizer(seller, context="SELLER")
        atualizacoes.append((seller_corrigido, id_))

# 3. Atualiza no banco
cur.execute("BEGIN")
cur.executemany("UPDATE auction_items SET seller = %s WHERE id = %s", atualizacoes)

# Ver os primeiros 10 para conferir
for seller_novo, id_ in atualizacoes[:10]:
    print(f"ID {id_}: {seller_novo}")

conn.commit()

print(f"{len(atualizacoes)} registros atualizados.")
cur.close()
conn.close()