from collections import Counter
import psycopg2
from dotenv import load_dotenv
import os
import pandas as pd
from difflib import SequenceMatcher
import re
from ..constants import *

load_dotenv()

def normalizar(nome):
    return re.sub(r"[^a-z0-9]", "", nome.lower())  # remove tudo que não é letra ou número

# 4. Deduplica por similaridade
def similaridade(a, b):
    return SequenceMatcher(None, normalizar(a), normalizar(b)).ratio()

def deduplicar_vendedores(resultado, threshold=0.85):
    registros = resultado
    removidos = set()
    for i, principal in enumerate(registros):
        if i in removidos:
            continue
        for j, duplicado in enumerate(registros):
            if i == j or j in removidos:
                continue
            sim = similaridade(principal["vendedor"], duplicado["vendedor"])
            if sim >= threshold:
                if i != registros.index(principal):
                    registros[i] = principal
                principal["ranks_list"] = principal.get("ranks_list", [principal["rank"]]) + \
                                          duplicado.get("ranks_list", [duplicado["rank"]])
                principal["rank"] = Counter(principal["ranks_list"]).most_common(1)[0][0]
                removidos.add(j)
                # print(f'Mesclado: "{duplicado["vendedor"]}" → "{principal["vendedor"]}"')
    
    resultado = [r for i, r in enumerate(registros) if i not in removidos]
    for r in resultado:
        r.pop("ranks_list", None)
    
    return resultado

def persistir_sellers(vendedores, cur):
    cur.execute("SELECT id, name FROM sellers")
    existentes = cur.fetchall()
    
    for v in vendedores:
        match_id = None
        for seller_id, seller_name in existentes:
            if similaridade(v["vendedor"], seller_name) >= SIMILARITY_THRESHOLD:
                match_id = seller_id
                break
        
        if match_id:
            cur.execute("UPDATE sellers SET rank = %s WHERE id = %s", (v["rank"], match_id))
        else:
            cur.execute("INSERT INTO sellers (name, rank) VALUES (%s, %s)", (v["vendedor"], v["rank"]))

def agrupation(doc, cur):
    resultado = []
    for item in doc:
        vendor, rank = extrair_vendor_rank(item["parsed"].get("seller"))
        resultado.append({"vendedor": vendor, "rank": rank, "ranks_list": [rank]})
    
    vendedores = deduplicar_vendedores(resultado, SIMILARITY_THRESHOLD)
    persistir_sellers(vendedores, cur)
    return vendedores

def extrair_vendor_rank(raw):
    vendor = raw or "indisponivel"
    rank = "sem rank"
    if vendor.startswith("[") and "]" in vendor:
        rank = vendor[1:vendor.index("]")]
        vendor = vendor[vendor.index("]")+1:].strip()
    return vendor, rank