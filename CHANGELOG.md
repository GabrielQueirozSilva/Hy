# Changelog

Todas as mudanças relevantes do projeto são documentadas neste arquivo.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).


---

## [5.0] — 2026-07-11

### Added
- Documentação final para a publicação, com os seguintes arquivos/pastas:
  - `LICENSE`: licença MIT
  - `README.md`: README novo, reescrito para a publicação
  - `docs/RESULTS.md`: resultados visuais do dashboard e métricas do modelo
  - `CHANGELOG.md`: log de versões, antigo README reorganizado
  - `docs/images/`: local de armazenamento das imagens do projeto
  - `I_A_H/tools/`: local de armazenamento dos scripts auxiliares criados durante o desenvolvimento do projeto

### Changed
- `constants.py`: adição de novas correções.
- `seller.py`: correção do erro que gerava vendedores órfãos; documentação do arquivo.
- `main.py`: adição de indicação de confiança na detecção.
- `.env.example`: correção no nome do arquivo (antes `.env.exemple`).
- `requirements.txt`: correção no nome do arquivo (antes `requeriments.txt`).
- `extract.py`: pequena atualização na documentação.
- `load.py`: alteração referente à correção de vendedores órfãos.
- `run_etl.py`: alteração referente à correção de vendedores órfãos.
- `.gitignore`: atualização para excluir pastas de dados locais e arquivos auxiliares que não deveriam ser versionados.

---

## [Não lançado] — Dúvida

Início de uma reestruturação da modelagem de vendedores (seller). Duas abordagens estão sendo avaliadas:

1. Reestruturar o ETL para processar dados em lote (batch) em vez de item a item, permitindo lidar melhor com a tabela de vendedores.
2. Criar um script separado dedicado a vendedores, mantendo o fluxo atual do ETL intacto.

Ainda sem decisão final — o projeto está em crescimento e os requisitos futuros ainda não estão totalmente claros.

---

## [4.9.1] — 2026-06-11

### Added
- Tabela dedicada para armazenamento de vendedores (em desenvolvimento).
- `pgchange.py`: script para reaplicar sanitização de seller diretamente nos dados já existentes no PostgreSQL.
- `seller.py`: agrupamento e deduplicação de vendedores.
- Documentação dos módulos de storage e do `main.py`.

### Changed
- `constants.py`: revisão das regras de sanitização de seller.
- Dados de seller no PostgreSQL corrigidos e realinhados com a nova versão do sanitizer (viável apenas por conta do volume ainda pequeno de dados, ~900 linhas, com backup total no MongoDB).

---

## [4.2.5] — 2026-06-06

### Changed
- Finalização da correção de documentação nos módulos do ETL.

---

## [4.2] — 2026-06-06

### Changed
- Padronização da documentação do parser e sanitizer, com apoio do `docformatter`.

### Removed
- Comentários desnecessários no código.

---

## [4.1.5] — 2026-06-04

### Added
- Documentação do parser e sanitizer.

### Changed
- Melhorias moderadas na lógica do parser e sanitizer.

---

## [4.1] — 2026-05-27

### Added
- Documentação geral do módulo ETL.

### Changed
- Padronização do campo `etl_errors`.
- Especificação de registros inseridos vs. já existentes no log de carga.
- Pequenos ajustes em `constants.py`.
- Otimizações pontuais no pipeline ETL.

### Fixed
- `reavaliando_parser.py` (antigo `testando_parser.py`): passou a verificar apenas os documentos em quarentena no modo completo.

---

## [4.0] — 2026-04-12

### Changed
- Troca do modelo de IA usado para identificar as caixas de informação dos itens.
- ETL reestruturado: não cria mais tabelas separadas para dados válidos/inválidos no PostgreSQL — apenas os dados válidos são carregados, e o campo `etl_status` no MongoDB passa a controlar o ciclo de vida de cada documento (pendente / aprovado / precisa de melhoria / corrompido).
- Dados no PostgreSQL e nos arquivos JSON passam a ser tratados como imutáveis (uso analítico e de observação, respectivamente); o MongoDB passa a ser o armazenamento temporário sujeito a melhorias/exclusão.

### Added
- Aviso sonoro no `main.py` ao detectar e ao salvar um item.

---

## [3.06] — 2026-02-12

### Added
- `reavaliando_parser.py`: varredura completa para correção geral ou individual, com opção de salvar as modificações.
- Novas entradas em `constants.py`.
- Regras adicionais no sanitizer.

### Fixed
- Correção de casos identificados via testes manuais no parser.

### Changed
- Remoção de comentários obsoletos.

### Added (infra)
- `.env` para proteger credenciais dos bancos de dados.
- Script para leitura/reimportação de arquivos JSON antigos.
- `requirements.txt`.

