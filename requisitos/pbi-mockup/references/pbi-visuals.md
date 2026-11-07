# Visuais nativos do Power BI — catálogo p/ mockup

O mockup só deve propor visuais **construíveis no Power BI**. Esta é a galeria padrão (sem custom). Para cada visual: campos (field wells), a que história serve, e a config que importa pro mockup. Ao final: o que **não é nativo** (workaround ou visual custom) e os **recursos transversais** (linhas de referência, barras de erro, pequenos múltiplos, formatação condicional, sparklines em tabela).

Legenda de status: ✅ nativo · 🔧 nativo via workaround/config · 🧩 visual custom (AppSource)

## Índice

- [Cartões e KPI](#cartões-e-kpi)
- [Colunas e barras](#colunas-e-barras)
- [Linha, área e combinados](#linha-área-e-combinados)
- [Especializados](#especializados)
- [Mapas (só quando a localização importa)](#mapas-só-quando-a-localização-importa)
- [Tabelas](#tabelas)
- [Filtros e IA](#filtros-e-ia)
- [Não-nativos — workaround ou visual custom](#não-nativos-workaround-ou-visual-custom)
- [Escala do visual (Numerro · Sizing Guide)](#escala-do-visual-numerro-sizing-guide)
- [Recursos transversais (configs que enriquecem o mockup)](#recursos-transversais-configs-que-enriquecem-o-mockup)

## Cartões e KPI

| Visual | Campos | História | Config-chave |
|---|---|---|---|
| **Cartão** ✅ | 1 medida | `kpi` | valor de destaque grande; rótulo de categoria; unidade |
| **Cartão (novo)** ✅ | vários dados + rótulos de referência | `kpi` (vários) | múltiplos cards num visual, referência (Δ/meta), layout |
| **KPI** ✅ | Valor, Eixo de tendência, Destino | `kpi` + `vs-meta` | mostra valor + tendência + cor de status vs. meta |
| **Cartão de várias linhas** ✅ | vários campos | `kpi` (lista) | bom p/ mini-tabela de números |

## Colunas e barras

| Visual | Campos | História | Config-chave |
|---|---|---|---|
| **Coluna/Barra empilhada** ✅ | Eixo X, Legenda, Eixo Y, Pequenos múltiplos | `composicao-no-tempo`, `parte-do-todo` | difícil comparar segmentos do meio — use com cautela |
| **Coluna/Barra agrupada (clustered)** ✅ | Eixo X, Legenda, Eixo Y | `comparar-categorias`, `ranking` | ordenar! eixo começa em 0; máx. 2 séries na legenda |
| **Coluna/Barra 100% empilhada** ✅ | Eixo X, Legenda, Eixo Y | `parte-do-todo`, `composicao-no-tempo`, `survey-likert` (workaround) | cor sequencial; 1 barra = parte-do-todo |

> Eixo começa em 0 (obrigatório). Sort por valor. Pequenos múltiplos nativo em coluna/barra/linha/área — ótimo p/ quebrar "muitas categorias" sem virar espaguete.

## Linha, área e combinados

| Visual | Campos | História | Config-chave |
|---|---|---|---|
| **Linha** ✅ | Eixo X, Legenda, Eixo Y, Eixo Y secundário | `tendencia`; **`comparar-2-grupos` (slopegraph)** | **2 categorias no eixo = slopegraph nativo**; máx. 4–5 linhas |
| **Área / Área empilhada** ✅ | Eixo X, Legenda, Eixo Y | `composicao-no-tempo` | empilhada p/ volume; cuidado oclusão |
| **Linha e coluna agrupada/empilhada (combo)** ✅ | Eixo X, Valores de coluna, Valores de linha | `tendencia` + `comparar`; `vs-meta` (linha=meta) | eixo secundário; combo barra+linha p/ valor vs. meta |
| **Gráfico de fita (Ribbon)** ✅ | Eixo X, Legenda, Eixo Y | `ranking` ao longo do tempo | conecta posições entre períodos (quem subiu/desceu) |

## Especializados

| Visual | Campos | História | Config-chave |
|---|---|---|---|
| **Cascata (Waterfall)** ✅ | Categoria, Detalhamento, Eixo Y | `parte-do-todo` de **variação** (de A até B) | agrupa "Outros"; cores +/−; ótimo p/ ponte de resultado |
| **Funil (Funnel)** ✅ | Grupo, Valores | `ranking`/estágios, conversão | taxa de conversão entre estágios |
| **Dispersão (Scatter/Bubble)** ✅ | Detalhes, Eixo X, Eixo Y, Tamanho, Legenda, Eixo de reprodução | `correlacao` | bolha = 3ª medida; Play = animação no tempo |
| **Pizza / Rosca** ✅ | Legenda, Valores, Detalhes | `parte-do-todo` (≤3–4 fatias) | maior às 12h, horário; nunca múltiplas pizzas |
| **Treemap** ✅ | Categoria, Detalhes, Valores | `parte-do-todo` hierárquico / muitas partes | área = valor; ok p/ "muitas categorias" |
| **Medidor (Gauge)** ✅ | Valor, Mínimo, Máximo, Destino | `vs-meta` | **nativo, mas desencorajado** (impreciso, ocupa espaço) — só se o cliente exigir o look de medidor; senão KPI/combo |

## Mapas (só quando a localização importa)

| Visual | Campos | História | Config-chave |
|---|---|---|---|
| **Mapa (bolha, Bing)** ✅ | Local, Lat/Long, Tamanho da bolha, Saturação | `geografico` | bolha proporcional |
| **Mapa coroplético (preenchido)** ✅ | Local, Lat/Long, Saturação de cor | `geografico` | área pintada por intensidade de 1 tom |
| **Mapa de formas (Shape map)** ✅ | Local, Saturação | `geografico` | mapas custom via TopoJSON |
| **Mapa do Azure / ArcGIS** ✅ | Local, Lat/Long, Tamanho, Legenda | `geografico` | camadas avançadas |

## Tabelas

| Visual | Campos | História | Config-chave |
|---|---|---|---|
| **Tabela** ✅ | Colunas | detalhe, `qualitativo` (tabela heat) | **formatação condicional**: barras de dados, escala de cor, ícones, sparklines |
| **Matriz** ✅ | Linhas, Colunas, Valores | `parte-do-todo`, tabela heat, cruzamento | formatação condicional + sparklines + subtotais + drill |

## Filtros e IA

| Visual | Campos | Uso |
|---|---|---|
| **Segmentação (Slicer)** ✅ | Campo | filtro: lista, lista suspensa, entre (intervalo), data relativa, hierarquia; **botão de segmentação** (recente) |
| **Árvore de decomposição** ✅ | Analisar, Explicar por | drill/explicação de fatores; "encontrar próximo" (IA) |
| **Principais influenciadores** ✅ | Analisar, Explicar por | drivers/`correlacao` (IA) |
| **Q&A / Narrativa inteligente** ✅ | auto | linguagem natural / texto gerado p/ `qualitativo` |
| **Visual R / Python** ✅ | Valores | qualquer gráfico via ggplot/matplotlib — saída do "não-nativo" |

---

## Não-nativos — workaround ou visual custom

| Ideal dataviz | Em Power BI | Como |
|---|---|---|
| **Slopegraph** | ✅ nativo | **Linha** com exatamente 2 categorias no eixo |
| **Bullet graph** | 🔧 / 🧩 | combo **coluna + linha de meta (constante)** + barra de erro; ou **KPI/Cartão**; ou custom *Bullet Chart* |
| **Dumbbell dot plot** | 🧩 | custom (*Dumbbell* / *Dot Plot by MAQ*) |
| **Lollipop** | 🧩 | custom |
| **Dot plot** | 🧩 | custom |
| **Histograma** | 🔧 / 🧩 | **agrupar** coluna numérica em bins → **coluna**; ou custom *Histogram* |
| **Box & whisker** | 🧩 | custom |
| **Sankey** | 🧩 | custom **certificado** (*Sankey*) |
| **Word cloud** | 🧩 | custom (verificar no AppSource) |
| **Mapa de calor (tabela)** | ✅ | **Matriz** + formatação condicional (escala de cor) |
| **Radar** | 🧩 | custom — desencorajado mesmo assim |

**Regra no mockup:** prefira o ✅ nativo. Quando o ideal dataviz só existir como 🔧 ou 🧩, **renderize o ideal no SVG** e **anote no racional** o status (workaround/custom + qual visual), pra fase PBIX não ter surpresa. Ex.: "slopegraph = Linha com 2 pontos (nativo)"; "bullet = custom *Bullet Chart* ou combo coluna+linha de meta".

---

## Escala do visual (Numerro · Sizing Guide)

Dimensione o visual conforme o nível de detalhe; isso define em que andar da tela ele entra (ver `layout-dashboard.md`).

- **Escala pequena (alto nível, topo):** Cartão · KPI · Segmentação (filtro) · Medidor · Rosca (visão geral).
- **Escala grande (detalhe, meio/base):** Barras/Colunas · Linha+Coluna · Área · Treemap · Mapas · Tabela · Matriz · Dispersão · Fita (Ribbon) · Cascata · Funil · Rosca (granular).

Regra: **não encolher visual grande pra caber mais** — gera margem irregular e bagunça. Se não cabe com folga, vira outra tela/aba.

## Recursos transversais (configs que enriquecem o mockup)

- **Linhas de análise** (painel Análise): constante, média, mín/máx, mediana, percentil, **tendência**. → use p/ `vs-meta` (linha de meta), benchmark, alvo. Nativo em linha/coluna/barra/área/combo/dispersão.
- **Barras de erro**: nativo em linha/coluna/barra/combo. → meio-bullet e medidas de variabilidade.
- **Pequenos múltiplos**: nativo em coluna/barra/linha/área. → quebra "muitas séries/categorias" sem espaguete.
- **Formatação condicional** (tabela/matriz): cor de fundo, cor de fonte, **barras de dados**, ícones, **escala de cor** (heat). → KPIs em tabela, tabela-heat qualitativa, pontos-indicadores.
- **Sparklines** em tabela/matriz: mini-linha/coluna na célula. → tendência ao lado do número.
- **Dicas de ferramenta de página** (report page tooltips): tela inteira vira tooltip ao passar o mouse. → detalhe sob demanda (Few: "details on demand").
- **Indicador/seta de tendência** no Cartão novo e KPI. → Δ vs. período/meta.
- **Tema JSON**: cores e fontes padronizadas (entregável do projeto — ver checklist do Guia, idx 56).

> Para `tendencia`: marque os pontos realmente medidos (marcadores na linha). Para `comparar-categorias`/`ranking`: ordene e destaque 1 com a cor de ação. Para `vs-meta`: prefira KPI/combo+linha de meta a Gauge.
