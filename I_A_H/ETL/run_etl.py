from I_A_H.ETL.extract import Extrator
from I_A_H.ETL.transform import transformar_documento
from I_A_H.ETL.schemas import validar_item
from I_A_H.ETL.load import load_data


def run():
    print("I_A_H")

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

    print(f"Registros válidos: {len(dados_validos)}")
    print(f"Registros inválidos: {len(dados_invalidos)}")

    if dados_validos:
        load_data(dados_validos)

    print("ETL finalizado")


if __name__ == "__main__":
    run()
