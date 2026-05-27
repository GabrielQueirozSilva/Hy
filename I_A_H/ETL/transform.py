#Essa parte é responsavel por tranformar os dados no mongodb, o qual são etiquetados de
#acordo com a situação deles atual, podendo o dado ser validated, o qual nesse caso
#é promovido para o postgres; quarantine, que são os que precisão de observação e correção
#manual direto no mongodb, muito utilizados para a melhoria do parser; E por fim o rejected
#que são dados inutilizaveis e que precisam ser apagados.  
 
def transformar_documento(doc, valid, reason, collection):
    #Nesta função é recebido: o dado para a analise, o estado de validade dele (TRUE/FALSE)
    #doc: Uma lista das informações do dado em si;
    #valid: Um bool do estado dele (True caso seja valido, False caso contrario);
    #reason: Razão da invalidade, pode vir null caso seja valido;
    #collection: a collection do mongodb para a modificação do dado;
    #Para mais informações sobre o dado, consulte o extract.py
    item_data = doc.get("parsed", {})
    #O item_data são as informações principais dos dados armazenadas, como nome, price e etc
    
    #Caso valid venha como true o dado é etiquetado como validated, oq significa que ele
    #não precisa de alterações, caso seja falso e a rasão seja diferente de parsed_missing
    # o dado fica em estado de quarentena esperando a correção;
    #Caso contrario é rejeitado e fica em espera para o apagamento dele
    if valid is True:
        etl_status = "validated"
    elif valid is False and reason != "PARSED_MISSING":
        etl_status = "quarantine"
    else:
        etl_status = "rejected"
    #Logo apos isto ele é atualizado diretamente no mongodb
    collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {
            "etl_status": etl_status,
            "etl_errors": reason
        }}
    )
    #E por fim retorna as informações principais transformadas para serem armazenadas no 
    #postgres (Vale lembrar que não são todas que são armazenadas lá, somente as de uso
    # principal, nesta etapa, informações como raw_text e sanitized_text são mantidas
    # apenas no mongodb e descartadas nesta etapa)

    #A função retorna sempre o dado resumido (sem o raw e o sanitized), com as modificações
    #feitas
    return {
        "id": str(doc.get("_id")),
        "scan_timestamp": doc.get("scan_timestamp"),
        "parsed": item_data
    }
