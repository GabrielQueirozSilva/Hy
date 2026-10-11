"""
ETL - Seller
============

Parte responsável por extrair, normalizar, deduplicar e persistir os vendedores (sellers) presentes
nos itens processados pelo ETL. Como o campo "seller" vem diretamente do OCR, ele costuma conter ruído
(prefixos de rank colados ao nome, pequenas variações de digitação causadas por erro de leitura), o que
exige uma etapa de agrupamento por similaridade antes da persistência no PostgreSQL.

Routine List
------------
normalizar
    Remove caracteres não alfanuméricos e normaliza a caixa do texto, para permitir comparação justa
    entre nomes de vendedores.
similaridade
    Calcula o grau de similaridade entre dois nomes de vendedores já normalizados.
deduplicar_vendedores
    Agrupa vendedores considerados duplicados (mesmo nome, mas com pequenas variações de OCR) em um
    único registro por similaridade.
persistir_sellers
    Insere novos vendedores na tabela `sellers` do PostgreSQL ou atualiza o rank de vendedores já
    existentes.
agrupation
    Função principal que orquestra a extração, deduplicação e persistência dos vendedores a partir de
    um lote de documentos.
extrair_vendor_rank
    Separa o rank (ex: "[MVP+]") do nome do vendedor a partir do texto bruto do campo seller.

Notes
-----
Este módulo depende da constante `SIMILARITY_THRESHOLD`, definida em `constants.py`, que determina o
limiar mínimo de similaridade (0 a 1) para dois nomes serem considerados o mesmo vendedor.

A extração de rank e nome (`extrair_vendor_rank`) é usada tanto no agrupamento em lote (`agrupation`)
quanto deve ser usada de forma consistente em qualquer outro ponto do sistema que resolva o `seller_id`
de um vendedor (ex: `load.py`), para evitar divergência entre o texto persistido e o texto usado na
comparação de similaridade.
"""
from collections import Counter
from difflib import SequenceMatcher
import re

from ..constants import SIMILARITY_THRESHOLD

SEM_RANK = "sem rank"
INDISPONIVEL = "indisponivel"

def normalizar(nome):
    """Remove caracteres não alfanuméricos e converte o texto para minúsculas.

    Parameters
    ----------
    nome: str
        O nome bruto do vendedor a ser normalizado.

    Returns
    -------
    str
        O nome normalizado, contendo apenas letras e números em minúsculas.

    Notes
    -----
    Esta normalização é utilizada exclusivamente para fins de comparação de similaridade entre nomes
    (`similaridade`), não sendo o texto persistido no banco de dados.
    """
    return re.sub(r"[^a-z0-9]", "", nome.lower())  # remove tudo que não é letra ou número


def similaridade(a, b):
    """Calcula o grau de similaridade entre dois nomes de vendedores.

    Parameters
    ----------
    a: str
        O primeiro nome a ser comparado.
    b: str
        O segundo nome a ser comparado.

    Returns
    -------
    float
        Um valor entre 0 e 1 representando o grau de similaridade entre os dois nomes, sendo 1 uma
        correspondência exata (após normalização) e 0 nenhuma similaridade.

    Notes
    -----
    Ambos os nomes são normalizados (via `normalizar`) antes da comparação, para que diferenças de
    capitalização ou pontuação causadas por erro de OCR não afetem o resultado.
    """
    return SequenceMatcher(None, normalizar(a), normalizar(b)).ratio()

def extrair_vendor_rank(raw):
    """Separa o rank e o nome do vendedor a partir do texto bruto do campo seller.

    Parameters
    ----------
    raw: str or None
        O texto bruto do campo seller, tipicamente no formato "[RANK] nome_do_vendedor". Pode ser None
        caso o item não possua um vendedor identificado.

    Returns
    -------
    tuple: str, str
        Uma tupla contendo o nome do vendedor (sem o prefixo de rank) e o rank extraído. Caso `raw` seja
        None ou vazio, o vendedor retornado é "indisponivel". Caso não seja encontrado um rank entre
        colchetes no início do texto, o rank retornado é "sem rank" e o texto original é mantido como
        vendedor.

    Notes
    -----
    Esta função deve ser utilizada de forma consistente em todo o sistema sempre que for necessário
    separar rank e nome a partir do texto bruto do seller — tanto na etapa de agrupamento (`agrupation`)
    quanto na resolução do `seller_id` durante a carga (`load.py`). Usar lógicas de extração divergentes
    nesses dois pontos causa incompatibilidade entre o texto persistido em `sellers` e o texto usado na
    busca por correspondência, resultando em vendedores órfãos ou duplicados.
    """
    vendor = str(raw).strip() if raw else ""
    if not vendor:
        return INDISPONIVEL, SEM_RANK
    rank = SEM_RANK
    if vendor.startswith("[") and "]" in vendor:
        rank = vendor[1:vendor.index("]")].strip() or SEM_RANK
        vendor = vendor[vendor.index("]") + 1:].strip()
    return vendor, rank

def vendor_valido(vendor):
    """Indica se o nome extraído é um vendedor real (não "indisponivel" e não vazio após normalizar)."""
    return vendor != INDISPONIVEL and bool(normalizar(vendor))

