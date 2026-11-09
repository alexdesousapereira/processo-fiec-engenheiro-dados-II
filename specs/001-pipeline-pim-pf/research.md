# Research: Pipeline da PIM-PF

Medições feitas em 2026-11-07. As da fonte estão registradas em `docs/fonte-sidra-8888.md`.

## 1. Quais meses extrair

**Decision**: sem período informado, os alvos são a união de três grupos: meses ausentes do controle, os 3 últimos publicados e os
marcados como parciais. A carga `completa` percorre todos, e um intervalo informado substitui esses grupos.

**Rationale**: a mesma regra cobre a primeira carga (todos ausentes), uma carga interrompida (os que faltam voltam) e um mês novo, sem
um caso especial para "primeira vez". Incluir os parciais evita que 202609 seja esquecido ao sair da janela.

**Alternatives considered**: um indicador de "primeira carga" falharia em cargas interrompidas. Sempre comparar todo o histórico pega
mais revisões, mas foi descartado na Q1. **Limitação aceita**: revisões anteriores à janela exigem uma carga `completa` manual.

## 2. Limite de 2 anos

**Decision**: o intervalo informado aceita até 24 meses, e a extração continua mês a mês.

**Rationale**: o `decisoes.md` pediu para validar essa possibilidade. Medido: uma requisição de 202301 a 202412 devolveu 200, com
73.872 linhas (24 × 3.078), em 5,5 s e 29,7 MB. A fonte aceita, mas pedir mês a mês mantém o hash por mês, que detecta o que mudou.

**Alternatives considered**: uma requisição só para o intervalo exigiria dividir a resposta antes de calcular o hash, sem ganho relevante.

## 3. Detectar novidade com a janela

**Decision**: a novidade é calculada só sobre os meses-alvo da seção 1: existe se algum tem data diferente da registrada ou se há
meses pendentes de carga. A função `periodos_com_novidade` é mantida, com a entrada filtrada.

**Rationale**: a fonte muda a data de todos os meses de uma vez (medido). Sem o filtro, os meses antigos, que a janela não atualiza,
pareceriam novidade todos os dias. Comparar mês a mês ainda cobre uma extração interrompida no meio da janela.

**Alternatives considered**: guardar uma única data da tabela não detecta interrupções na janela.

## 4. Extração por tabela

**Decision**: cada dimensão vem da sua fonte leve: `variaveis` e `categoria` de `/metadados`, e `territorio` de `/localidades/N1|N2|N3`.
`producao_fisica` vem de `/values` e carrega também as três dimensões.

**Rationale**: medido em 202501: nomes, códigos e unidades de metadados e localidades são idênticos aos de `/values`, com 6 variáveis, 27
categorias e 19 territórios. Extrair uma dimensão custa poucas requisições, em vez de um mês inteiro.

**Alternatives considered**: derivar as dimensões de `/values`, como hoje, obrigaria a baixar 3.078 linhas para atualizar uma dimensão.

## 5. Executar a extração sem prender a requisição

**Decision**: `BackgroundTasks` do FastAPI, com um único worker do Uvicorn e a situação gravada em `controle.execucao_ingestao`.

**Rationale**: atende a SC-007 sem novos serviços. O estado no banco sobrevive a reinícios: ao subir, a API marca como `interrompida` o que
ficou em aberto.

**Alternatives considered**: Celery e fila exigem mais serviços para uma execução por vez.

## 6. Uma execução por vez

**Decision**: um índice único parcial, válido para situações em aberto, garante uma execução por vez em todo o sistema. O `INSERT` que viola o
índice vira `409`, com o identificador da execução em andamento.

**Rationale**: o banco resolve a corrida entre dois pedidos sem lock em memória. Tabelas diferentes também são bloqueadas porque
`producao_fisica` recarrega as dimensões, e a simultaneidade poderia misturar a Stage. É mais restrito que FR-011 e mais simples de defender.

**Alternatives considered**: bloquear por tabela exige regras de conflito entre tabelas.

## 7. Período inexistente

**Decision**: o formato e o intervalo são validados no pedido (`422`). A existência dos meses é verificada já em segundo plano, e a execução
falha com causa `periodos_indisponiveis`.

**Rationale**: consultar a fonte na requisição poderia exceder os 5 s de SC-007, pois há novas tentativas com tempo limite de 120 s.

## 8. DAG acompanhando a API

**Decision**: tarefas Python chamam `cliente_api.py`, e um `PythonSensor` em modo `reschedule` consulta o status a cada 30 s, com limite de 1 h.
Se a tentativa do POST receber `409`, a tarefa adota o identificador devolvido.

**Rationale**: uma nova tentativa do POST não pode falhar só porque a primeira foi aceita. O cliente pode ser testado sem Airflow, e `requests` já está
na imagem (medido). O modo `reschedule` não ocupa um slot durante a espera.

**Alternatives considered**: `HttpOperator` e `HttpSensor` complicam o tratamento do `409` e os testes.

**Falha da extração**: o sensor falha sem nova tentativa, pois o erro já é definitivo. Os meses seguem pendentes, e a próxima execução os retoma.

## 9. dbt em contêiner próprio e socket do Docker

