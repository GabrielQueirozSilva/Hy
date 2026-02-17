## **Como executar o projeto**

### **MAIN**

Para rodar o código principal do projeto, navegue até a pasta raiz do repositório e execute:

```bash
python -m I_A_H.main
```


### **ELT**

O pipeline ETL é responsável por processar os dados brutos armazenados no MongoDB e carregá-los no PostgreSQL para fins analíticos.

Pré-requisitos

Python 3.11 (versão estável e compatível com psycopg2)

PostgreSQL em execução

MongoDB em execução

Dependências instaladas no ambiente virtual

Criação do ambiente virtual (recomendado)

Na pasta raiz do projeto:

```bash
python -m venv venv
```

Ative o ambiente virtual:

```bash
venv\Scripts\Activate
```

Roda o ETL

```bash
python -m I_A_H.ETL.run_etl
```


---
## **Versão 0**

O progama funciona a partir de uma IA e do easyOCR para indentificar itens de leilão. Ele 
usa a IA para indentificar as caixas onde tem informações dos itens e o easyOCR para ler essas
informações. Atualmente ele é dividido em 4 arquivos principais os quais:

O analyzer.py: Serve para indentificar a caixa de informações dos itens, depois ele joga no item_parser.py
 para a coleta desses dados e armazena tudo em uma pasta detections, com as insformações em .json;

O constants.py: Serve para guardar constantes usadas no progama, tem as váriaveis para indentificar
as classes dos itens;

O item_parser.py: Serve para coletar as informações dos itens a partir do texto lido;

E por fim o main.py: É o arquivo principal que junta todas as partes.

Alem desses arquivos principais, o progama também usa um arquivo .gitignore para ignorar
certos arquivos e pastas que não são necessários para o funcionamento do progama, assim como
o ação.py para ações de automação de leitura de tela e cliques e o exportando.py
que serve para exportar os dados.json para xlsx.

---


## **Versão 1** 

O programa agora tenta consertar os erros de leitura do OCR, sanitizando o texto antes de
passar para o item_parser.py. Alem disso, o item_parser.py agora retorna tanto os dados do item
quanto o texto sanitizado, para facilitar a depuração e análise dos dados. Com tambem agora o salvamento sendo feito tanto na pasta detections quando em banco de dados MongoDB.

---



## **Versão 1.01 – 09/11/2025**

Foi feita algumas adições nas constantes.py, com tambem sendo feita a lista SELLER_REPLACEMENTS. E por fim foi feito alterações no item_phaser.py para ele suportar a verificação do seller. 

---



## **Versão 1.02 – 14/12/2025**

Existia um erro de correção do item_parser nos casos em que as correções eram feitas nas linhas específicas e não era alterado a linha sanitizada, ficando assim errada, isto foi corrigido, assim como uma melhoria na lógica da função item_sanitizer e na organização geral. Também foi altera algumas constants pois estavam sendo feitas correções inadequadas, adiconando em alguns casos letras extras.

---



## **Versão 2.0 – 21/12/2025**

Eu estava cometendo alguns erros, primeiro estava tentando ligar diretamente o PowerBI com os dados do mongodb para fazer a analise estatística dos dados, estava dando muito errado, e depois aprendi que essas ferramentas não se conversão bem entre sí. Agora pretendo fazer o uso do MongoDB (que fica a data crua) -> ETL (python) -> PostgreSQL -> PowerBI. Atualmente estou na parte do MongoDB. Aproveitando tamanha mudança, mudei a estrutura dos dados. Fiz uma pasta principal, a raiz do projeto, de nome I_A_H, nesa separei melhor as funções, ja que antes estava começando a misturar tudo com o parser.py fazendo a sanitização e o parser, o analyzer fazendo a analise das informações e o salvamento no MongoDB. Nessa nova pasta tudo vai ficar devidamente separado e mais organizado. Ajeitei também alguns bugs que ocorreram devido a divisão e fiz uma minuscula melhora no item_parse


FLUXO ATUAL:

OCR + IA
  ↓
MongoDB (raw) + json
  ↓
ETL (Python)
  ↓
PostgreSQL
  ↓
Power BI

---



## **Versão 3.0 – 25/12/2025**

