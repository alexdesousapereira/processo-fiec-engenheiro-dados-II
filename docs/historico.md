# Histórico do projeto

Registro do que foi feito e decidido, do mais recente para o mais antigo.
Modelo de entrada: **O que foi feito**, **Decisões**, **Pendências**.

## 2026-11-08: Commits por etapa e publicação no GitHub (T001)

### O que foi feito

- `/speckit-converge` sem pendências no código; restam só T064 e T070, do candidato.
- Histórico do Git organizado em commits por etapa, cada um citando as tarefas que cobre, e enviado para
  `github.com/alexdesousapereira/processo-fiec-engenheiro-dados-II`, na branch `main`.
- Identidade do Git: `alexdesousapereira <alexdesousapereiraa@gmail.com>`, inclusive no primeiro commit, refeito com o mesmo conteúdo e data.

### Decisões

- Cada commit tem a data da última modificação dos seus arquivos, o momento em que eles chegaram ao conteúdo atual. A data de criação do Windows não serviu, porque é renovada quando um arquivo é reescrito.
- `powerbi/` usa a data em que o projeto foi gerado, porque a sincronização do OneDrive alterou a data de modificação.
- Cada commit tem a versão final dos arquivos: as etapas intermediárias não foram reconstruídas.

### Pendências

- T064 (abrir o painel no Power BI Desktop) e T070 (exportar `arquitetura.png`).
- Responder à Questão 1.

## 2026-11-08: Terceira convergência (T087)

### O que foi feito

- `/speckit-converge` apontou que só os pacotes diretos tinham versão fixa: 8 na ingestão e 2 no dbt, de 30 e 54 instalados.
- Criação de `requirements/ingestao.lock`, `requirements/dbt.lock` e `requirements/dbt.txt`, aplicados com `-c` nos Dockerfiles.
- Verificado: builds sem cache instalaram exatamente as versões travadas; 150 testes em Python, 46 do dbt e a DAG com 6 tarefas verdes.

### Decisões

- Os `.lock` foram gerados das imagens já validadas, para travar as versões testadas, sem trazer versões novas.

### Pendências

- Confirmar com um novo `/speckit-converge` que não restou nada.
- Continuam abertas T001 (commits), T064 (painel no Power BI Desktop) e T070 (exportar `arquitetura.png`).

## 2026-11-07: Proposta futura na Azure

### O que foi feito

- Esclarecimentos com o candidato (4 perguntas), registrados em `docs/arquitetura/proposta-futura/PROPOSTA-FUTURA.md`, e não na spec da feature 001, que declara a proposta futura fora do escopo.
- Proposta futura reescrita para Databricks, Azure Data Factory e ADLS Gen2, com o ADR 0014 e uma nota no ADR 0007.
- Diagrama: na metade da proposta futura, 9 textos foram trocados e saíram os logos do Airflow e do Docker. A arquitetura atual não mudou.

### Decisões

- A Gold fica em Delta no ADLS e é consultada pelo SQL Warehouse do Databricks.
- A extração continua em Python, em um job do Databricks acionado pelo Data Factory.
- A API FastAPI sai da proposta futura.
- O acesso é feito pelo Unity Catalog, com grupos do Entra ID e identidades gerenciadas, sem chaves.
- Os serviços da Azure aparecem no diagrama só como texto, sem logos da marca.

### Pendências

- Conferir no Excalidraw se os textos novos couberam nas caixas e exportar `arquitetura.png` (T070).
- Interpretei "orquestrador via Data Factory ao invés de ." como "no lugar do Airflow"; o candidato deve confirmar.

## 2026-11-07: Segunda convergência (T084 a T086)

### O que foi feito

- `/speckit-converge` encontrou 3 violações pequenas da constituição, e `/speckit-implement` as corrigiu.
- Logs e status da execução agora dizem quais meses foram tratados (`meses_gravados` e `meses_stage`).
- Funções de tratamento recebem DataFrames; a conversão do JSON foi para `carga.py`.
- Resultados: 150 testes em Python e 46 do dbt.
- Verificado: reprocessar os 297 meses com o código novo deixou a assinatura MD5 do fato e das dimensões idêntica. O script de criação foi testado em um banco novo.

### Decisões

- Refatorar em vez de emendar a regra de DataFrames da constituição.
- A coluna nova entrou no ambiente em uso com `ALTER TABLE`, para não apagar os dados. Ambientes novos a recebem pelo script de criação.

### Pendências

- Confirmar com um novo `/speckit-converge` que não restou nada.
- Continuam abertas T001 (commits), T064 (abrir o painel no Power BI Desktop) e T070 (exportar `arquitetura.png`).
- Responder à Questão 1.

## 2026-11-07: Correções da convergência (T076 a T083)

### O que foi feito

- Tarefa `validar_lote` na DAG, com 19 testes sobre a Stage antes de publicar.
- Cliente da DAG com `Session` e novas tentativas nas consultas, e modelos Pydantic em `/health` e no `409`.
- `post_hook` passou a comparar o arquivo, e não só o mês.
- Mudança de códigos na fonte interrompe a carga, e os territórios dos valores são comparados com as localidades.
- Localidades guardadas com os bytes originais de cada resposta. A API libera sozinha uma execução que ficou aberta.
- Resultados: 146 testes em Python, 46 do dbt, 914.166 linhas no fato, 2.004 na view e 612 no top 3.
- Verificados de verdade: lote inválido, teste reprovado depois de publicar, versão nova pendente no `post_hook` e um novo `git clone` limpo, em cerca de 5 minutos.

### Decisões

