from ..constants import *
import unicodedata
import re

def normalize_ocr(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.replace('\u200b', '')
    text = text.replace('\xa0', ' ')
    return text

def item_sanitizer(text, context="GLOBAL"):
    if not text: return ""
    text = normalize_ocr(text)


    # 1. Aplica correções GLOBAIS (Sempre roda)
        # Troca ; por : e outras limpezas básicas
    if context == "GLOBAL":
        linhas = text.splitlines()
        linhas_filtradas = []

        for i, linha in enumerate(linhas):
            l = linha.lower().strip()

            if "click" in l and "inspect" in l:
                # mantém a linha do click to inspect
                linhas = linhas[:i+1]
                break

        for linha in linhas:
            limpa = linha.strip()

            # remove linhas vazias
            if not limpa:
                continue

            # remove linhas muito pequenas
            if len(limpa) <= 5:
                continue

            # remove linhas que são só símbolos
            if re.fullmatch(r"[\W_]+", limpa):
                continue

            linhas_filtradas.append(linha)

        text = "\n".join(linhas_filtradas)

        # continua o resto do GLOBAL
        text = text.replace(',', '')
        for erro, correcao in GLOBAL_REPLACEMENTS.items():
            text = re.sub(re.escape(erro), correcao, text, flags=re.IGNORECASE)
            
                # --- Lógica pesada de números ---
        # Z/z no inicio de numeros vira 2 (Z000 -> 2000)
        text = re.sub(r'\b[Zz](?=[\d,])', '2', text)
        # S no inicio de numeros vira 5 (S00 -> 500)
        text = re.sub(r'\b[Ss](?=[\d,])', '5', text)
        
    elif context == "NAME":
        for erro, correcao in NAMES_REPLACEMENTS.items():
            text = re.sub(re.escape(erro), correcao, text, flags=re.IGNORECASE)

    # 2. Lógica baseada no CONTEXTO
    elif context == "PRICE":
        # Aplica dicionário de preços
        for erro, correcao in PRICE_REPLACEMENTS.items():
            text = re.sub(re.escape(erro), correcao, text, flags=re.IGNORECASE)
            
        # O ou o vira 0
        text = re.sub(r'\b[Oo](?=[\d,])', '0', text)
        text = re.sub(r'(?<=0)[Qq](?=0)', '0', text)

        # # Limpeza de relógio (@Zn -> 2h)
        # text = re.sub(r'@\s*[Zz]', '2', text)
        # text = re.sub(r'@\s*[Ss]', '5', text)
    
    elif context == "SELLER":
        for erro, correcao in SELLER_REPLACEMENTS.items():
            text = re.sub(re.escape(erro), correcao, text, flags=re.IGNORECASE)

    return text