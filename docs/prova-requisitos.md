# Requisitos da prova

Extraído de `Prova Prática - 7778 Engenheiro de Dados (2).docx`. Em caso de dúvida, vale o original.
Os IDs servem para rastrear cada requisito na arquitetura e no código.

## Entrega

| ID | Requisito |
|---|---|
| E1 | Arquivo `.zip` com respostas escritas e código organizado e documentado |
| E2 | O zip inclui o **histórico de commits do Git** (a pasta `.git`) |
| E3 | Enviar para `rh.selecao@sfiec.org.br` |
| E4 | Assunto: `PROVA PRÁTICA - SELEÇÃO CÓD. 7778 ENGENHEIRO DE DADOS II- <Seu Nome>` |
| E5 | IA é permitida, mas o candidato explica e defende na entrevista todas as decisões e trechos |

## Questão 1: experiência prévia

Para cada item, dizer se já usou e onde (projeto real, pessoal etc.). Nunca ter usado é aceito.

| ID | Item |
|---|---|
| Q1.1 | Manipulação e tratamento de dados com Python |
| Q1.2 | Manipulação e tratamento de dados com PySpark |
| Q1.3 | Modelagem de dados |
| Q1.4 | SQL |
| Q1.5 | Desenvolvimento de pipelines com Airflow |
| Q1.6 | Consumo/integração de APIs REST |
| Q1.7 | Ferramentas de Inteligência Artificial |
| Q1.8 | Ferramentas de visualização (Power BI, QlikSense e outros) |

## Questão 2: pipeline com Python e PySpark

Fonte: tabela 8888 do SIDRA, Produção Física Industrial, <https://sidra.ibge.gov.br/tabela/8888>

### Ingestão e armazenamento

| ID | Requisito |
|---|---|
| I1 | Extração automatizada em Python |
| I2 | Extrair **todos** os dados que a fonte disponibiliza |
| I3 | Considerar atualizações mensais |
| I4 | Considerar: formato dos arquivos |
| I5 | Considerar: organização dos dados |
| I6 | Considerar: particionamento |
| I7 | Considerar: identificação da origem |
| I8 | Considerar: data de processamento ou ingestão |
| I9 | Considerar: possibilidade de novas cargas |
| I10 | Considerar: facilidade de reprocessamento |

### Tratamento e preparação

| ID | Requisito |
|---|---|
| T1 | Processo em Python e/ou PySpark que gere versão confiável para outras equipes |
| T2 | Identificar e tratar os problemas dos dados de origem |
| T3 | Padronizar nomes de campos |
| T4 | Definir tipos de dados adequados |
| T5 | Tratar valores ausentes ou inválidos |
| T6 | Tratar duplicidades |

### Consumo analítico

Escopo: atividades da Indústria de Transformação, ano de 2025, indicador Número-índice (2022=100).

| ID | Requisito |
|---|---|
| A1 | Grão: Unidade da Federação × mês × atividade da Indústria de Transformação |
| A2 | Índice de produção da atividade |
| A3 | Média dos índices das atividades de transformação da UF e do mês |
| A4 | Diferença: índice − média (pode ser negativa) |
| A5 | Formato consultável via SQL (ex.: banco relacional) |

### Consulta SQL

| ID | Requisito |
|---|---|
| S1 | Usar a estrutura analítica criada na etapa anterior |
| S2 | Para cada UF e mês de 2025, as 3 atividades com maior índice de produção |

## Questão 3: contêineres e orquestração

| ID | Requisito |
|---|---|
| C1 | Ambiente com Docker Compose com os componentes para executar a solução |
| C2 | Instalar e disponibilizar as dependências do código |
| C3 | Disponibilizar uma instância do Apache Airflow |
| C4 | Manter as configurações para execução reproduzível |
| O1 | DAG no Airflow provisionado, orquestrando o pipeline da questão 2 |
