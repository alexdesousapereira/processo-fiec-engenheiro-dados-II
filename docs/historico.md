# Histórico do projeto

Registro do que foi feito e decidido, do mais recente para o mais antigo.
Modelo de entrada: **O que foi feito**, **Decisões**, **Pendências**.

## 2026-11-09: Rótulo curto do mês na `dim_calendario` e painel sem a `meses_linha`

### O que foi feito

- Clarificação da spec 002: o painel não cria tabelas próprias além de `Medidas`; o rótulo curto do mês vem do
  dbt. O converge gerou as tarefas T034 a T037, todas concluídas.
- dbt: `dim_calendario` ganhou `mes_curto` (jan, fev…), declarada no contrato como `not null`. Como o modelo é
  incremental com `on_schema_change: fail`, o banco existente precisou de uma migração única: `ALTER TABLE ... ADD
  COLUMN`, `dbt run`, preenchimento dos 288 meses fora da Stage atual (2002 a 2026) e `SET NOT NULL`. Um banco novo
  já nasce com a coluna. As imagens do dbt e do Airflow foram reconstruídas (o manifesto do Cosmos fica na imagem).
- Painel: saíram a tabela `meses_linha`, o `TREATAS` e a medida "Média mensal da linha". A linha usa
  `dim_calendario[mes_curto]` com `[Média das atividades]`, e o filtro de mês não age sobre ela (`visualInteractions`
  com `NoFilter` no `page.json`). O insight virou o cartão `linha_insight`, que recebe o filtro de mês.
- O gerador passou a gravar a posição dos filtros e a página inicial (Análise) ajustadas no Desktop, que uma
  regeração desfaria.
- Validado: `dbt run` com 7 modelos, `dbt test` com 42 de 42, PBIP com 44 JSON sem erro e 9 TMDL conferidos.

### Pendências

- Abrir `powerbi/Observatorio.pbip` no Desktop e conferir a linha com 12 meses, o cartão do insight no lugar do
  subtítulo e o texto "Janeiro em 101,58; pico em outubro (115,35)"; depois republicar no serviço.

## 2026-11-09: Requisitos e resolução do case no repositório

### O que foi feito

- `requisitos/` (enunciado `case.docx`, `decisoes.md`, tema do Power BI e regras `pbi-mockup/`) e `resolucao_case/`
  (documentos da Questão 1 e das Questões 2 e 3) passaram a ser versionados, a pedido do candidato.
- `.gitignore`: saiu `requisitos/`, e `Prova*.docx` passou a valer só na raiz (`/Prova*.docx`), para não esconder os
  documentos de `resolucao_case/`.
- `CLAUDE.md` lista as duas pastas; a spec 002 registra que `requisitos/` passou a ser versionada; o plano da
  feature 001 indica as 18 tarefas da DAG com o Cosmos.

### Decisões

- Revoga a decisão de 2026-11-06 de deixar o enunciado da prova fora do Git. As menções antigas a
  "`requisitos/` não é versionado" no plano e nas tarefas da feature 002 ficam como registro da época.

## 2026-11-09: Convergência da feature 002 (`/speckit-converge` e `/speckit-implement`)

### O que foi feito

- O converge comparou a feature 002 com o código e achou 3 divergências, todas de documentação: a spec, o
  contrato das telas e o data-model ainda citavam `vw_transformacao_2025`. Viraram as tarefas T031 a T033.
- Corrigidos: a clarificação da spec agora diz que o dbt mantém só `vw_top3_transformacao_2025`; o contrato das
  telas usa `dim_categorias[categoria_rotulo]` nas barras e `meses_linha[mes_curto]` com `[Média mensal da linha]`
  na linha, como o gerador do PBIP; o data-model dá como fonte a tabela fato com `dim_categorias`.
- Documento das questões 02 e 03: retirada a configuração `updateFields`, que fazia o Word perguntar sobre
  "campos que referenciam outros arquivos" ao abrir. O sumário já sai com as páginas certas.

- Feature 001: `data-model.md` passa a listar a tabela analítica e a view do top 3; a quickstart conta a tabela
  no lugar da view removida e espera 18 tarefas na DAG; `research.md` ganhou uma atualização na decisão do top 3.

## 2026-11-09: Uma view só e documento sem referência a questões

### O que foi feito

- dbt: `vw_transformacao_2025` removida (também do banco, com `DROP VIEW`). A única view é
  `vw_top3_transformacao_2025`, que responde às 3 atividades de maior índice por UF e mês a partir da tabela
  analítica. `sql/top3_por_uf_mes.sql` passou a ler dela.
