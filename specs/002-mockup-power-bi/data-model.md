# Data Model: Mockup do painel Power BI

## Caso de referência (warehouse, 2026-11-08)

Recorte: Ceará (`uf_codigo = 23`), janeiro de 2025 (`periodo = 202501`), Número-índice 2022=100. Fonte: `warehouse.fato_producao_fisica_industrial_2025` com `warehouse.dim_categorias`, pelas consultas de `mockup/dados-referencia.sql`.

| CNAE | Atividade | Índice | Diferença | Destaque |
|---|---|---|---|---|
| 3.13 | Fabricação de produtos têxteis | 145,03 | +43,45 | Top 1 |
| 3.24 | Metalurgia | 136,56 | +34,98 | Top 2 |
| 3.11 | Fabricação de bebidas | 120,05 | +18,47 | Top 3 |
| 3.25 | Fabricação de produtos de metal, exceto máquinas e equipamentos | 112,65 | +11,07 | |
| 3.10 | Fabricação de produtos alimentícios | 105,04 | +3,46 | |
| 3.23 | Fabricação de produtos de minerais não metálicos | 99,07 | −2,51 | |
| 3.15 | Preparação de couros e fabricação de artefatos de couro, artigos para viagem e calçados | 92,71 | −8,87 | |
| 3.19 | Fabricação de coque, de produtos derivados do petróleo e de biocombustíveis | 84,68 | −16,90 | |
| 3.20 | Fabricação de produtos químicos | 81,21 | −20,37 | |
| 3.14 | Confecção de artigos do vestuário e acessórios | 75,99 | −25,59 | |
| 3.27 | Fabricação de máquinas, aparelhos e materiais elétricos | 64,38 | −37,20 | |

Derivados: média das atividades **101,58** (101,58012); **11** atividades com dado; **5 de 11** acima da média.

Média das atividades do Ceará por mês de 2025:

| Jan | Fev | Mar | Abr | Mai | Jun | Jul | Ago | Set | Out | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 101,58 | 95,07 | 95,71 | 89,98 | 100,96 | 98,02 | 104,74 | 109,26 | 108,49 | 115,35 | 105,96 | 84,17 |

Datas: referência **jan/2025**; atualização **08/11/2026**, a maior `data_carga` do fato.

Os valores são conferidos a cada execução do conferidor. Se a fonte revisar os dados, as tabelas acima e as telas precisam ser atualizadas juntas.

## Entidades

### Tela

| Campo | Regra |
|---|---|
| `arquivo` | `tela-NN-slug.svg` |
| `titulo` | Pergunta da tela, com 26 px ou menos e sem caixa alta |
| `carimbos` | "Dados: {referência} · atualizado em {dd/mm/aaaa}", logo abaixo do título |
| `camadas` | `fundo`, `menu`, `cabecalho`, `filtros`, `kpis`, `visuais` e `rodape`, nesta ordem, omitindo as que não existirem |
| `rodape` | Fonte (IBGE, tabela 8888) e selo "MOCKUP — números do warehouse em 08/11/2026" |

### Visual

| Campo | Regra |
|---|---|
| `id` | `kpi-N` ou `visual-*`, em kebab-case, um grupo por visual |
| `grade` | Coluna inicial e quantidade de colunas (2, 3, 4, 6, 8, 9 ou 12) |
| `titulo` | Descritivo, 15 px semibold, sem caixa alta |
| `subtitulo` | Insight, 12 px, na mesma cor do destaque |
| `campo` | Campo ou medida no modelo do painel, registrado no racional |
| `status_pbi` | ✅ nativo, 🔧 adaptação ou 🧩 visual personalizado |

### Racional

Uma seção por visual com gráfico, história, motivo, alternativa recusada, campo ou medida e status no Power BI. No fim, uma lista dos desvios em relação ao `pbi-mockup`.

## Validações

| Regra | Como é verificada |
|---|---|
| Números iguais ao warehouse | `conferir_mockup.py` |
| Nada ultrapassa a moldura, e os cards não se sobrepõem | `check_bounds.py` |
| XML bem formado, sem `<use>`, `<symbol>` ou `currentColor` | `conferir_mockup.py` |
| Cada `url(#x)` aponta para um gradiente, e não para um grupo | `conferir_mockup.py` |
