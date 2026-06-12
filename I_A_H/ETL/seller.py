import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os
import pandas as pd
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
    print(repr(e))
    pass


cur = conn.cursor()
cur.execute("SELECT id, seller FROM auction_items")
rows = cur.fetchall()
cur.close()

df = pd.DataFrame(rows, columns=["id", "vendor"])

df["rank"] = df["vendor"].str.extract(r"\[([^\]]+)\]") 
df["vendedor"] = df["vendor"].str.extract(r"\]\s*(.+)") 


resultado = df.groupby(["vendedor", "rank"]).agg(
    total_itens=("id", "count"),
    ids_itens=("id", list)
).reset_index()
resultado.to_csv("vendedores.csv", index=False)
print("RESULTADOS:")
print(resultado["vendedor"].tolist())

problemas = df[df["rank"].isna() | df["vendedor"].isna()]
print("\n\n\nPROBLEMAS:")
print(problemas["vendor"].tolist())