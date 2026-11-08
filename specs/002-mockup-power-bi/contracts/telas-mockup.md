# Contrato: telas do mockup

As duas telas usam o esqueleto `canvas-topo-marca` do `pbi-mockup`.

## Grade

Área útil x 24 → 1256 (1232 px), 12 colunas, gutter 20 e coluna de 84,33 px.

```text
x(coluna) = 24 + coluna × 104,33
largura(n colunas) = n × 84,33 + (n − 1) × 20
```

| Divisão | Coluna inicial | x | Largura |
|---|---|---|---|
| 4 + 4 + 4 | 0, 4 e 8 | 24, 441,33 e 858,67 | 377,33 |
| 8 + 4 | 0 e 8 | 24 e 858,67 | 774,67 e 377,33 |

O bloco de 4 colunas do corpo começa no mesmo eixo do 3º KPI.

## Zonas verticais

| Zona | y | Altura |
|---|---|---|
| Barra de marca e navegação (`menu`) | 0 → 60 | 60 |
| Título e carimbos (`cabecalho`) | 76 → 124 | 48 |
| KPIs | 132 → 220 | 88 |
| Corpo (`visuais`) | 240 → 652 | 412 |
| Rodapé | 672 → 696 | 24 |

## Tela 1: capa (`tela-01-capa.svg`)

| Bloco | Conteúdo |
|---|---|
| `menu` | Marca "Observatório da Indústria"; abas **Capa** (ativa) e Análise |
| `cabecalho` | Título: "Quais atividades puxam a produção industrial em cada UF?"; carimbos de data |
| `visuais` / `visual-principal` | Recorte (Indústria de Transformação, 2025, Número-índice 2022=100), o que a análise responde e o botão "Abrir a análise" |
| `rodape` | Fonte e selo de mockup |

## Tela 2: análise (`tela-02-analise.svg`)

| Bloco | Grade | Título | Subtítulo (insight) |
|---|---|---|---|
| `menu` | n/a | Abas Capa e **Análise** (ativa) | n/a |
| `cabecalho` | n/a | "Indústria de Transformação — atividades da UF no mês" | Carimbos: "Dados: jan/2025 · atualizado em 08/11/2026" |
| `filtros` | Direita do título | Pílula "Jan/2025" (ativa) e "UF: Ceará ▾" | n/a |
| `kpi-1` | Colunas 0 a 3 | "Atividade líder" | Têxteis · 145,03 · +43,45 sobre a média |
| `kpi-2` | Colunas 4 a 7 | "Média das atividades" | 101,58 · 11 atividades com dado |
| `kpi-3` | Colunas 8 a 11 | "Acima da média" | 5 de 11 atividades |
| `visual-principal` | Colunas 0 a 7 | "Índice de produção por atividade · 2022=100" | "Têxteis lidera, 43,45 pontos acima da média da UF" (cor de ação) |
| `visual-1` | Colunas 8 a 11 | "Média das atividades por mês · 2025" | "Janeiro em 101,58; pico em outubro (115,35)" (cor de ação) |
| `rodape` | n/a | Fonte e selo de mockup | n/a |

**`visual-principal`**:
- 11 barras horizontais ordenadas, começando no zero.
- Top 3 na cor de ação e as demais em `#C9CDD4`.
- Linha tracejada da média (101,58), explicada na legenda.
- Rótulo de cada barra: índice e diferença, como em "145,03 (+43,45)".
- Legenda no topo-esquerda: "Top 3", "Demais" e "Média da UF".

**`visual-1`**:
- Linha de 12 meses, com eixo de valor rotulado.
- Janeiro marcado na cor de ação, e os demais pontos em neutro.

## Correspondência com o painel

| Bloco do mockup | Visual do PBIP | Campo ou medida |
|---|---|---|
| `filtros` | `filtro_mes`, `filtro_uf` | `dim_calendario[mes_nome]`, `dim_territorio[territorio_nome]` |
| `kpi-1` | `cartao_lider` | `[Atividade líder]` e `[Diferença do líder]` |
| `kpi-2` | `cartao_media` | `[Média das atividades]` e `[Atividades com dado]` |
| `kpi-3` | `cartao_acima` | `[Atividades acima da média]` e `[Atividades com dado]` |
| `visual-principal` | `barras_indice` | `vw_transformacao_2025[atividade_nome]`, `[Índice de produção]`, `[Cor do ranking]` e linha constante `[Média das atividades]` |
| `visual-1` | `linha_media` | `dim_calendario[mes_nome]` e `[Média das atividades]`, sem resposta ao filtro de mês |
