# Histórico do projeto

Registro do que foi feito e decidido, do mais recente para o mais antigo.
Modelo de entrada: **O que foi feito**, **Decisões**, **Pendências**.

## 2026-11-07: Constituição 1.1.0, com padrões de engenharia

### O que foi feito

- Inclusão da seção "Padrões de engenharia" na constituição, com regras para Python, pandas, requests, FastAPI,
  Docker, Airflow, SQL e PostgreSQL. Os princípios I a V não mudaram.

### Decisões

- Versão MINOR, pois a alteração só acrescenta orientação.
- "requesta" foi interpretado como a biblioteca `requests`, já usada na extração.
- As regras de FastAPI valem quando a API existir: a arquitetura em vigor ainda não tem esse serviço.

### Pendências

- Resolver os conflitos entre `requisitos/decisoes.md` e os requisitos e a arquitetura em vigor antes de
  `/speckit-specify`: extração dos últimos 3 meses (I2 pede todos os dados), arquivos brutos, Airflow com
  `DockerOperator` e nome do schema (`warehouse` ou `dw`).
- Anotar o retorno da função de `src/pim_pf/banco.py` que está sem esse tipo.

## 2026-11-07: DW em fato e dimensão, com dcalendario

### O que foi feito

- Renomeação das tabelas do `dw` para `dterritorio`, `dvariavel`, `dcategoria` e `fproducao_fisica`.
- Criação da `dcalendario`, ligada ao fato pelo código do mês, com chave estrangeira, e de um teste de dados.
- A view passou a filtrar 2025 pelo calendário. Diagrama, documentação e ADR 0010 atualizados.
- DW recriado pela DAG com `modo=reprocessar`, a partir dos arquivos já guardados: 914.166 linhas no fato, 300 meses no
  calendário, 2.004 na view e 612 no top 3, com o Ceará igual ao anterior. Testes: 26 unitários e 11 do dbt.
- Reprocessamento de 202501 sobre as tabelas já criadas, sem duplicar linhas.

### Decisões

- Prefixos `d` e `f`, seguindo o nome `dcalendario` pedido pelo candidato.
- Calendário mensal, o grão da fonte, com chave `periodo` (AAAAMM). Chaves das dimensões continuam sendo os códigos do IBGE.
- Stage sem mudança de nomes: ela é a área de carga, não o modelo de consumo.
- O título "estilo OLTP" deixa de valer para o DW. A divisão em Stage e DW do ADR 0008 continua.

### Pendências

- As mesmas da entrada anterior. A extração completa não foi repetida, pois o código dela não mudou.

## 2026-11-07: Implementação do pipeline com dbt

### O que foi feito

- Criação do ambiente em Docker Compose, da DAG, do código Python, do projeto dbt, dos testes e do README.
- Atualização do diagrama: título "Arquitetura Proposta", dbt entre a Stage e o OLTP e sem a quarentena.
- Execução do zero com os dados reais: 914.166 linhas no fato, 2.004 na view e 612 no top 3.
- Testes aprovados: 26 unitários e 10 do dbt. Repetição sem novidade e reprocessamento de um mês verificados.
- Registro de novas medições em `docs/fonte-sidra-8888.md` e criação do ADR 0009.

### Decisões

- Extração em Python, e não em dbt: o dbt não chama APIs, e o requisito I1 exige Python. O pedido dizia "extração via
  dbt"; a interpretação como erro de digitação precisa da confirmação do candidato.
- Tratamento em pandas (T1), e dbt da Stage ao DW, com `merge`, contratos e testes.
- Sem quarentena, seguindo o desenho do candidato: uma linha inválida interrompe a carga antes da Stage.
- `numeric(14,5)` no valor, pois a carga real revelou uma variação de 11.126.974,6%.
- Novo modo `reprocessar` na DAG, que refaz o DW sem chamar a API.
- Airflow 3.4.0 e dbt 1.11, versões suportadas. A implementação seguiu o pedido direto, sem passar pelo Spec Kit.

### Pendências

