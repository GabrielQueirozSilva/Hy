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

def transformar_documento(doc, valid, reason, collection):
    """Função principal para transformação dos dados.

    Parameters
    ----------
    doc: dict
        O documento do mongodb a ser transformado.
    valid: bool
        O estado de validade do documento (True caso seja válido, False caso contrário).
    reason: str
        A razão da invalidade do documento, pode ser None caso seja válido.
    collection: pymongo.collection.Collection
        A collection do mongodb para a modificação do documento.

    Returns
    -------
    dict
        Um dicionário contendo as informações principais do documento transformado, pronto para o armazenamento no
        postgres.

    Notes
    -----
    Esta função transforma os dados do mongodb diretamente.
    """
    item_data = doc.get("parsed", {})    
    if valid is True:
        etl_status = "validated"
    elif valid is False and reason != "PARSED_MISSING":
        etl_status = "quarantine"
    else:
        etl_status = "rejected"
    collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {
            "etl_status": etl_status,
            "etl_errors": reason
        }}
    )
    #A função retorna sempre o dado resumido (sem o raw e o sanitized), com as modificações feitas
    return {
        "id": str(doc.get("_id")),
        "scan_timestamp": doc.get("scan_timestamp"),
        "parsed": item_data
    }