- Os testes que liam a view removida passaram a ler `fato_producao_fisica_industrial_2025` (Ceará, 17 UFs e 12 meses,
  padrão `3.NN`, ao menos 3 atividades). Saíram só os 4 testes de não nulo da view, já garantidos pela chave primária.
- Validado: `dbt run` com 7 modelos, `dbt test` com 23 testes (21 de dados e 2 de unidade), top 3 com 612 linhas,
  conferidor do mockup com 28 de 28 números e DAG com 18 tarefas verdes.
- Documento das questões 02 e 03: sumário depois da capa; seção "Visão geral" com problema do cliente, solução
  entregue e escopo; sem referências a questões; seção da view com o SQL dela; orquestração com os grupos e o Cosmos.
  O sumário é recalculado pelo Word ao abrir.
- Desenho: caixa do warehouse com "tabela analítica e view do top 3". Na arquitetura atual, o quadro voltou a ser
  "Fonte", só com IBGE / SIDRA; as quatro fontes ficam apenas na proposta futura.
- Quarentena retirada da proposta futura, a pedido do candidato: desenho, `PROPOSTA-FUTURA.md` e documento Word.
  O `ARQUITETURA.md` mantém a explicação de por que a arquitetura atual não tem quarentena.

### Pendências

- A data de atualização do mockup ficou em 08/11/2026, e o warehouse foi recarregado em 09/11/2026 (UTC).

## 2026-11-08: Conferência das tarefas abertas (`/speckit-implement`)

### O que foi feito

- Checklists de requisitos das features 001 e 002: 16 de 16 itens cada.
- T023 a T030 (feature 002) e T070 (feature 001) conferidas no código e marcadas como concluídas: já tinham sido feitas
  ao ajustar o painel e o desenho da arquitetura.

- T018 (feature 002) e T064 (feature 001) concluídas: o candidato conferiu o painel no Power BI Desktop e aceitou as
  diferenças restantes, registradas em `mockup/observatorio-mockup-racional.md`. As features 001 (87 tarefas) e 002
  (30 tarefas) estão completas.

## 2026-11-08: Cosmos no Airflow e grupos de tarefas na DAG

### O que foi feito

- DAG em dois grupos: `ingestao` (verificar, solicitar e aguardar a extração) e `dbt` (`validar_lote` e o grupo
  `warehouse` do Cosmos). O grupo `warehouse` mostra só as tabelas, com uma tarefa `run` e uma `test` cada; os testes
  de chave estrangeira rodam dentro do `test` do fato, a pedido do candidato. `carregar_warehouse` e `testar_dados` saíram.
- Imagem do Airflow: `astronomer-cosmos==1.15.1` (mais `aenum` e `deprecation`, em `requirements/airflow.lock`) e uma
  etapa de build que gera o `manifest.json` com `dbt parse`. O dbt não entra na imagem final.
- O teste "soma das diferenças é zero" passou a ler a tabela analítica, para ela ganhar uma tarefa de teste que roda
  também o teste de unidade da média.
- Validado com o scheduler, em `modo=reprocessar` para 202501: 20 tarefas verdes em cerca de 1 min 40 s e 27 testes
  aprovados.
- ADR 0015, contrato da DAG, arquitetura, README e spec 001 (esclarecimento e FR-031) atualizados.

### Decisões

- Cosmos em modo Docker, escolhido pelo candidato: o dbt continua no contêiner `pim-pf-dbt`, e o ADR 0012 vale.
- Versão 1.15.1, e não a 1.16.0, publicada em 03/11/2026, há menos de duas semanas.
- O grupo `dbt` não repete tarefas: um modelo com falha é reexecutado sozinho pela interface.

### Pendências

- `airflow dags test` com o scheduler ligado disputa as mesmas tarefas e falha; validar sempre disparando pelo scheduler.

## 2026-11-08: Documento das questões 02 e 03 atualizado e desenhos em fundo branco

### O que foi feito

- `docs/arquitetura/arquitetura.excalidraw`: fundo branco nos dois painéis, caixa "tabela analítica 2025 e views" no
  warehouse e correção de rótulos sobrepostos ("Ingestão", "dbt", nomes `dim_`, "Databricks" e "SQL Warehouse").
  `arquitetura.png` foi exportado de novo a partir dele.
- `resolucao_case/Prova_Pratica_7778_Questao_02_03_Alex_Pereira.docx` alinhado à arquitetura atual:
  - API FastAPI como entrada da ingestão, hash por mês e schemas `stage`, `warehouse` e `controle`;
  - tabelas `dim_`, `fat_producao_fisica` e a tabela analítica `fato_producao_fisica_industrial_2025`, com as views;
  - as 6 tarefas reais da DAG e os testes do lote antes de publicar;
  - proposta futura na Azure (ADLS Gen2, Databricks, Data Factory e Unity Catalog).
