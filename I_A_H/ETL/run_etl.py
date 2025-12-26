from I_A_H.ETL.extract import Extrator
from I_A_H.ETL.transform import transformar_documento
from I_A_H.ETL.schemas import *
from I_A_H.ETL.load import load_data


def run():


    create_database_if_not_exists()
    create_tables()
    
    extrator = Extrator()
    documentos_raw = extrator.extrair_dados()

    print(f"{len(documentos_raw)} documentos extraidos do MongoDB")

    dados_validos = []
    dados_invalidos = []

    for doc in documentos_raw:
        try:
            transformado = transformar_documento(doc)

            if validar_item(transformado):
                transformado["is_valid"] = True
                dados_validos.append(transformado)
            else:
                transformado["is_valid"] = False
                dados_invalidos.append(transformado)

        except Exception as e:
            print(f"Erro ao processar documento {doc.get('_id')}: {e}")

    print(f"Registros validos: {len(dados_validos)}")
    print(f"Registros invalidos: {len(dados_invalidos)}")

    if dados_validos:
        load_data(dados_validos,True)

    if dados_invalidos:
        load_data(dados_invalidos,False)

    print("ETL finalizado")


if __name__ == "__main__":
    run()
