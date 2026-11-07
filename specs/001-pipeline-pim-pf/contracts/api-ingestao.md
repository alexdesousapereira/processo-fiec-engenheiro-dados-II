# Contrato: API de ingestão

Base: `http://localhost:8000` na máquina e `http://ingestao:8000` na rede do Compose. Sem autenticação, somente em ambiente local. O FastAPI publica a
documentação em `/docs`.

## Acionar a extração

`POST /extracoes/{tabela}`

| `{tabela}` | O que carrega na Stage |
|---|---|
| `variaveis` | `stage.variaveis` |
| `categoria` | `stage.categoria` |
| `territorio` | `stage.territorio` |
| `producao-fisica` | `stage.producao_fisica` e as três dimensões (FR-012) |

**Corpo em `producao-fisica`** (todos os campos são opcionais):

```json
{ "modo": "auto", "inicio": "2025-01", "fim": "2025-03" }
```

| Campo | Regra |
|---|---|
| `modo` | `auto` (padrão), `completa` ou `reprocessar` |
| `inicio`, `fim` | Formato `AAAA-MM`; ambos ou nenhum; `inicio` ≤ `fim`; no máximo 24 meses; não aceitos com `completa` |

| Modo | Sem intervalo | Com intervalo |
|---|---|---|
| `auto` | Meses ausentes, 3 últimos publicados e parciais; grava só o que mudou | Meses do intervalo; grava só o que mudou |
| `completa` | Todos os meses; regrava sem comparar o hash e aceita códigos novos ou removidos na fonte | Recusado |
| `reprocessar` | Todos os meses guardados, sem chamar a fonte | Meses do intervalo, sem chamar a fonte |

**Corpo nas dimensões**: `{ "modo": "auto" }` ou `{ "modo": "reprocessar" }`. Campos de período são recusados.

**Respostas**:

| Código | Quando | Corpo |
|---|---|---|
| `202` | Aceita | `{ "execucao_id": "uuid", "situacao": "pendente", "status_url": "/execucoes/uuid" }` |
| `409` | Já há execução em aberto | `{ "detail": "...", "execucao_id": "uuid" }` |
| `422` | Tabela, modo ou período inválido | Erro de validação, indicando o campo |

## Consultar uma execução

`GET /execucoes/{execucao_id}`

```json
{
  "execucao_id": "uuid",
  "tabela": "producao_fisica",
  "modo": "auto",
  "inicio": null,
  "fim": null,
  "situacao": "sucesso",
  "periodos_gravados": 1,
  "periodos_sem_mudanca": 2,
  "periodos_parciais": [202609],
  "meses_gravados": [202608],
  "meses_stage": [202608],
  "linhas_stage": { "producao_fisica": 3078, "variaveis": 6, "categoria": 27, "territorio": 19 },
  "nulos_stage": { "producao_fisica": 2500 },
  "causa": null,
  "criada_em": "2026-11-07T12:00:00Z",
  "iniciada_em": "2026-11-07T12:00:00Z",
  "concluida_em": "2026-11-07T12:00:05Z"
}
```

Os números acima são ilustrativos. `meses_gravados` são os meses que ganharam uma nova versão bruta, e `meses_stage` são os tratados e carregados na Stage, inclusive os pendentes de execuções anteriores e os reprocessados. `situacao` pode ser `pendente`, `executando`, `sucesso`, `falha` ou `interrompida`. Identificador inexistente devolve `404`.

Em falha, `causa` é `{ "tipo": "...", "mensagem": "..." }`:

| `tipo` | Significado |
|---|---|
| `fonte_indisponivel` | A fonte falhou depois das novas tentativas |
| `estrutura_alterada` | A resposta difere dos metadados, das localidades ou da quantidade esperada, ou os códigos mudaram em relação à versão guardada |
| `dados_invalidos` | Símbolo desconhecido ou índice negativo |
| `periodos_indisponiveis` | Meses pedidos que a fonte não tem, listados na mensagem |
| `sem_dado_bruto` | Reprocessamento sem arquivo guardado |
| `erro_interno` | Erro inesperado; o detalhe fica só no log |

## Verificar novidades

`GET /fonte/novidades`

```json
{ "ha_novidade": true, "meses_alterados": [202609], "meses_pendentes": [] }
```

Só compara os meses-alvo do modo `auto`, sem baixar valores. Se a fonte estiver indisponível, devolve `503`.

## Saúde

`GET /health`: `200` com `{ "status": "ok" }` se o banco responder, ou `503` com `{ "status": "indisponivel" }`. Não depende da fonte.