---

## [3.05] — 2026-02-12

### Added
- Validação por discrepância no parser: verifica se as linhas estão corretamente localizadas antes de aplicar as regras principais; em caso de discrepância, o parser vai direto para a lógica de backup.
- Nova lógica de busca de seller na etapa de backup do parser.
- Novas constantes de reconhecimento.
- Função no sanitizer para remover linhas muito curtas geradas por erros do OCR.
- Remoção de tudo que vem após a linha "click to inspect" para limpeza adicional do texto.

---

## [3.04] — 2026-01-11

### Changed
- Substituição do campo booleano de invalidez por `invalid_reason`, permitindo uma análise mais granular dos motivos de rejeição.

---

## [3.03] — 2026-01-05

### Changed
- Padronização do campo `item_tier` → `tier`.
- Definição dos campos obrigatórios na camada silver (nome, tier, classe e preço).
- Regra de invalidação centralizada em `validar_item`.
- `transform.py` deixou de decidir validade — essa responsabilidade passou a ser exclusiva de `schemas.py`, respeitando corretamente o fluxo bronze → silver → gold.

---

## [3.02] — 2026-01-01

### Fixed
- `scan_timestamp` sempre nulo no PostgreSQL.

### Removed
- Persistência do campo `confidence` no PostgreSQL.

### Added
- Classe `Equipment` para aumentar a taxa de itens válidos.

### Changed
- Pequena atualização em `constants.py`.

---

## [3.01] — 2025-12-26

### Added
- Persistência dos registros inválidos no PostgreSQL, permitindo análise posterior de falhas de OCR e oportunidades de melhoria na sanitização/parsing.

### Changed
- Lógica de criação de tabelas (DDL) movida de `load.py` para `schemas.py`, separando corretamente:
  - `schemas`: DDL (definição)
  - `load`: DML (manipulação)
  - `run`: orquestração

### Fixed
- `UnicodeDecodeError` causado por incompatibilidade entre `psycopg2` e Python 3.13. Resolvido migrando o ambiente para **Python 3.11** via `venv`.

---

## [3.0] — 2025-12-25

### Added
- Pipeline ETL em Python (sem ferramentas dedicadas de ETL), com arquitetura próxima ao modelo medalhão (bronze/silver via MongoDB → PostgreSQL; gold é feito no Power BI).
- Estrutura do ETL dividida em 6 componentes: `extract`, `transform`, `schemas`, `load`, `run` e `__init__`.
- Separação entre registros válidos e inválidos (apenas válidos carregados no PostgreSQL nesta versão).

### Known issues
- Colunas `scan_timestamp` e `confidence` vindo nulas no PostgreSQL mesmo com dados presentes na origem.

### Resultado do primeiro teste
```
58 documentos extraídos do MongoDB
Registros válidos: 13
Registros inválidos: 45
13 registros carregados no PostgreSQL
```

---

## [2.0] — 2025-12-21

### Changed
- Abandonada a tentativa de conectar o Power BI diretamente ao MongoDB (integração problemática entre as ferramentas).
- Novo fluxo definido: **MongoDB (dados crus) → ETL (Python) → PostgreSQL → Power BI**.
- Reestruturação geral do projeto na pasta raiz `I_A_H`, separando responsabilidades que antes estavam misturadas (sanitização, parsing, análise e persistência).

---

## [1.02] — 2025-12-14

### Fixed
- Erro em que correções feitas em linhas específicas do parser não eram refletidas no texto sanitizado final.

### Changed
- Melhoria na lógica de `item_sanitizer` e organização geral do módulo.
- Ajustes em `constants.py` para evitar correções inadequadas que adicionavam letras extras.

---

## [1.01] — 2025-11-09

### Added
- Lista `SELLER_REPLACEMENTS` em `constants.py`.

### Changed
- `item_parser.py` passou a suportar a verificação do campo seller.

---

## [1.0]

### Added
- Sanitização de texto antes do parsing, para corrigir erros comuns de leitura do OCR.
- `item_parser.py` passou a retornar tanto os dados estruturados quanto o texto sanitizado (facilita depuração).
- Persistência dos dados também em MongoDB (além da pasta local de detections).

---

## [0.0] — Versão inicial

### Added
- Primeira versão funcional: uso de um modelo de IA para localizar as caixas de informação dos itens em tela e EasyOCR para ler o texto.
- Estrutura inicial em 4 arquivos principais: `analyzer.py`, `constants.py`, `item_parser.py`, `main.py`.
- Script de automação de leitura de tela/cliques e script de exportação dos dados de `.json` para `.xlsx`.
