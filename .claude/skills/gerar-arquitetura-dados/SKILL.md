---
name: gerar-arquitetura-dados
description: Gera a arquitetura de uma solução de dados a partir de requisitos e de medições reais da fonte, com rastreabilidade, decisões registradas (ADRs), diagramas Mermaid, camadas, modelo de dados, estratégia de carga, qualidade e orquestração. Use sempre que o usuário pedir para desenhar, gerar, propor, revisar ou atualizar uma arquitetura de dados, pipeline, data lake, lakehouse, medallion, modelagem analítica ou fluxo ETL/ELT, mesmo sem usar a palavra "arquitetura", e especialmente na prova prática da FIEC (PIM-PF, SIDRA 8888, Airflow, Docker).
---

# Gerar arquitetura de dados

Produza uma arquitetura que a pessoa consiga implementar e defender em uma entrevista técnica.
Uma boa arquitetura aqui é rastreável aos requisitos, baseada no comportamento medido da fonte e
tão simples quanto os requisitos permitem.

## Entradas

Leia o que existir antes de desenhar:

- Requisitos: `docs/prova-requisitos.md` (o original prevalece em caso de dúvida)
- Fatos da fonte: `docs/fonte-sidra-8888.md`
- Princípios: `.specify/memory/constitution.md`
- Histórico: `docs/historico.md`
- Arquitetura anterior: `docs/arquitetura/`, para evoluí-la em vez de recomeçar

## Processo

### 1. Confirme os fatos da fonte

Os fatos de uma fonte mudam com o tempo, então verifique os que sustentam uma decisão. Para o
SIDRA, rode:

```powershell
py -I .claude/skills/gerar-arquitetura-dados/scripts/perfil_sidra.py --saida <arquivo-temporario>.json
```

Compare o resultado com `docs/fonte-sidra-8888.md` e atualize esse documento se algo mudou. Para
outra fonte, meça o equivalente: volume, chaves, nulos, duplicidades, limites e frequência de
atualização. Separe claramente **medido**, **documentado por terceiros** e **hipótese**, porque a
pessoa precisará dizer na entrevista como sabe cada coisa.

### 2. Transforme fatos em consequências

Para cada comportamento relevante da fonte, escreva o que ele obriga o desenho a fazer. Essa é a
parte mais valiosa do documento: ela mostra raciocínio, não apenas ferramentas.

### 3. Tome as decisões

Consulte [references/decisoes.md](references/decisoes.md) e cubra cada área aplicável. Compare no
mínimo duas alternativas reais e recomende uma. Pergunte ao usuário somente quando a escolha
depender de algo que só o usuário sabe, como experiência prévia, prazo ou limite da máquina.

Prefira o mais simples que atenda ao volume medido. Ferramentas distribuídas se justificam pelo
volume, pela exigência da prova ou por um padrão explícito do time, não por parecerem sofisticadas.

### 4. Escreva os artefatos

```
docs/arquitetura/
├── ARQUITETURA.md
└── adr/
    └── NNNN-titulo-curto.md
```

Use exatamente esta estrutura em `ARQUITETURA.md`:

```markdown
# Arquitetura: <solução>

## 1. Resumo
Até 10 linhas: o problema, a solução e as 3 decisões mais importantes.

## 2. Fatos da fonte e consequências
| Fato | Evidência | Consequência no desenho |

## 3. Visão geral
Diagrama Mermaid (flowchart) da fonte ao consumo, com o orquestrador.

## 4. Camadas de dados
Para cada camada: propósito, formato, particionamento, caminho, grão, chave e campos técnicos.

## 5. Estratégia de carga
Carga inicial, incremental, atualizações tardias, revisões e reprocessamento.

## 6. Modelo analítico
Diagrama Mermaid (erDiagram), grão, regras de cálculo e esboço da consulta exigida.

## 7. Qualidade dos dados
| Verificação | Camada | Ação em caso de falha |

## 8. Orquestração
Diagrama da DAG, agendamento, retries, idempotência e parâmetros.

## 9. Ambiente
Serviços do Compose, papel de cada um, versões, volumes e configuração.

## 10. Rastreabilidade
| ID do requisito | Onde é atendido | Como verificar |

## 11. Riscos e pendências
| Item | Impacto | Mitigação ou próximo passo |

## 12. Perguntas prováveis na entrevista
Pergunta e resposta curta para cada decisão difícil.
```

Em cada ADR, registre contexto, alternativas consideradas, decisão e consequências, incluindo o
que se perde com a escolha.

### 5. Verifique antes de concluir

- Todo ID de requisito aparece na seção 10; o que faltar deve estar explícito na seção 11.
- Toda regra analítica foi testada contra uma amostra real. Calcule ao menos um caso à mão.
- Todo fato tem evidência, e toda hipótese está marcada.
- Os diagramas Mermaid são válidos e condizem com o texto.
- Nenhum componente existe sem requisito ou justificativa.

### 6. Registre e encaminhe

Acrescente a etapa a `docs/historico.md`, com decisões e pendências. Depois, resuma para o usuário
as decisões que merecem revisão e indique o próximo passo do Spec Kit: `/speckit-specify` usando
`docs/arquitetura/ARQUITETURA.md` como contexto.

Esta skill produz o desenho, não a implementação. Escreva código apenas para medir a fonte ou
validar uma regra, pois a implementação pertence às tarefas do Spec Kit.