def encontrar_seller(vendor, sellers):
    """Retorna o id do vendedor mais similar acima do limiar, compartilhada com o load.py

    `sellers` é uma lista de tuplas (id, name). Usada tanto por persistir_sellers
    quanto pelo load.py, para garantir o mesmo critério nos dois pontos.
    """
    melhor_id, melhor_score = None, -1.0
    for seller_id, name in sellers:
        score = similaridade(vendor, name)
        if score >= SIMILARITY_THRESHOLD and score > melhor_score:
            melhor_id, melhor_score = seller_id, score
    return melhor_id

def _rank_mais_comum(ranks):
    reais = [r for r in ranks if r != SEM_RANK]
    return Counter(reais or ranks).most_common(1)[0][0]


def deduplicar_vendedores(resultado, threshold=0.85):
    """Agrupa vendedores duplicados (mesmo vendedor, nome levemente divergente) em um único registro.

    Parameters
    ----------
    resultado: list of dict
        Uma lista de dicionários, cada um representando um vendedor extraído de um item, contendo as
        chaves "vendedor" (nome) e "rank".
    threshold: float, optional
        O limiar mínimo de similaridade (entre 0 e 1) para que dois registros sejam considerados o
        mesmo vendedor. O padrão é 0.85.

    Returns
    -------
    list of dict
        A lista de vendedores após a deduplicação, contendo apenas um registro por vendedor único,
        com o rank mais frequente entre as ocorrências mescladas.

    Notes
    -----
    Quando dois ou mais registros são mesclados, o rank final do vendedor é definido pelo rank mais
    comum entre todas as ocorrências mescladas (via `Counter.most_common`), já que rank também é um
    campo sujeito a ruído de OCR e pode divergir entre detecções do mesmo vendedor.
    """
    registros = resultado
    removidos = set()
    for i, principal in enumerate(registros):
        if i in removidos:
            continue
        for j, duplicado in enumerate(registros):
            if i == j or j in removidos:
                continue
            if similaridade(principal["vendedor"], duplicado["vendedor"]) >= threshold:
                principal["ranks_list"] = (
                    principal.get("ranks_list", [principal["rank"]])
                    + duplicado.get("ranks_list", [duplicado["rank"]])
                )
                principal["rank"] = _rank_mais_comum(principal["ranks_list"])
                removidos.add(j)

    resultado = [r for i, r in enumerate(registros) if i not in removidos]
    for r in resultado:
        r.pop("ranks_list", None)
    return resultado

def persistir_sellers(vendedores, cur):
    """Insere vendedores novos ou atualiza o rank de vendedores já existentes na tabela `sellers`.

    Parameters
    ----------
    vendedores: list of dict
        Uma lista de dicionários já deduplicados, cada um contendo as chaves "vendedor" (nome) e "rank".
    cur: psycopg2.extensions.cursor
        O cursor de conexão ativo com o banco de dados PostgreSQL, utilizado para executar as consultas
        de leitura e escrita na tabela `sellers`.

    Notes
    -----
    A busca por vendedores já existentes é feita comparando cada vendedor da lista de entrada com todos
    os vendedores já persistidos na tabela `sellers`, utilizando o mesmo critério de similaridade
    (`SIMILARITY_THRESHOLD`) usado na deduplicação em lote. Caso nenhuma correspondência seja encontrada,
    um novo registro é inserido; caso contrário, apenas o rank do registro existente é atualizado.

    Esta função não realiza commit da transação — a responsabilidade de efetivar (ou reverter) as
    alterações no banco cabe à função chamadora.
    """
    cur.execute("SELECT id, name FROM sellers")
    existentes = cur.fetchall()

    for v in vendedores:
        match_id = encontrar_seller(v["vendedor"], existentes)
        if match_id is not None:
            if v["rank"] != SEM_RANK:  # não sobrescreve rank real com "sem rank"
                cur.execute("UPDATE sellers SET rank = %s WHERE id = %s", (v["rank"], match_id))
        else:
            cur.execute("INSERT INTO sellers (name, rank) VALUES (%s, %s)", (v["vendedor"], v["rank"]))

def agrupation(doc, cur):
    """Orquestra a extração, deduplicação e persistência dos vendedores a partir de um lote de itens.

    Parameters
    ----------
    doc: list of dict
        Uma lista de documentos de itens já processados, cada um contendo a chave "parsed", que por sua
        vez contém a chave "seller" com o texto bruto do vendedor (ex: "[MVP+] nome_do_vendedor").
    cur: psycopg2.extensions.cursor
        O cursor de conexão ativo com o banco de dados PostgreSQL, repassado para `persistir_sellers`.

    Returns
    -------
    list of dict
        A lista de vendedores únicos (já deduplicados) extraídos do lote de documentos, no formato
        {"vendedor": str, "rank": str}.

    Notes
    -----
    Esta é a função principal do módulo, chamada pelo orquestrador do ETL para processar os vendedores
    de um lote de itens antes (ou em conjunto com) a carga desses itens no PostgreSQL.
    """
    resultado = []
    for item in doc:
        vendor, rank = extrair_vendor_rank(item["parsed"].get("seller"))
        if not vendor_valido(vendor):
            continue
        resultado.append({"vendedor": vendor, "rank": rank, "ranks_list": [rank]})

    vendedores = deduplicar_vendedores(resultado, SIMILARITY_THRESHOLD)
    persistir_sellers(vendedores, cur)
    return vendedores