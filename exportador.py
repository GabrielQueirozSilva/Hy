# exportador.py
import os
import json
import pandas as pd

# --- CONFIGURAÇÕES ---
# Pasta raiz onde os JSONs estão salvos (com as subpastas de classe)
PASTA_RAIZ = "detections"
# Nome do arquivo de saída que será gerado
ARQUIVO_SAIDA_EXCEL = "relatorio.xlsx"

def exportar_dados_para_excel():
    """
    Varre as subpastas, coleta os dados de 'item_data' de cada JSON
    e os consolida em um único arquivo Excel.
    """
    todos_os_itens = []

    print(f"🔎 Varrendo a pasta '{PASTA_RAIZ}' em busca de arquivos .json...")

    # os.walk() é perfeito para navegar em todas as subpastas
    for dirpath, dirnames, filenames in os.walk(PASTA_RAIZ):
        for filename in filenames:
            # Verifica se o arquivo é um JSON
            if filename.endswith(".json"):
                caminho_completo = os.path.join(dirpath, filename)
                
                # Pega o nome da pasta atual, que é a nossa classe
                classe_detectada = os.path.basename(dirpath)
                
                try:
                    with open(caminho_completo, 'r', encoding='utf-8') as f:
                        dados_json = json.load(f)
                        
                        # Pega apenas o dicionário 'item_data', se ele existir
                        item_data = dados_json.get('item_data')
                        
                        if item_data:
                            # Adiciona a classe detectada aos dados do item
                            item_data['detected_class'] = classe_detectada
                            todos_os_itens.append(item_data)

                except json.JSONDecodeError:
                    print(f"⚠️ Aviso: O arquivo {caminho_completo} não é um JSON válido e será ignorado.")
                except Exception as e:
                    print(f"❗️ Erro ao processar o arquivo {caminho_completo}: {e}")

    if not todos_os_itens:
        print("Nenhum dado de item encontrado para exportar.")
        return

    print(f"\n✅ {len(todos_os_itens)} itens encontrados. Consolidando e exportando para Excel...")

    # --- A MÁGICA DO PANDAS ---
    # 1. Converte a lista de dicionários em uma tabela (DataFrame)
    df = pd.DataFrame(todos_os_itens)

    # 2. Salva a tabela em um arquivo Excel (.xlsx)
    # index=False evita que o pandas salve os índices das linhas como uma coluna extra
    df.to_excel(ARQUIVO_SAIDA_EXCEL, index=False, engine='openpyxl')

    print(f"\n🎉 Sucesso! Os dados foram salvos em '{ARQUIVO_SAIDA_EXCEL}'")


if __name__ == "__main__":
    exportar_dados_para_excel()