- Figuras 1 e 2 trocadas pelos painéis do Excalidraw em fundo branco. Nova seção 3.9 "Painel no Power BI", com o
  link publicado na web e o print da tela de análise (Figura 3).
- Desenho: o quadro "Fonte" virou "Fontes", com cartões de IBGE / SIDRA, APIs REST, bancos relacionais e arquivos.
  Na arquitetura atual, só o IBGE está ativo, e as demais aparecem tracejadas como fontes futuras; na proposta
  futura, as quatro estão ativas.
- Documento todo em A4 retrato: as seções em paisagem das Figuras 1 e 2 saíram, e as figuras ocupam a largura
  útil da página.

### Pendências

- O `.docx` fica fora do Git (`.gitignore`). Abrir no Word para conferir antes de enviar.

## 2026-11-08: Painel publicado no README

### O que foi feito

- README: a seção "Como abrir o painel" mostra o print da tela de análise do painel real
  (`docs/painel-power-bi.png`), e não mais o desenho do mockup, que continua citado por link.
- A imagem leva à tela de análise do relatório no workspace do Power BI Service.

### Decisões

- O link aponta para o relatório no workspace, e não para "Publicar na Web". Por isso, pede login na conta
  Microsoft e acesso ao workspace.

## 2026-11-08: Tabela analítica `fato_producao_fisica_industrial_2025`

### O que foi feito

- dbt: nova tabela `warehouse.fato_producao_fisica_industrial_2025`, com grão UF × mês × atividade de
  2025, índice, média da UF no mês, diferença, `path_origem` e `data_carga`. Tem contrato, chave primária
  e chaves estrangeiras para as dimensões. Foram geradas 2.004 linhas.
- `vw_transformacao_2025` e `vw_top3_transformacao_2025` passaram a ler da tabela, e não calculam mais nada.
  As colunas não mudaram, então `sql/top3_por_uf_mes.sql`, os testes e o mockup continuam iguais.
- Testes unitários apontados para a tabela. `dbt test`: 27 de 27 passaram.
- Power BI: o modelo importa a tabela e as dimensões, sem nenhuma view. O top 3 (com desempate pelo código),
  a líder e a cor do ranking viraram medidas DAX. Todas as medidas ficam na tabela `Medidas`. O rótulo do eixo
  passou para `dim_categorias[categoria_rotulo]`.
- Spec 002 (esclarecimento e FR-019), contrato do painel, arquitetura e README atualizados.

### Decisões

- Tabela `table`, e não `incremental`: a média depende de todas as atividades da UF no mês, e o merge deixaria
  uma linha antiga se a fonte revisasse um valor para "-". A tabela é pequena e recriada a cada carga.
- Nome `fato_...` pedido pelo candidato, fora do prefixo `fat_` do projeto, com o motivo registrado no `schema.yml`.
- No painel, índice, média e diferença vêm da tabela, e não do DAX, para baterem com a consulta SQL.

### Pendências

- Abrir no Power BI Desktop e conferir Ceará, janeiro de 2025: média 101,58, líder 3.13 Têxteis (+43,45)
  e top 3 com 3.13, 3.24 e 3.11.

## 2026-11-08: Botões e legenda do painel iguais ao mockup

### O que foi feito

- Botões corrigidos: o `show` de texto, preenchimento, contorno e ícone saiu do seletor `default` e foi
  para uma entrada própria. Antes, o Desktop ignorava a formatação e desenhava as abas Capa e Análise e o
  botão "Abrir a análise →" como caixas vazias com contorno escuro.
- Abas: texto azul (`#0E4194`) e negrito na aba ativa, cinza nas demais, e sublinhado azul na aba ativa.
- Botão da capa: fundo azul com texto branco, como no mockup.
- Barras: a linha da média ficou sem rótulo, pois o "101,58" cobria a primeira barra. No lugar, há uma
  legenda acima das barras ("■ Top 3 ■ Demais - - - Média da UF (101,58)"), feita com uma caixa de texto
  e a nova medida `Legenda da média`, com espaço reservado abaixo do subtítulo.
- PBIP regerado e validado: 43 JSON sem erro e 10 TMDL conferidos.

### Pendências

- Conferir no Power BI Desktop se a legenda e o sublinhado ficaram no lugar. As posições foram
  estimadas, porque a altura do título do visual só aparece no Desktop.

