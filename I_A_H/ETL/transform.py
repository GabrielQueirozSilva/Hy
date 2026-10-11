""" 
ETL - Transform
===================

Parte responsável por transformar os dados extraídos do mongodb, 
transformando-os em um formato adequado para o armazenamento no postgres, além de etiquetar os dados de acordo com a
sua situação atual, podendo ser validado, em quarentena ou rejeitado.

Routine List
------------
transformar_documento
    É a função que transforma os dados de acordo com o necessario.

Notes
-----
Existem 3 etiquetas principais para os dados: 
- Validated: Dados que foram considerados válidos e prontos para serem armazenados no postgres.
- Quarantine: Dados que foram considerados inválidos, mas que possuem informações suficientes para serem corrigidos
manualmente no mongodb.
- Rejected: Dados que foram considerados inválidos e que não possuem informações suficientes para serem corrigidos, 
sendo assim, aguardando para serem apagados do mongodb.
"""

from pymongo import UpdateOne

# Motivos de invalidez sem informação suficiente para correção manual.
MOTIVOS_REJEITADOS = {"PARSED_INVALID"}

def classificar_status(valid, reason):
    """Retorna 'validated', 'quarantine' ou 'rejected'."""
    if valid:
        return "validated"
    if reason in MOTIVOS_REJEITADOS:
        return "rejected"
    return "quarantine"


def transformar_documento(doc):
    """Retorna o documento resumido (sem raw/sanitized), pronto para a carga."""
    return {
        "id": str(doc["_id"]),
        "scan_timestamp": doc.get("scan_timestamp"),
        "parsed": doc.get("parsed") or {},
    }
    
def marcar_status(collection, marcacoes):
    """Grava etl_status e etl_errors no Mongo em uma única operação em lote.

    marcacoes: lista de tuplas (_id, status, reason).
    """
    if not marcacoes:
        return
    ops = [
        UpdateOne({"_id": _id}, {"$set": {"etl_status": status, "etl_errors": reason}})
        for _id, status, reason in marcacoes
    ]
    collection.bulk_write(ops, ordered=False)