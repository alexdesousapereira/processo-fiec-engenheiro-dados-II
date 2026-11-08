# ADR 0011: API FastAPI como ponto de entrada da ingestão

**Status:** aceita, 2026-11-07

## Contexto

A prova não exige uma API. O candidato decidiu que a ingestão fica em um contêiner próprio, com uma API que aciona a extração
e informa o status, e esta é a justificativa escrita que a constituição exige. Uma carga completa leva cerca de 3 minutos, e a
DAG e pessoas precisam acompanhá-la sem acessar o contêiner.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| API com a extração em segundo plano, no mesmo processo | Sem novos serviços; contrato único para DAG e pessoas | Um reinício interrompe a execução |
| Extração direto na DAG, sem API | Mais simples | pandas volta à imagem do Airflow, e não há como acionar sem o Airflow |
| API com fila e workers | Execuções sobrevivem a reinícios e escalam | Mais serviços para uma execução por vez |

## Decisão

- `POST /extracoes/{tabela}` aceita o pedido e devolve `202` com um identificador. A extração roda em `BackgroundTasks`, com um único worker do Uvicorn.
- O estado fica em `controle.execucao_ingestao`, e `GET /execucoes/{id}` o consulta.
- Um índice único parcial, sobre uma expressão constante, permite só uma execução em aberto. A violação vira `409`, com o identificador em andamento.
- A trava vale para o sistema todo, e não por tabela, porque a produção física recarrega as dimensões na Stage.
- Cada dimensão tem o seu endpoint e vem de metadados ou localidades. A produção física carrega também as dimensões, para o fato não violar as chaves estrangeiras.
- Os dados continuam sendo lidos por SQL: a API não os devolve.
- Sem autenticação, com a porta publicada só em `127.0.0.1`, por ser um ambiente local de avaliação.

## Consequências

- Medido: `202` em 0,27 s durante uma carga completa, e `409` em uma segunda chamada.
- Ao subir, a API marca como `interrompida` o que ficou em aberto, o que foi verificado reiniciando o contêiner durante uma carga. Os meses gravados até ali seguem pendentes, e a próxima execução os retoma.
- Se o banco cair no instante de registrar o início ou o fim de uma execução, ela fica em aberto. Como há um só worker, o próximo pedido percebe que este processo não a está rodando, marca-a como `interrompida` e segue, sem exigir um reinício.
- Em produção, o ajuste mínimo é acrescentar autenticação. Com mais fontes ou execuções simultâneas, faria sentido adotar uma fila.
