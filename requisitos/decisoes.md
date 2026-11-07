# Arquitetura de Dados
- Os dados consumidos serão da api do sidra IBGE, a partir do seguinte link: `https://apisidra.ibge.gov.br/values` e `https://servicodados.ibge.gov.br/api/v3/agregados/8888`

- Teremos um arquivo `python` que vai usar a biblioteca `request` para extrair os dados da tabela 8888 da api. Esse arquivo python é todo paramentrizá-vel para permitir cargas dinâmicas (validas essa possibilidade de extrair dados de até 2 anos). É feito também um processo de etl utilizando a biblioteca `pandas`, que vai adicionar metadados aos dados recuperados e fazer a carga no database `postgres` no schema `stage`.

- Teremos uma `api em python`, usando `biblioteca fastapi` que vai interagir com esse código python, ativandp a requisição da api do sidra, requisitando status da carga.

-  O arquivo `python de ingestão de dados` e a `api`, estarão no mesmo `container docker`e apenas a porta da `api` esta exposta. A api é o ponto de entrada da ingestão.

- Teremos um container docker para o `postgres`a fim de armazenar os dados extráidos, com 2 schemas pré-criados que serão: stage e warehouse.

- Teremos um container docker com o dbt instalado e plugado no schema stage do postgres. O dbt irá fazer um processo de etl nos dados do schema stage e armazená-los em um modelo de dw no schema warehouse.

- Teremos um airflow provesionado em docker que vai schedular a ingestão de dados via api e o etl do dbt via bash-comand, enviado por docker operator.

- Todos os container serão gerenciados via docker compose

- A parte visual será feita via power bi, via arquivo pbip, plugado no schema warehouse do postgres. Usando as melhores práticas de storyteling. Use a paleta de cores do arquivo `requisitos\tema_powerbi_fiec_observatorio.json`.

## feature 01: extração de dados da sidra

- objetivo: extrair os dados da tabelas do endpoint `https://apisidra.ibge.gov.br/values` e `https://servicodados.ibge.gov.br/api/v3/agregados/8888` a fim de trazer 4 tabelas: variaveis, territorio, categoria e produção fisica e armazenar no schema stage do postgres.
- eval: dados das 4 tabelas disponíveis no postgres e disponivel para consumo.
- fluxo:
1. Acessar o endpoint e extrair as informações dos últimos 3 meses.
2. para cada tabela extraida usar a biblioteca pandas para adicionar metadados de path origem e data de carga.
3. Inserir os dados em suas respectivas tabelas, no schema stage do postgres.
4. Aplique testes unitarios no codigo python.
5. Crie mecanismo de qualidade de software, a fim de garantir que as extrações da api funcionem corretamente, colocando tentativas de execução, timeout e etc.

# feature 02: api de execução de extração dados

- objetivo: crie uma api usando a biblioteca fastapi para interagir com meu codigo de extração de dados do sidra. Nesta api, verifique se é possível fazer a extração dos dados via um campo de data da api. Crie também um endpoint para consumir cada uma das tabelas dessa api (variaveis, territorio, categoria e produção).
- eval: api que chama o exctator de dados so sidra, com um  endpoint para cada uma das tabelas.
- fluxo:
1. Crir uma api execute o exctator de dados do sidra para cada um dos enpoints das tabelas.
2. Aplique testes unitarios python garantir funcionamento da api.
3. Crie mecanismo de qualidade de software, a fim de garantir que as extrações da api funcionem corretamente, colocando tentativas de execução, timeout e etc.

## feature 03: contrução do etl dbt

- objetivo: exctair dados das tabelas da stage e usar o dbt para essa extração, armazenando essas tabelas no schema warehouse, a fim de criar 5 tabelas: dim_variaveis, dim_categorias, dim_territorio, dim_calendario e  fat_producao_fisica.
- eval: dados das 5 tabelas geradas no schema warehouse para consumo.
- fluxo:
1. Acessar camada stage e fazer extração dos dados das 4 tabelas.
2. Para cada tabela usar dbt para aplicar as transformações, e modelagem das tabelas, adicionando em cada uma das tabelas os metadados de data_carga e path de origem.
3. Inserir os dados em suas respectivas tabelas, no schema warehouse do postgres.
4. No final Crie uma view que responda a principal pergunta do usuário dentro documento de `requisitos\case.docx` questões c e d da 2 .
5. Aplique testes unitarios no dbt para garantir que a transfomração funcione com sucesso.
6. Crie mecanismo de qualidade de software, a fim de garantir transformações rodem com sucesso.

## feature 04: orquestração dos extratores
- objetivo: criar orquestrador que faça a execução dos extratores e do etl em db.
- eval: schendular e ver tudo sendo executado corretamente.

## feature 05: construção dashboard
- objetivo: construir um dashboard que atenda os principais requisitos do documento `requisitos\case.docx` para questões c e d da 2. Neste Dashboard crie apenas duas telas, uma tela de capa e outra tela que o usuário utilizara para análise com os principais indicadores. Nesta etapa você consumirá apenas dados do warehouse.

- eval: dashboard análitico para consumo do usuário.
- fluxo:
1. Acessar dados do warehouse de cada uma das tabelas, verificar o requisitos do cliente com base arquivo `requisitos\case.docx` , analisando indicadores a serem cridos com seus devidos visuais. 
2. Criar Background do bi seguindo melhores práticas de storyteling em svg usando paleta de cores do arquivo para consumir no bi.
3. Criar pbip do power bi consumindo dados do warehouse e criando indicadores e gráficos.


