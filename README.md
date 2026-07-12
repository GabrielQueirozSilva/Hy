# I_A_H — Hypixel Item Analyzer / Auction Seeker

Pipeline completo de dados para o mercado de leilões (Auction House) do Hypixel Skyblock: captura de tela com visão computacional, extração de texto via OCR, ETL em Python, armazenamento em MongoDB/PostgreSQL e um dashboard analítico em Power BI ("Auction Seeker").

> Prints e vídeos do dashboard final: [`docs/RESULTS.md`](docs/RESULTS.md)
> Histórico de versões e decisões técnicas: [`CHANGELOG.md`](CHANGELOG.md)

---

## Visão geral da arquitetura

```
Análise de tela
      │
      ▼
YOLO (detecção da caixa do item)
      │
      ▼
EasyOCR (extração de texto)
      │
      ▼
Parser + Sanitizer (estruturação dos dados)
      │
      ▼
MongoDB + JSON (dados brutos / bronze)
      │
      ▼
ETL em Python  (extract → transform → schemas → load)
      │
      ▼
PostgreSQL (dados tratados / silver)
      │
      ▼
Power BI — Auction Seeker  (métricas / gold)
```

O projeto segue uma lógica próxima da arquitetura medalhão: dados brutos e imutáveis ficam em arquivos .json, dados iniciais e tratáveis ficam no MongoDB, dados validados e tratados vão para o PostgreSQL, e as métricas de negócio (lucratividade, sellers, histórico de preços) são construídas em DAX no Power BI.

## Stack

- **Visão computacional:** YOLO (`yolo11s`, treinado no Kaggle), OpenCV
- **OCR:** EasyOCR
- **Linguagem:** Python 3.11
- **Bancos de dados:** MongoDB e .json (armazenamento bruto), PostgreSQL (dados tratados)
- **BI:** Power BI Desktop (modelagem de dados + DAX)
- **Outras libs:** psycopg2, pymongo, thefuzz (fuzzy matching), python-dotenv

## Estrutura do projeto

```
I_A_H/
├── analyzer/        # captura de tela e detecção via YOLO + EasyOCR
├── ETL/
│   ├── extract.py    # extração do MongoDB
│   ├── transform.py  # validação e etiquetagem (etl_status)
│   ├── schemas.py     # DDL do PostgreSQL + regras de validação
│   ├── load.py         # carga no PostgreSQL
│   ├── seller.py        # agrupamento e deduplicação de vendedores
│   └── run_etl.py         # orquestrador do pipeline
├── parser/          # sanitizer.py e item_parser.py — estruturação do texto bruto
├── storage/         # mongo.py, json_export.py
├── ui/               # overlay.py — feedback visual durante a captura
├── constants.py    # constantes utilizadas para correção
└── main.py            # loop principal de captura
```

## Pré-requisitos

- Python **3.11** (versões mais novas têm incompatibilidade conhecida com `psycopg2`, ver [CHANGELOG](CHANGELOG.md#301))
- PostgreSQL em execução localmente ou remoto
- MongoDB em execução localmente ou remoto

## Configuração

1. Clone o repositório e crie um ambiente virtual na raiz do projeto:

   ```bash
   python -m venv venv
   venv\Scripts\Activate   # Windows
   # source venv/bin/activate   # Linux/macOS
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

   ```env
   MONGO_URI=<sua_uri_de_conexao_mongodb>
   MONGO_DB=<nome_do_banco_mongodb>
   MONGO_COLLECTION_NAME=<nome_da_collection>

   POSTGRES_HOST=<host_do_postgres>
   POSTGRES_DB=<nome_do_banco_postgres>
   POSTGRES_USER=<usuario_postgres>
   POSTGRES_PASSWORD=<senha_postgres>
   ```

## Como executar

### Captura de itens (main)

Inicia a captura de tela, detecção de itens via YOLO e extração de texto via OCR:

```bash
python -m I_A_H.main
```

Durante a execução:
- `v` → salva o item detectado (MongoDB + JSON local)
- `x` → encerra a captura

### Pipeline ETL

Processa os dados brutos do MongoDB, valida, etiqueta (`etl_status`) e carrega os registros válidos no PostgreSQL:

```bash
python -m I_A_H.ETL.run_etl
```

O status de cada documento no MongoDB pode ser:
- `validated` — pronto e carregado no PostgreSQL
- `quarantine` — inválido, mas recuperável (pode ser reprocessado sem perder histórico)
- `rejected` — inválido e sem dados suficientes para correção

## Scripts auxiliares

Além do pipeline principal, o projeto conta com scripts pontuais de manutenção e correção retroativa de dados, localizados em `I_A_H/tools/`:

- **`read_json.py`** — reimporta arquivos JSON de detecções antigas para o MongoDB.
- **`pgchange.py`** — reaplica correções de sanitização de vendedores diretamente nos registros já existentes no PostgreSQL.
- **`reavaliando_parser.py`** — reprocessa documentos em quarentena com a versão atual do parser, para avaliar se as correções recentes resolveram os erros anteriores.

## Dashboard (Power BI)

O "Auction Seeker" é composto por 4 páginas:

| Página | Conteúdo |
|---|---|
| **Visão Geral** | panorama geral do volume de itens analisados e principais métricas |
| **Lucratividade** | margens, itens mais lucrativos, variação de preços |
| **Vendedores** | ranking de sellers, consistência, melhores ofertas por item |
| **Histórico** | evolução de preços, detecção de undercutting |

Prints e uma descrição de cada página estão em [`docs/RESULTS.md`](docs/RESULTS.md).

## Licença

Este projeto está licenciado sob os termos da [Licença MIT](LICENSE).