- O modo `completa` é quem aceita uma mudança de códigos na fonte, porque ela exige também atualizar o histórico.
- A API considera perdida a execução aberta que este processo não está rodando. Isso só vale porque há um único worker.
- POST da DAG não é repetido pela sessão: um pedido que falhou no meio pode ter sido aceito.

### Pendências

- Continuam abertas T001 (commits), T064 (abrir o painel no Power BI Desktop) e T070 (exportar `arquitetura.png`).
- Confirmar com um novo `/speckit-converge` que não restou nada.

## 2026-11-07: Convergência e constituição 1.2.0

### O que foi feito

- `/speckit-converge` comparou o código com a spec, o plano, as tarefas e a constituição, e acrescentou as tarefas T076 a T083 (Fase 9).
- Registro da decisão sobre testes reprovados na spec (US3, FR-015, SC-008), na pesquisa e na constituição.

### Decisões

- Opção A do candidato: validar o lote na Stage antes de publicar. Testes sobre o resultado publicado rodam depois e marcam a DAG como falha.
- Constituição 1.2.0, versão MINOR: a mudança ajusta uma regra da seção de padrões, sem remover nem redefinir princípios.

### Pendências

- Implementar T076 a T083. Antes disso, o código ainda publica os dados sem validar o lote.
- Continuam abertas T001 (commits), T064 (abrir o painel no Power BI Desktop) e T070 (exportar a imagem do diagrama).

## 2026-11-07: Implementação do pipeline com API, dbt em contêiner e painel

### O que foi feito

- Ingestão em contêiner próprio, com API FastAPI, registro de execuções, extração por tabela e janela de períodos.
- dbt em contêiner próprio, acionado por `DockerOperator`; modelo renomeado para `warehouse`, `dim_*` e `fat_*`; nova view do top 3 e testes de unidade do dbt.
- DAG refeita, com 5 tarefas. A imagem do Airflow ficou sem pandas nem dbt.
- Painel em PBIP com capa e análise, com o JSON validado contra os esquemas oficiais.
- ADRs 0011, 0012 e 0013, arquitetura, README e textos do diagrama atualizados.
- Resultados: 133 testes em Python, 17 do dbt, 914.166 linhas no fato, 2.004 na view e 612 no top 3, com o Ceará igual ao conferido à mão.
- Verificados de verdade: reprocessar com a rede cortada, falha forçada no fato, falha da extração na DAG, `409`, reinício da API e `git clone` limpo só com o `.env.example`.
- Medições: `EXPLAIN ANALYZE` do top 3 em 5 ms, sem necessidade de novos índices.

### Decisões

- Corrigido `validar_brutos`, que chamava a fonte mesmo em `reprocessar`. Agora ele usa os metadados guardados.
- Criado `banco.abrir`, que fecha a conexão, pois um serviço no ar acumularia conexões abertas.
- Socket do Docker só no `airflow-scheduler`, sem proxy, com o risco registrado no ADR 0012.
- No PBIR, tema e fundos ficam em `StaticResources/RegisteredResources`, e não em `powerbi/tema`.
- O recorte do painel fica nas consultas do modelo: só UFs, 2025 e atividades de transformação.

### Pendências

- T001 e commits: dependem de autorização do candidato. O projeto continua fora do Git, com um só commit, na branch `docs/constituicao-1.1.0`, e a `main` não existe.
- T064: abrir `powerbi/Observatorio.pbip` no Power BI Desktop e validar. DAX, TMDL e visuais ainda não foram abertos em nenhum Power BI.
- T070: o `.excalidraw` foi atualizado, mas a imagem `arquitetura.png` ainda mostra o desenho antigo e precisa ser exportada de novo.
- Responder à Questão 1 e definir o arquivo de respostas.
- Avaliar o aviso do Starlette sobre `httpx` ao atualizar as dependências.
- A validação em clone limpo usou imagens-base já baixadas. O tempo em uma máquina sem cache não foi medido.

## 2026-11-07: Especificação do pipeline com API e painel

### O que foi feito

- Criação de `specs/001-pipeline-pim-pf/spec.md` a partir do enunciado da prova e de `requisitos/decisoes.md`, com checklist de qualidade.

### Decisões

- Uma única spec, com as 5 features do candidato como histórias priorizadas.
- O tratamento segue antes da Stage (T1) e os arquivos brutos seguem preservados (Princípio IV).
- Os nomes `warehouse`, `dim_*` e `fat_*` substituem os do ADR 0010; o plano deve registrar isso em um novo ADR.

- Escopo padrão (FR-002): todo o histórico na primeira carga; depois, os últimos 3 meses publicados, com parâmetro de até 2 anos.
- Endpoints por tabela (FR-012): acionam a extração só daquela tabela; os dados são lidos por SQL.

### Plano

- Criação de `plan.md`, `research.md`, `data-model.md`, `quickstart.md` e `contracts/` em `specs/001-pipeline-pim-pf/`.
- Novas medições em `docs/fonte-sidra-8888.md`: 24 meses em uma requisição, e metadados e localidades iguais aos valores.
- Medido no Docker Desktop: o usuário do Airflow acessa o socket (`root:root 660`, `gid=0`), então não é preciso proxy.
- Uma execução de ingestão por vez, com índice único parcial; dbt em contêiner próprio, acionado por `DockerOperator`.

### Pendências

- Implementar `specs/001-pipeline-pim-pf/tasks.md` (T001 a T075), incluindo os ADRs 0011 (API), 0012 (dbt e socket) e 0013 (nomes do warehouse).
- Corrigir `validar_brutos`, que hoje acessa a fonte mesmo em `reprocessar`, ao contrário do que diz a arquitetura (T025).
- Confirmar em teste que o `post_hook` do fato roda na mesma transação da carga.
- O painel será gerado fora do Power BI Desktop, e o candidato precisa abri-lo para validar.

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