**Decision**: `DockerOperator` com `dbt run` e `dbt test` na imagem `pim-pf-dbt:1.0`, na rede `pim_pf_rede`, com `mount_tmp_dir=False` e a senha em
`private_environment`. O socket é montado só no `airflow-scheduler`, onde o LocalExecutor roda as tarefas. O serviço `dbt` do Compose executa
`dbt --version` e encerra, o que garante a imagem pronta.

**Rationale**: é o desenho definido pelo candidato. Medido no Docker Desktop: o socket é `root:root 660`, e o usuário do Airflow (`uid=50000`, `gid=0`)
consegue ler e gravar, sem proxy nem ajuste de grupo. O projeto dbt vai na imagem, o que evita caminhos do host, que variam no Windows.

**Risco, para o ADR 0012**: quem controla o socket controla o Docker do host. É aceitável na avaliação local, pois a DAG é versionada e nenhum
serviço externo chega ao scheduler. Em produção, a troca seria por um executor em Kubernetes ou um proxy com API restrita.

**Alternatives considered**: dbt na imagem do Airflow (simples, testado, sem socket, mas contraria a decisão do candidato); proxy do socket (um
serviço a mais, e o tag estável não foi confirmado).

## 10. Marcar os meses como carregados

**Decision**: um `post_hook` no `fat_producao_fisica` atualiza `controle.carga_periodo.carregado_em` para os meses presentes na Stage.

**Rationale**: o Python não roda mais depois do dbt. O hook fica junto da carga do fato e, pelo comportamento padrão do dbt, dentro da mesma
transação. **Verificado em 2026-11-07**: uma linha com território inexistente na Stage fez o fato falhar pela chave estrangeira; o fato
manteve as 914.166 linhas e a mesma `data_carga`, e o mês continuou pendente. Reprocessar o mês concluiu a carga e zerou os pendentes.

**Ajuste da convergência**: o hook compara `path_origem` com `carga_periodo.arquivo`, e não só o mês. Comparar só o mês marcava como carregada uma versão nova pendente enquanto a Stage ainda tinha a anterior. Verificado com esse cenário: o mês continua pendente.

**Alternatives considered**: uma tarefa extra na DAG abre uma janela entre a carga e a marcação.

## 11. Metadados nas tabelas

**Decision**: `path_origem` e `data_carga` nas 4 tabelas da Stage e nas 5 do warehouse. `data_carga` é definida na carga da Stage e propagada sem
mudar. Em `dim_calendario`, `path_origem` é `gerado:dbt`, e `data_carga` é o instante da execução.

**Rationale**: um único instante liga as duas camadas e mantém os modelos determinísticos. O caminho aponta para o arquivo bruto, cujo manifesto traz a
URL. A comparação de SC-003 considera os dados de negócio: um reprocessamento manual atualiza esses metadados, e isso é esperado.

## 12. Top 3

**Decision**: duas views: `vw_transformacao_2025` (questão c) e `vw_top3_transformacao_2025` (questão d), construída sobre a primeira. `sql/top3_por_uf_mes.sql`
continua como a consulta exigida.

**Rationale**: o `decisoes.md` pede uma view que responda às duas questões, mas os grãos são diferentes. A segunda view evita recriar o ranking no painel.

**Atualização (2026-11-09)**: a média e a diferença passaram para a tabela `fato_producao_fisica_industrial_2025`, e a
`vw_transformacao_2025` foi removida. Fica uma só view, `vw_top3_transformacao_2025`, lida da tabela, que responde ao top 3.

## 13. Portas

**Decision**: API, Airflow e PostgreSQL publicados só em `127.0.0.1`, em portas configuráveis.

**Rationale**: a API não tem autenticação, e o Power BI roda na mesma máquina. Isso limita o acesso à própria máquina, com uma mudança de uma linha.

## 14. Painel em PBIP

**Decision**: importação, e não DirectQuery, das views e das dimensões usadas, com servidor e porta em parâmetros e login `pim_leitura`. Arquivos em
`powerbi/`, com `.pbi/` e `cache.abf` ignorados.

**Rationale**: o recorte de 2025 tem 2.004 linhas, e a importação simplifica medidas e dá resposta imediata. O PBIP é texto, então fica versionável no Git.

**Risco**: os arquivos serão gerados fora do Power BI Desktop, e o formato não pode ser validado em contêiner. A aceitação depende de o candidato abrir o
projeto no Desktop e ajustar o que for preciso.

## 15. Migração do ambiente

**Decision**: recriar os volumes (`docker compose down -v`) e refazer a carga completa.

**Rationale**: os schemas são criados só com o volume vazio, e o caminho dos dados brutos muda. A carga leva cerca de 3 min, então migrar não compensa.

## 16. Teste de dados reprovado

**Decision**: uma nova tarefa `validar_lote` roda `dbt test --select source:stage` antes de `carregar_warehouse`, com testes definidos sobre as tabelas da Stage. Os testes das tabelas e views publicadas continuam em `testar_dados`, depois da carga.

**Rationale**: decisão do candidato (opção A). Barra a maioria dos problemas antes de tocar no warehouse, sem copiar dados. **Limitação aceita**: um problema que só apareça nas views ainda é publicado. Nesse caso, a DAG fica como falha, e a correção passa por reprocessar o período.

**Alternatives considered**: publicar em um schema candidato e promover cumpriria a garantia para todos os testes, mas exigiria copiar cerca de 914 mil linhas a cada carga, porque o modelo incremental não testa o histórico. Só mudar o texto da spec enfraqueceria a regra sem melhorar a proteção.