## 2026-11-08: Painel ajustado ao mockup (feature 002, US2 e US3)

### O que foi feito

- Mockup aprovado pelo candidato (T012).
- Gerador e validador do PBIP agora versionados em `powerbi/ferramentas/`.
- PBIP regerado no desenho do mockup:
  - visuais e telas: um só gráfico de barras com o top 3 e a linha da média, cartões com subtítulo, carimbos de data e barra de marca com abas;
  - modelo: medidas novas e as colunas `atividade_rotulo` e `dim_territorio[data_carga]`.
- Contrato do painel (feature 001) atualizado; README com a tela de análise; arquitetura e `CLAUDE.md` atualizados.
- Verificado: 32 JSON válidos nos esquemas oficiais; o PBIP é idêntico ao ser gerado duas vezes; 150 testes em Python seguem aprovados; geometria e números do mockup seguem corretos.

### Decisões

- O PBIP do repositório tinha sido salvo pelo Power BI Desktop: há `.platform`, `diagramLayout.json`, `lineageTag` e versões de formato mais novas. Corrige a entrada anterior, que atribuía as datas de `powerbi/` ao OneDrive.
- O Desktop descartou os fundos em SVG ao salvar. Por isso, a barra de marca e o fundo agora são visuais nativos e cor de página, sem imagem.
- O gerador usa as versões de formato que o Desktop gravou e preserva `.platform` e `diagramLayout.json`.
- O validador usa o esquema `visualContainer` 2.13.0 quando o 2.14.0, gravado pelo Desktop, ainda não está publicado, e avisa.

### Pendências

- T018: abrir o painel no Desktop e comparar com o mockup. Isso confirma a linha da média nas barras, os subtítulos por medida, a cor de fundo e os marcadores, e conclui também a T064 da feature 001.
- T070 (imagem do diagrama) e a Questão 1.

## 2026-11-08: Mockup do painel (feature 002, US1)

### O que foi feito

- Criação de `mockup/` com as telas `tela-01-capa.svg` e `tela-02-analise.svg`, o índice HTML, o racional, a consulta dos números, o conferidor e o validador de geometria.
- Verificado: `check_bounds.py` sem erros, colisões nem avisos; o conferidor encontrou os 28 valores obrigatórios e nenhum número sem origem no warehouse; o teste negativo detectou um número alterado.
- Telas convertidas para PNG e revisadas a olho, inclusive em escala de cinza. Foram corrigidos três problemas que o validador não pegou: a aba encostada na marca, um texto no limite do cartão e a linha da média sobre os rótulos.

### Decisões

- Gerador `mockup/ferramentas/gerar_telas.py`, fora da lista de tarefas, para regerar as telas se o IBGE revisar os dados.
- O conferidor também verifica o caminho inverso: todo número decimal exibido precisa existir no warehouse.
- Texto pequeno em `#5C6470`, porque os cinzas do `pbi-mockup` não atingem o contraste de 4,5:1.
- A linha mensal rotula só janeiro e o pico, porque doze rótulos se sobreporiam; os demais meses ficam no eixo.

### Pendências

- T012: aprovação do mockup pelo candidato, antes de ajustar o painel (US2).

## 2026-11-08: Especificação do mockup do painel (feature 002)

### O que foi feito

- Criação de `specs/002-mockup-power-bi/spec.md` e do checklist de qualidade, com 16 de 16 itens aprovados.
- As respostas às duas perguntas vieram das regras de `requisitos/pbi-mockup`, um pacote de skill para mockups de Power BI.

### Decisões

- O mockup tem um SVG estático por tela, de 1280 × 720, um índice HTML e um racional, e é a referência que o painel passa a seguir.
- Usa os números reais do warehouse, e não dados fictícios como as regras sugerem, porque a constituição exige dados medidos.
- Onde as regras divergirem do contrato atual do painel, prevalece o mockup, e o PBIP é ajustado.

### Plano

- Criação de `plan.md`, `research.md`, `data-model.md`, `quickstart.md` e `contracts/telas-mockup.md` em `specs/002-mockup-power-bi/`.
- Esqueleto `topo-marca`, com abas Capa e Análise e cor de ação `#0E4194`, a do tema do Observatório.
- A regra antirredundância funde os dois gráficos de barras do painel em um só: as atividades ordenadas pelo índice, o top 3 destacado e a linha da média.
- Os números foram medidos no warehouse: Ceará, jan/2025, 11 atividades, média 101,58 e 5 acima da média.

### Pendências

- `/speckit-tasks` e a implementação da feature 002.

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
