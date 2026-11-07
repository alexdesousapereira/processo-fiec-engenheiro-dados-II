# ADR 0005: Power BI como ferramenta de visualização

**Status:** proposta, 2026-11-06

## Contexto

A prova exige uma estrutura consultável via SQL, sem pedir um painel. Ela informa que os dados serão
usados por analistas e equipes de negócio, e cita Power BI e QlikSense na Questão 1.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| Sem visualização | Escopo mínimo | Não mostra como o negócio consome os dados |
| Power BI | Citado na prova; conector nativo de PostgreSQL | Desktop só para Windows; fora do Compose |
| Metabase ou Superset | Sobem no Compose | Mais um serviço pesado, sem exigência da prova |

## Decisão

Usar Power BI como consumidor do DW, por meio de um usuário somente leitura e da view
`dw.vw_transformacao_2025`. Ele fica fora do Compose e nenhuma etapa do pipeline depende dele.

## Consequências

- O pipeline e a consulta exigida funcionam sem o Power BI.
- O PostgreSQL precisa expor sua porta para a máquina local, somente no ambiente de desenvolvimento.
- A atualização do painel é manual no Power BI Desktop; atualização agendada exigiria serviço e gateway.
- O escopo do painel ainda precisa ser definido.
