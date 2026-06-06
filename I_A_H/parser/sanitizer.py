"""
Modulo responsável por refinar os texto identificado e remover erros comuns
============================================================================

Esse modulo é o responsável por refinar o texto identificado e digitalizado pelo OCR, ele funciona com a ajuda do constants.py e é utilizado sempre como função secundária.
Ele é necessário pois a fonte original do texto ocasiona muitos erros de indentificação nas palavras e ele corrige tanto momentos específicos, quanto o texto como um todo.

Routine List
------------
normalize_ocr
    Normaliza o texto Unicode e remove falsos espaços.
item_sanitizer
    Aplica correções específicas com base no contexto (GLOBAL, NAME, PRICE, SELLER).
    
Examples
--------
>>> from meu_projeto import sanitizer
>>> texto_refinado = sanitizer.item_sanitizer("TEXTO_BRUTO_AQUI", context="GLOBAL")
>>> print(texto_refinado)

Notes
-----
Este módulo depende diretamente das constantes de validação definidas definidas no arquivo constants.py.

"""
from ..constants import *
import unicodedata
import re

def normalize_ocr(text):
    """Esta função normaliza o texto Unicode a forma NFKD e remove falsos espaços comuns em textos extraídos por OCR

    Parameters
    ----------
    text: str
        O texto cru extraído pelo OCR.

    Returns
    -------
    str
        O texto normalizado.
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.replace('\u200b', '')
    text = text.replace('\xa0', ' ')
    return text

def item_sanitizer(text, context="GLOBAL"):
    """Aplica correções específicas com base no contexto (GLOBAL, NAME, PRICE, SELLER).
    
    Parameters
    ----------
    text: str
        O texto a ser refinado.
    context: str
        O contexto para aplicar correções específicas. Pode ser "GLOBAL", "NAME", "PRICE" ou "SELLER". O padrão é "GLOBAL".
        
    Returns
    -------
    str 
        O texto refinado.
    
    Notes
    -----
    - "GLOBAL": Aplica correções gerais em todo o texto.
    - "NAME": Aplica correções específicas para o nome do item.
    - "PRICE": Aplica correções específicas para o preço do item.
    - "SELLER": Aplica correções específicas para o nome do vendedor.
    """
    if not text: return ""
    text = normalize_ocr(text)

    # 1. Aplica correções GLOBAIS (Sempre roda)
    if context == "GLOBAL":
        linhas = text.splitlines()
        linhas_filtradas = []
        #joga fora tudo depois de click to inspect
        for i, linha in enumerate(linhas):
            l = linha.lower().strip()
            
            if "click" in l and "inspect" in l:
                # mantém a linha do click to inspect
                linhas = linhas[:i+1]
                break

        #remove ruidos como linhas vazias, pequenas demais
        for linha in linhas:
            limpa = linha.strip()

            if not limpa:
                continue
            if len(limpa) <= 5:
                continue
            if re.fullmatch(r"[\W_]+", limpa):
                continue

            linhas_filtradas.append(linha)
        text = "\n".join(linhas_filtradas)

        #correções usando o constants.py
        text = text.replace(',', '')
        for erro, correcao in GLOBAL_REPLACEMENTS.items():
            text = re.sub(re.escape(erro), correcao, text, flags=re.IGNORECASE)            
                # --- Lógica de troca de números ---
        # Z/z no inicio de numeros vira 2 (Z000 -> 2000)
        text = re.sub(r'\b[Zz](?=[\d,])', '2', text)
        # S no inicio de numeros vira 5 (S00 -> 500)
        text = re.sub(r'\b[Ss](?=[\d,])', '5', text)
           
    elif context == "NAME":
        for erro, correcao in NAMES_REPLACEMENTS.items():
            text = re.sub(re.escape(erro), correcao, text, flags=re.IGNORECASE)
            
    elif context == "PRICE":
        # Aplica dicionário de preços
        for erro, correcao in PRICE_REPLACEMENTS.items():
            text = re.sub(re.escape(erro), correcao, text, flags=re.IGNORECASE)
            
        #O/o vira 0
        text = re.sub(r'\b[Oo](?=[\d,])', '0', text)
        text = re.sub(r'(?<=0)[Qq](?=0)', '0', text)

        # # Limpeza de relógio (@Zn -> 2h)
        # text = re.sub(r'@\s*[Zz]', '2', text)
        # text = re.sub(r'@\s*[Ss]', '5', text)

    elif context == "SELLER":
        for erro, correcao in SELLER_REPLACEMENTS.items():
            text = re.sub(re.escape(erro), correcao, text, flags=re.IGNORECASE)
    return text.lower()