PARA RODAR O CÓDIGO PRINCIPAL, VÁ PARA A PASTA PRINCIPAL DO PROJETO E USE python -m I_A_H.main

ETL - PARA RODAR A PARTE DO ETL É NECESSARIO FAZER O SEGUINTE COMANDO NO TERMINAL: python -m I_A_H.ETL.run_etl (lembrando de estar na pasta raiz do projeto).

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