- Confirmar a extração em Python.
- Fazer os commits, pois o histórico faz parte da entrega (E2).
- Responder à Questão 1 e definir o arquivo de respostas.
- Definir o escopo do Power BI.
- Testar em uma máquina limpa, a partir de um clone do repositório.

## 2026-11-06: Stage, DW estilo OLTP e diagrama único

### O que foi feito

- Inclusão da Stage e do DW estilo OLTP na arquitetura atual (ADR 0008).
- Junção da arquitetura atual e da proposta futura em `docs/arquitetura/arquitetura.excalidraw`, com a imagem
  `arquitetura.png`.
- Remoção dos diagramas separados, inclusive a versão detalhada do lakehouse.
- Atualização de `ARQUITETURA.md`, `PROPOSTA-FUTURA.md` e dos ADRs 0005 e 0007.

### Decisões

- Schemas `stage`, `dw` e `controle`, com a quarentena em `controle`.
- O pandas recarrega a Stage com `COPY`, e uma transação faz o upsert no DW.
- A DAG continua com 6 tarefas: `carregar_relacional` passa a se chamar `carregar_dw`.
- A proposta futura continua igual, com Gold em star schema.

### Pendências

- Testar a Stage e o upsert no PostgreSQL durante a implementação.

## 2026-11-06: Desenho da arquitetura

### O que foi feito

- Medição da data de modificação por período e validação da regra analítica com os dados de 2025.
- Criação de `docs/arquitetura/ARQUITETURA.md` e dos ADRs.
- Criação dos diagramas em Excalidraw, no formato desenhado, com logos.
- Inclusão do Power BI como ferramenta de visualização conectada à view analítica (ADR 0005).
- Inclusão da camada Landing na arquitetura com camadas (ADR 0006).
- Medição do volume com pandas: 914 mil linhas, com pico de 343 MB.
- Arquitetura com camadas movida para `docs/arquitetura/proposta-futura/`, usando PySpark.
- Definição da arquitetura atual: arquivos brutos, pandas e modelo relacional no PostgreSQL (ADR 0007).
- Validação do modelo relacional e da view com os 12 meses de 2025, em SQLite.

### Decisões

Todas com status de proposta, nos ADRs:

- Python com pandas, PostgreSQL e Airflow em Docker Compose, sem Spark e sem MinIO no cenário atual.
- Detecção de mudanças por hash de cada mês, pois a data da fonte vale para a tabela inteira.
- Símbolo `-` como nulo, preservando o original.
- Arquivos brutos em JSON gzip e modelo relacional normalizado com view analítica.
- Spark fica para a proposta futura, pois o volume medido não o exige.

### Pendências

- Revisar a escolha entre PostgreSQL e SQL Server.
- Definir o escopo do Power BI: arquivo `.pbix` na entrega ou só a conexão documentada.
- Confirmar o significado de `-` nas notas da tabela no SIDRA.
- Iniciar `/speckit-specify` usando a arquitetura como contexto.

## 2026-11-06: Início do projeto

### O que foi feito

- Leitura da prova e extração dos requisitos com IDs para `docs/prova-requisitos.md`.
- Instalação do uv 0.13.7 e do Spec Kit (`specify-cli` 1.3.2.dev0).
- Inicialização do Spec Kit com a integração Claude e criação do repositório Git na branch `main`.
- Criação da constituição do projeto, versão 1.0.0.
- Medição da tabela 8888 nas APIs do IBGE, registrada em `docs/fonte-sidra-8888.md`.
- Criação da skill `gerar-arquitetura-dados`.

### Decisões

- O arquivo original da prova fica fora do Git e do zip.
- Spec Kit iniciado com `--ignore-agent-tools`, pois o Claude Code roda pela extensão do VS Code e o
  comando `claude` não está no PATH.
- Fase de arquitetura separada da implementação: a skill produz o desenho, e o Spec Kit conduz o
  código.

### Pendências

- Responder à Questão 1 com a experiência real do candidato.
- Fazer o commit inicial.
- Avaliar mover o projeto para fora do OneDrive, pois a sincronização pode interferir na pasta
  `.git` e em volumes do Docker.
