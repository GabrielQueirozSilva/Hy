from I_A_H.ETL.extract import Extrator
from I_A_H.ETL.transform import transformar_documento
from I_A_H.ETL.schemas import (
    create_database_if_not_exists,
    create_tables,
    validar_item
)
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

            is_valid, invalid_reason = validar_item(transformado)

            transformado["is_valid"] = is_valid
            transformado["invalid_reason"] = invalid_reason

            if is_valid:
                dados_validos.append(transformado)
            else:
                dados_invalidos.append(transformado)

        except Exception as e:
            print(f"Erro ao processar documento {doc.get('_id')}: {e}")

    print(f"Registros validos: {len(dados_validos)}")
    print(f"Registros invalidos: {len(dados_invalidos)}")

    if dados_validos:
        load_data(dados_validos, validade=True)

    if dados_invalidos:
        load_data(dados_invalidos, validade=False)

    print("ETL finalizado")


if __name__ == "__main__":
    run()