Iniciei a implementação de um pipeline ETL em Python e uso do PostgreSQL, sem o uso de ferramentas ETL dedicadas, devido ao meu nível atual de conhecimento e ao controle fino que preciso sobre o processo. A arquitetura segue os princípios da arquitetura medalhão (so fiz a parte referente ao silver e bronze, o gold é so no PowerBI), com dados brutos mantidos no MongoDB e dados tratados sendo carregados no PostgreSQL para consumo analítico.

O ETL foi estruturado em seis componentes principais:

extract: responsável por extrair os dados brutos do MongoDB

transform: responsável por normalizar e preparar os dados para o PostgreSQL

schemas: define as regras de validade dos dados, separando registros válidos e inválidos

load: responsável pela carga no PostgreSQL

run: orquestra todo o fluxo ETL

__init__: garante o correto funcionamento do pacote (me recomendaram fazer isso para evitar bugs ou erros)

Atualmente, o ETL já executa com sucesso a separação entre dados válidos e inválidos, apesar de carregar apenas os validos no PostgreSQL, os proximos passos que busco fazer são justamente referentes a essa etapa. Esse foi o primeiro log de resultado que fiz nos dados iniciais que peguei bem no começo de tudo:

```bash
58 documentos extraidos do MongoDB
Registros válidos: 13
Registros inválidos: 45
13 registros carregados no PostgreSQL
ETL finalizado
```

Teve 2 tabelas que estam vindo nulls, apesar de terem dados, devo corrigir isso futuramente, tais tabelas foram a scan_timestamp e a confidence.

---


## **Versão 3.01 – 26/12/2025**

Nesta versão, foi adicionada também a persistência dos registros inválidos no PostgreSQL, permitindo análises posteriores sobre falhas de OCR, inconsistências de dados e oportunidades de melhoria no processo de sanitização e parsing.

Durante essa refatoração, a lógica de criação das tabelas foi movida do módulo load para o módulo schemas, respeitando a separação correta de responsabilidades:

schemas: DDL (Data Definition Language)

load: DML (Data Manipulation Language)

run: orquestração do fluxo

Essa mudança revelou um problema crítico de compatibilidade entre o psycopg2 e a versão do Python utilizada inicialmente (3.13), resultando no seguinte erro:

```bash
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe3 in position 96: invalid continuation byte
```

A solução adotada foi a criação de um ambiente virtual utilizando o Python 3.11, versão estável e plenamente compatível com o driver PostgreSQL. Após a migração para a venv, foram necessários apenas pequenos ajustes de nomenclatura no código, e o pipeline voltou a executar corretamente.

Essa experiência reforçou a importância de:

utilizar versões estáveis do Python em projetos que dependem de drivers nativos,

isolar o ambiente de execução com venv,

separar claramente responsabilidades dentro da arquitetura do ETL

Apesar de ser a melhor resposta, ainda me incomoda ter que criar uma venv.

---


##  **Versão 3.02 – 01/01/2026**
Foram feitas modificações/correções menores:

1: Correção de timestamp sempre vir null no PG;

2: A remoção do salvamento da confidence no PG;

3: Adição da classe equipaments para tornar mais items validos;

4: Pequena atualização no constants.py;

##  **Versão 3.03 – 05/01/2026**
Foram feitas modificações/correções menores:


1: Padronizei os campos item_tier  →  tier;

2: Defini os campos obrigatórios no silver (nome, tier, classe e preço);

3: Deixei uma invalidação clara na classe validar item;

4: Modifiquei o transform para apenas o schema definir validade e assim seguir corretamente o esquema bronze -> silver -> gold;

##  **Versão 3.04 – 11/01/2026**
Foram feitas modificações/correções menores:

1: Mudei de apenas invalid para invalid_reason, para ter uma analise melhor;

##  **Versão 3.05 – 12/02/2026**
Foram feitas melhorias no parser:

1: Como percebi que o sistema de detecção por linha não funcionava as vezes, fiz uma validação
por discrêpancia, que verificava se as linhas estavam corretamente localizadas, caso não, o código
evita fazer todas as verificações referentes a isso e vai direto para as verificações por backup;

2: Adicionei uma opção de salvar as modificações no testando_parser;

3: Fiz uma nova parte no backup do item_parser dedicado a encontra o seller;

4: adicionei novas possibilidades as constantes;

5: Ao perceber que as vezes vinham linhas a mais por causa de pequenos erros do OCR que fazia o código criar nova linhas minusculas, adicionei uma função no sanitizer para remover linhas muito pequenas, o que resolve alguns casos de textos anteriormentes incorretos,
