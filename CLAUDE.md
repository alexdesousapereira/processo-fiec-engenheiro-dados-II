# Prova Prática FIEC: Engenheiro de Dados II (seleção 7778)

Prova do Observatório da Indústria: pipeline da PIM-PF (SIDRA, tabela 8888) até uma camada
analítica consultável via SQL, em Docker Compose e orquestrado por Airflow.

## Onde está cada coisa

| Caminho | Conteúdo |
|---|---|
| [docs/prova-requisitos.md](docs/prova-requisitos.md) | Requisitos da prova com IDs. É o guia do projeto. |
| [docs/fonte-sidra-8888.md](docs/fonte-sidra-8888.md) | Fatos medidos na API do IBGE e armadilhas dos dados |
| [docs/historico.md](docs/historico.md) | Histórico do que foi feito e decidido |
| [README.md](README.md) | Como executar, consultar, reprocessar e testar |
| `dags/`, `src/pim_pf/`, `dbt/`, `sql/`, `tests/` | Código do pipeline |
| `docker/`, `requirements/` | Imagens de ingestão, dbt e Airflow, e dependências da ingestão |
| `powerbi/` | Painel em PBIP, com tema e fundos dentro do relatório |
| [specs/001-pipeline-pim-pf/](specs/001-pipeline-pim-pf/spec.md) | Especificação, plano, contratos e tarefas (Spec Kit) |
| [docs/arquitetura/](docs/arquitetura/ARQUITETURA.md) | Arquitetura atual (API, pandas, dbt, Stage e warehouse em fato e dimensão), ADRs e diagrama único com a atual e a proposta |
| [docs/arquitetura/proposta-futura/](docs/arquitetura/proposta-futura/PROPOSTA-FUTURA.md) | Lakehouse em camadas: não será implementado na prova |
| [.specify/memory/constitution.md](.specify/memory/constitution.md) | Princípios do projeto (Spec Kit) |
| `.claude/skills/gerar-arquitetura-dados/` | Skill que gera a arquitetura de dados |

## Fluxo de trabalho

1. Arquitetura: `/gerar-arquitetura-dados`
2. Spec Kit: `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`

## Regras

- **Atualize [docs/historico.md](docs/historico.md) ao fim de cada etapa**, com data, o que foi
  feito, decisões e pendências. O usuário pediu esse histórico explicitamente.
- Não invente a experiência do candidato. As respostas da Questão 1 vêm do próprio candidato.
- O código será defendido na entrevista técnica, inclusive os trechos feitos com IA.
  Explique os porquês e evite complexidade desnecessária.
- Rode tudo em contêiner. O Python local é 3.14, e não há garantia de que o Airflow rode
  nessa versão.
- Escreva documentação e mensagens para o usuário em português do Brasil.

## Comandos no Windows

O Spec Kit e o uv ficam fora do PATH padrão:

```powershell
$env:PATH = "C:\Users\alexd\.local\bin;$env:PATH"
specify check
```
