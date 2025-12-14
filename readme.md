Versão 0 - O progama funciona a partir de uma IA e do easyOCR para indentificar itens de leilão. Ele 
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


Versão 1 - O programa agora tenta consertar os erros de leitura do OCR, sanitizando o texto antes de
passar para o item_parser.py. Alem disso, o item_parser.py agora retorna tanto os dados do item
quanto o texto sanitizado, para facilitar a depuração e análise dos dados. Com tambem agora o salvamento
sendo feito tanto na pasta detections quando em banco de dados MongoDB.

Versão 1.01.09/11/2025 - Foi feita algumas adições nas constantes.py, com tambem sendo feita a lista SELLER_REPLACEMENTS. E por fim foi feito alterações no item_phaser.py para ele suportar a verificação do seller. 

Versão 1.02.14/12/2025 - Existia um erro de correção do item_parser nos casos em que as correções
eram feitas nas linhas específicas e não era alterado a linha sanitizada, ficando assim errada,
isto foi corrigido, assim como uma melhoria na lógica da função item_sanitizer e na organização
geral. Também foi altera algumas constants pois estavam sendo feitas correções inadequadas, adiconando em alguns casos letras extras.