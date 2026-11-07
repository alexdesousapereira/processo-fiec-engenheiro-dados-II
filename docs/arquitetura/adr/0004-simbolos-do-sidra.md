# ADR 0004: Tratamento dos símbolos do SIDRA

**Status:** proposta, 2026-11-06

## Contexto

A coluna de valor mistura números e símbolos. Documentação de terceiros descreve `-` como zero absoluto
e `...` como dado indisponível; a confirmação nas notas da tabela está pendente. Medições em 2025:

- `-` aparece em 2.892 das 4.896 linhas das atividades de transformação.
- Os 167 pares UF × atividade com número aparecem nos 12 meses, e os demais nunca têm número.

Esse padrão indica atividade sem dado na UF, não produção zero em um mês específico.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| `-` como zero | Segue a legenda geral | Média do Ceará em 01/2025 cairia de 101,58 para 46,56 |
| Descartar as linhas com símbolo | Simples | Perde a informação da fonte |
| Valor nulo, com `simbolo_origem` | Média correta; decisão reversível | Uma coluna a mais |

## Decisão

Em `fproducao_fisica`, `valor` fica nulo e `simbolo_origem` guarda o símbolo. Símbolo desconhecido interrompe
a carga antes da Stage. A view analítica considera só linhas com valor.

## Consequências

- `AVG` considera apenas atividades com dado na UF, como a análise requer.
- Quem precisar da interpretação de zero ainda consegue aplicá-la a partir de `fproducao_fisica`.
- A decisão diverge da legenda geral, e por isso a evidência fica registrada. Se as notas da tabela
  definirem outro significado, a mudança se limita à regra de tratamento e ao reprocessamento dos arquivos brutos.
