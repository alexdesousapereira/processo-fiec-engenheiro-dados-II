# SVG kit — tokens + primitivos

Canvas PBI: `viewBox="0 0 1280 720"`. Fonte `Segoe UI` (nativa do PBI → mockup fiel). Texto sempre como `<text>` (nítido, editável). Substitua `{{COR_ACAO}}` pelo hex da marca do cliente.

> **Templates prontos (use como ponto de partida — `../templates/`):** todos seguem o **§Grid padrão** (margem 24, gutter 20) e já vêm com os **ícones Material embutidos no `<defs>`** (abrem completos no navegador/VSCode).
> - **Ícones — Google Material Symbols.** Dois arquivos:
>   - `icons-gallery.svg` — **galeria VISÍVEL** (114 ícones com o nome de cada `ic-…`). **Abra este** para escolher o ícone.
>   - `icons-material.svg` — **biblioteca** de `<symbol>` (`viewBox 0 -960 960 960`). Abrir direto mostra **branco** (`display:none`) — é normal; é a fonte de onde o skill **copia o `d=` do ícone**.
>   - **⚠️ FIGMA-SAFE — não use `<use>`/`<symbol>`/`currentColor` no SVG final.** O Figma ignora o `viewBox` do `<symbol>` e o `currentColor` → o ícone explode em preto. **Asse cada ícone como `<path>` com transform + fill em hex:** `<g transform="translate(X,Y) scale(W/960) translate(0,960)" fill="#HEX"><path d="…"/></g>` (W = tamanho em px, ex.: 24 → scale 0.025). Assim renderiza igual em navegador, **Figma** e PBI.
> - **Esqueletos de tela (escolha pelo layout/menu/tema pedido):**
>   - `canvas-base.svg` — menu em abas no topo (genérico), 4 KPIs, principal + 2 de apoio. Claro.
>   - `canvas-left-rail.svg` — **app-shell claro**, trilho de ícones à esquerda (72px, estilo ex.16), 4 KPIs + 2 linhas (wide + 2).
>   - `canvas-left-rail-dark.svg` — **app-shell escuro sobre gradiente** (estilo edição do cliente), trilho à esquerda, cards baixos + assimétricos.
>   - `canvas-topbar-grid.svg` — **barra de menu no topo** (abas, estilo ex.14), 4 KPIs + 2 linhas (wide + 2). Claro.
>   - `canvas-cards-accent.svg` — **app-shell (estilo ex.20)**: superfície branca com aba, trilho, **cards de topo colorido** + card em gradiente.
>   - `canvas-2x2.svg` — **grade 2×2 limpa** + cabeçalho, sem menu. Para 4 histórias de peso parecido.
>   - `canvas-5kpi-list.svg` — **5 KPIs** + lista/ranking lateral + visual central + faixa inferior.
>   - `canvas-hero-banner.svg` — **hero colorido** no topo + KPIs sobrepostos + grade (visão executiva).
>   - `canvas-wide-sidebar.svg` — **sidebar largo (240px)** com nav + filtros (data no sidebar) + conteúdo.
>   - `canvas-kpi-footer.svg` — **top bar colorido + KPIs com faixa de rodapé colorida** (rótulo) + ícone no topo (estilo ex.09).
>   - `canvas-grouped-panel.svg` — **sidebar + coluna de KPIs + painel agrupado** (container colorido com visuais da MESMA pergunta) + faixa inferior (estilo ex.12).
>   - `canvas-banda-kpi-colorida.svg` — **banda de 4 KPIs em cor cheia** (cartões coloridos, não brancos) + corpo branco (estilo ex.01). Claro.
>   - `canvas-moldura.svg` — **canvas emoldurado**: superfície branca arredondada dentro de uma moldura colorida (gradiente da marca) + KPIs + grade (estilo ex.03/11). Claro.
>   - `canvas-cartoes-segmento.svg` — **4 cartões-categoria GRANDES e sólidos** no topo (número-âncora por segmento) + corpo (estilo ex.04). Claro.
>   - `canvas-topo-marca.svg` — **barra superior de marca full-width** (logo + cliente + nav em abas) + faixa KPI + 2 bandas largas (estilo ex.17/18/19). Claro.
>   - `canvas-escuro-ranking.svg` — **dashboard escuro** (réplica FIEL do ex.22, geometria exata do Figma): painel com **moldura angular entalhada**, trilho de ícones, 3 KPIs escuros com **acento colorido no topo-esquerdo + base-direita e borda** (#F65164/#E0A458/#4E7CFF) + chip de ícone, painel + área de gráfico, e **cartão-ranking em gradiente** (#7033FF→#F65164) com troféus.
>   - _"Linhas full-width": parta do `canvas-left-rail.svg` e troque a grade por 2 cards de largura total._
> - **Mapa exemplo→template** (`templates/novos/exemplo_NN`): 01→`banda-kpi-colorida` · 02→`5kpi-list` · 03/11→`moldura` · 04→`cartoes-segmento` · 06→`2x2` · 09→`kpi-footer` · 12→`grouped-panel` · 14→`topbar-grid` · 16→`left-rail` · 17/18/19→`topo-marca` · 20→`cards-accent` · 22→`escuro-ranking` · 05/10→`left-rail-dark`.
> - **Exemplos não convertidos (redundantes/fora de escopo):** 07 (= `base`/`topbar-grid`, layout genérico) · 08 (capa/landing com ilustração, não é tela de dashboard) · 13 (= `wide-sidebar` com sidebar colorido, re-skin) · 15 (= `base` com fundo tingido full-bleed, é escolha de tema/fundo).
> - `cards.svg` — **biblioteca de 12 cards de KPI** (básico, Δ período, vs-meta/bullet, sparkline, sparkline-área, número grande, multi-métrica, valor+meta %, valor+ano anterior, topo colorido, donut+valor, gradiente+meta). Copie o card que precisa para a faixa de KPIs. **Restrição:** os cards **4 e 5 (sparkline)** e **11 (donut)** só funcionam num **card maior que o padrão** — sparkline precisa de **largura** extra; donut precisa de **altura/largura**. Em KPI pequeno (faixa-padrão), use 1/2/3.
> - `components.svg` — **catálogo de gráficos** com "Quando usar": barra ordenada, linha, área, área empilhada, **coluna+linha (eixo duplo)**, **dispersão/bolha**, **cascata (ofensor)**, **árvore de decomposição**, barra %+linha 100% (vs-meta), 100% empilhada, treemap, **gauge (anti-padrão)**, **funil (cuidado)**, tabela/matriz condicional. Copie o bloco **dentro** da moldura de visual do canvas.
>
> **Todos os SVGs já vêm Figma-safe** (ícones assados como `<path>`+transform+fill; sem `<use>`/`<symbol>`/`currentColor`; 1 `<defs>` só com gradientes) **e com camadas nomeadas** (ver §Camadas nomeadas). `cards.svg` traz **22 cards** (cada um um `<g id="card-NN-...">` deletável de uma vez): 12 por função + **10 variações de acento** (posição do destaque — bloco/barra/borda/topo/canto, dos 10 cards de `novos/Card`). `components.svg` traz **14 gráficos** (`<g id="grafico-NN-tipo">`).
> Todos os esqueletos já trazem: título que **localiza** a tela (`{{AREA}} — {{ASSUNTO}}`), os **dois carimbos de data** sob o título, **barra de filtros** (data destacada + N filtros + "✕ Limpar", dentro da margem), e rodapé só com fonte + selo. A cor de ação default é `#4E7CFF` (azul) — re-skine pela marca do cliente. `../templates/novos/` guarda os backgrounds-referência (incl. `exemplo_20.jpg`) e `../templates/novos/Card/` os 10 cards-referência que originaram a biblioteca.
>
> Os snippets abaixo documentam cada primitivo; os arquivos em `templates/` são a versão consolidada e conhecida-boa.

## Índice

- [Camadas nomeadas (edição no Figma)](#camadas-nomeadas-edição-no-figma)
- [Contraste (texto × fundo) — WCAG AA](#contraste-texto-fundo-wcag-aa)
- [Fidelidade de formas (NÃO desenhe formas orgânicas à mão)](#fidelidade-de-formas-não-desenhe-formas-orgânicas-à-mão)
- [Tokens](#tokens)
- [Títulos de visual (convenção)](#títulos-de-visual-convenção)
- [Legenda — sempre no topo-esquerda (inviolável)](#legenda-sempre-no-topo-esquerda-inviolável)
- [Template do canvas](#template-do-canvas)
- [Posicionamento calculado pela grid (12 colunas — OBRIGATÓRIO)](#posicionamento-calculado-pela-grid-12-colunas-obrigatório)
- [Seletor de período + carimbos de data](#seletor-de-período-carimbos-de-data)
- [Barra de filtros (N filtros + "Limpar")](#barra-de-filtros-n-filtros-limpar)
- [Canvas por ambiente](#canvas-por-ambiente)
- [KPI card (ícone em box + hierarquia de texto + mini-bullet)](#kpi-card-ícone-em-box-hierarquia-de-texto-mini-bullet)
- [Número grande isolado (KPI puro)](#número-grande-isolado-kpi-puro)
- [Barra ordenada (1 destacada) — comprimento, começa em 0](#barra-ordenada-1-destacada-comprimento-começa-em-0)
- [Linha com marcadores (tendência)](#linha-com-marcadores-tendência)
- [Vs. meta — barra de % + linha constante em 100% (NATIVO)](#vs-meta-barra-de-linha-constante-em-100-nativo)
- [Slopegraph (comparar 2 grupos em N variáveis)](#slopegraph-comparar-2-grupos-em-n-variáveis)
- [Donut de 1 fatia destacada (reforçar 1 número)](#donut-de-1-fatia-destacada-reforçar-1-número)
- [Lollipop (ranking leve)](#lollipop-ranking-leve)
- [Scatterplot (correlação)](#scatterplot-correlação)
- [Sparkline (dentro de card/tabela)](#sparkline-dentro-de-cardtabela)
- [Barra empilhada divergente (Likert)](#barra-empilhada-divergente-likert)
- [Tabela com pontos-indicadores (status vs. meta)](#tabela-com-pontos-indicadores-status-vs-meta)
- [Mapa / Sankey (placeholders)](#mapa-sankey-placeholders)
- [Hierarquia de texto (Numerro · Working with Text)](#hierarquia-de-texto-numerro-working-with-text)
- [Cor acessível (Numerro · daltonismo)](#cor-acessível-numerro-daltonismo)
- [Regras de uso do kit](#regras-de-uso-do-kit)

## Camadas nomeadas (edição no Figma)

Ao abrir o SVG no Figma, o atributo `id` de um `<g>` vira o **nome da camada**. Por isso **todo mockup é uma árvore de grupos nomeados** — o cliente identifica o bloco e deleta/edita de uma vez (em vez de caçar item por item). Estrutura top-level padrão (nesta ordem; omita o que não existir):

```
<g id="fundo">      rects/paths/gradientes de fundo e superfície
<g id="menu">       sidebar / trilho / barra de navegação (logo + itens + ativo)
<g id="cabecalho">  título da página + os 2 carimbos de data
<g id="filtros">    barra de filtros → dentro: filtro-data, filtro-1, filtro-2[, filtro-3], filtro-limpar
<g id="kpis">       faixa de KPIs → dentro: kpi-1, kpi-2, … (cada cartão inteiro)
<g id="visuais">    área de gráficos → dentro: visual-principal, visual-1, visual-2, … (e visual-destaque p/ card em gradiente)
<g id="rodape">     fonte + selo "MOCKUP"
```

Regras: **cada cartão/visual/filtro é UM grupo** (rect + ícone + textos juntos), para deletar/duplicar em bloco. `id` em **kebab-case PT-BR**. Catálogos: `cards.svg` usa `card-NN-tipo`, `components.svg` usa `grafico-NN-tipo`. **Ao gerar uma tela nova ou editar um template, mantenha essa estrutura de grupos** — é o que torna o arquivo editável. Envolver em `<g id>` (sem transform) **não altera a renderização**.

> ⚠️ **id de grupo NÃO pode colidir com id de gradiente.** Se um `<g id="hero">` e um `<linearGradient id="hero">` existem no mesmo arquivo, `fill="url(#hero)"` resolve para o GRUPO (não pinta nada → forma some, texto fica sobre o fundo da página). Use sufixo nos gradientes (`hero-grad`, `ranking-grad`, `moldura-grad`). Cheque: cada `url(#x)` deve ter um único `id="x"`, e esse id deve ser de um gradiente/clip, não de um grupo.

## Contraste (texto × fundo) — WCAG AA

Texto sobre preenchimento colorido tem que ter contraste. Regra prática:
- **Texto pequeno** (rótulo, filtro, insight — ~10–14px): contraste **≥ 4,5:1**.
- **Texto grande/bold** (número de KPI, título ≥24px ou ≥19px bold): **≥ 3:1**.
- **A cor de ação `#4E7CFF` é clara demais para texto branco pequeno** (~3,7:1). Sob texto branco pequeno (faixas, barras de topo, painéis, cartões cheios), use **tons PROFUNDOS**: azul `#2E50C8` · violeta `#6A2BD9` · vermelho `#B5283C` · teal `#0E6E62` · navy `#14215C`. O `#4E7CFF` fica para **ícone/linha/barra** ou **texto grande/bold** sobre branco.
- **Fundo claro pede texto escuro.** Em preenchimento claro (`#1FB8A6`, `#F4A261`, `#56CFE1`, `#E0A458`) **não** use texto branco — use `#33394C` (ink). Escolha a cor do texto pela luminância do fundo (claro→texto escuro; escuro→texto branco).
- **Gradiente sob texto**: garanta que **as duas pontas** passem (não termine num tom claro sob texto branco — ex.: o hero usa `#14215C→#4E7CFF`, navy onde fica o texto; o ranking escuro usa `#6A2BD9→#B5283C`, profundo nas duas pontas).
- **Chip branco** (filtro/pílula) sobre faixa colorida resolve de vez: fundo `#FFFFFF` + texto `#5C6470`/cor-de-ação — legível em qualquer banner.

## Fidelidade de formas (NÃO desenhe formas orgânicas à mão)

Formas **arredondadas compostas/orgânicas** — abas "folder", recortes côncavos, painéis com cantos diferentes, sidebars com notch — são difíceis de acertar à mão e saem tortas. **Não precisa de biblioteca de runtime.** A regra:

- **Quando um template replica um exemplo** (mapa exemplo→template acima), **reaproveite a geometria do próprio `novos/exemplo_NN.svg`** (export do Figma, paths exatos): extraia os `<rect>`/`<path>` do chrome (container, painel, sidebar, aba) e **descarte só o texto vetorizado e os dados**; mantenha os retângulos/paths de fundo como estão. Foi assim que o `canvas-grouped-panel` (ex.12) ficou fiel: copiou os rx/coords reais (painel `462,50 758×374 rx36`, cards `223×222 rx16`, etc.).
- **Slots de gráfico são transparentes/vazios** — os `<rect>` brancos onde o visual vai entrar **não devem ser preenchidos** com conteúdo (o gráfico entra por cima no PBIX). Não sobrescreva esses elementos.
- **Marcas de dado são quadradas** (`rx=0`): barras, barras de dados (data bars da árvore de decomposição), células. Pílula arredondada em barra = erro (ver árvore de decomposição em `components.svg`, fiel ao `novos/Decomposition tree.svg`: trilho + preenchimento **quadrados e finos**, ~8px). Só **molduras de card/visual** e **pílulas de slicer/nav** são arredondadas.
- **Aba folder do `cards-accent`**: o cliente exportou o `.svg` do Figma; usei os **paths exatos** (superfície com recorte, sidebar, item ativo). Quando faltar o SVG de uma forma orgânica, peça o export em vez de aproximar à mão.

## Tokens

```
Fonte:        'Segoe UI', system-ui, Inter, sans-serif
--acao:       {{COR_ACAO}}   (azul principal / destaque — escasso!)   default #4E7CFF
--bg-page:    #F5F7FB      --bg-card:   #FFFFFF      --border:    #E6E8EC      --area-externa(app-shell): #EDEFF2
--ink:        #33394C      --ink-2:     #5C6470      --ink-3:     #7C8595
--grid:       #EDEFF2      --tabela-zebra: #F4F6F8     --neutral(dados/contexto): #C9CDD4
--semânticas: ok #2E9E5B · alerta/neutral #E0A458 · ruim #D64545     --meta(linha): #7C8595
--categóricas (séries em empilhados/treemap/área, na ordem): #7033FF #F65164 #1FB8A6 #F4A261 #56CFE1 #B48EAD #7C8595
--app-shell navy: #14215C   --navy-texto-claro: #AEB6C6   --on-cor-clara (texto escuro sobre fundo claro): #33394C
--preenchimento-profundo (PRECISA p/ texto branco pequeno — ver §Contraste): azul #2E50C8 · violeta #6A2BD9 · vermelho #B5283C · teal #0E6E62 · navy #14215C
Tema escuro (variante): bg-page #0F1117 · bg-card #181B22 · border #2A2E38 · grid #262B35 · ink #ECEFF4 · ink-2 #C7CCD3 · ink-3 #8A929E · ação #4E7CFF · ação-clara #4C8DFF/#7FB0FF/#9DC0FF · semânticas bom #3FBF77 · ruim #FF6B6B
> Mockup e tema DEVEM usar os mesmos tokens (mesmo dark/light, mesma cor de ação). Veja os valores em /corporate-pbi-tema/references/dark-vs-light.md.
> Cor de AÇÃO é escassa (só no que o insight cita). Categóricas só quando há de fato N categorias a distinguir. Semânticas com parcimônia. Tudo o mais é neutro.
```

Tamanhos de texto (px): título da página 26 semibold · subtítulo da página 14 · rótulo KPI 12 caps · número KPI 38–44 · **título de visual 15 semibold (sentence-case, nome descritivo)** · **subtítulo de visual / insight 12 (cor condicional)** · rótulo de eixo/categoria 12–13 · valor sobre barra 12.

## Títulos de visual (convenção)

Dois níveis distintos:

- **Título da página** (topo da tela, 26 semibold): o **ponto/pergunta** da tela — ex.: "Estamos batendo a meta e crescendo?".
- **Título de cada visual** (15 semibold, `#33394C`, **sentence-case**): o **nome descritivo** do gráfico — ex.: "Faturamento mensal · R$ milhões", "Atingimento de meta por vendedor". **Nunca caixa alta** (caps em frase cansa e grita) e **nunca** o insight.
- **Subtítulo de visual = insight dinâmico (OPCIONAL — opt-in do cliente)** (12, logo abaixo do título): o **takeaway** que o número conta — ex.: "2025 acelerou e superou a meta". Recebe **cor condicional**: bom = verde / cor de ação; ruim = vermelho; neutro = `#5C6470`. **É o "highlight abaixo do título" que custa DAX + formatação condicional** — só inclua se o cliente escolher (ver §Regras de uso do kit). Sem opt-in, fique só no título descritivo estático.

```svg
<text x="24" y="32" font-size="15" font-weight="600" fill="#33394C">Faturamento mensal · R$ milhões</text>
<text x="24" y="50" font-size="12" fill="{{COR_ACAO}}">2025 acelerou e superou a meta</text>  <!-- insight; cor condicional -->
```

> **No PBIX:** o título descritivo é estático (fácil). O **subtítulo de insight + cor condicional** exige uma **medida DAX** (texto do insight) e **formatação condicional** da cor — é o item mais custoso; registre no racional e ofereça como **upgrade opcional** ao cliente. No mockup, mostre-o já colorido para alinhar a expectativa.

### Doutrina de cor (ordem de prioridade — aplique nesta ordem)

A cor tem **4 papéis e nenhum a mais**. Se um elemento não se encaixa nos papéis 2–4, ele é **neutro**. Esta é a resposta para "qual o padrão de escolha de cor".

1. **Neutro = contexto (padrão).** Todo dado que é só referência fica cinza. (dark: barra `#39414E`, texto `#8A929E`/`#C7CCD3`; light: barra `#C9CDD4`, texto `#7C8595`.) **Fundo de card é sempre neutro.**
2. **Cor de ação = foco.** Só no item que o insight cita (líder do ranking, ponto final da linha, fatia destacada). **Um destaque por gráfico.** Também na seleção/menu ativo.
3. **Semântica = juízo de valor (bom/ruim).** Verde `bom` / vermelho `ruim`, aplicada a **variações (Δ)** e a **status vs meta/limite**. A cor vem de **direção × polaridade** (tabela), nunca do "subiu/desceu" cru. **Sempre** com seta/rótulo/ícone junto (nunca só cor — daltonismo).
4. **Categórica = distinguir séries.** Só quando há de fato N categorias a separar (empilhado, donut, linhas múltiplas, legenda). Paleta fixa, na ordem dos tokens.

**Direção × polaridade (cor do Δ):** o que decide é se o movimento é **bom ou ruim para o negócio**, não a direção da seta.

| Polaridade do indicador | ▲ aumentou | ▼ diminuiu |
|---|---|---|
| **Positiva** — mais é melhor (receita, headcount, promoções, eNPS, saldo, diversidade %, atingimento) | **verde** (bom) | **vermelho** (ruim) |
| **Negativa** — menos é melhor (turnover, absenteísmo, custo, despesa, desligamentos, dias perdidos, horas extras, tempo até saída) | **vermelho** (ruim) | **verde** (bom) |
| **Neutra / sem meta / descritivo** | **cinza** | **cinza** |

> Ex.: turnover ▼ + polaridade negativa = **verde**. Custo de folha ▲ + polaridade negativa = **vermelho**. Headcount ▲ + positiva = **verde**. Não pinte todo "▲" de verde.

**Destaque de barra por status vs meta** (turnover/absenteísmo por área): o lado ruim do limite recebe a semântica **ruim (vermelho)**, o resto neutro, com **linha de meta + legenda**. Não use a cor de ação para "ruim", nem o vermelho para "foco".

**Laranja `#E0A458`** é exceção rara: só "atenção/oportunidade **sem** veredito bom-ruim" (zona de observação, "sem compra = oportunidade") e **sempre com legenda**. Na dúvida entre laranja e vermelho/ação, **não use laranja**.

### Regra de cor do insight ↔ destaque do gráfico (inviolável)

A cor do texto do insight **não é escolhida ao acaso**: ela é **a mesma cor da marca que está destacada no gráfico** — assim o olho liga a frase ao dado. E o destaque do gráfico **sempre marca o item de que o insight fala** (nunca um destaque "solto" sem significado).

- **Cor de ação `{{COR_ACAO}}` = "em foco / líder / favorável".** Destaca **exatamente o item citado no insight** (a barra líder, o ponto final da linha, a fatia maior). O **texto do insight** usa essa mesma cor. Resto do gráfico em cinza neutro.
- **Laranja semântico `#E0A458` = "atenção / oportunidade".** Só pode aparecer quando há **algo que o explique na própria tela**: uma **legenda** (ex.: status de meta acima/próximo/abaixo), **células coloridas** numa tabela (com nota "laranja = atenção"), ou um **rótulo** explícito ("sem compra = oportunidade"). Aí o texto do insight também é laranja, casando com as marcas laranja.
- **Proibido:** destacar uma barra na cor de ação e escrever o insight em laranja (ou vice-versa) — cores divergentes confundem. Destaque e texto do insight **sempre na mesma cor**, e essa cor **sempre tem significado explicado** (foco/legenda/rótulo).
- Verde (cor de ação) e laranja são as **únicas** cores de significado; o resto é cinza de contexto. Não introduza uma 3ª cor de destaque sem legenda.

## Legenda — sempre no topo-esquerda (inviolável)

A legenda (séries de cor, status vs meta, "atenção", linha de meta) fica **no canto superior-esquerdo da área do visual**, logo **abaixo do título/insight** e **acima do gráfico**, na horizontal. **Nunca** no canto direito, embaixo, ou solta no meio. Motivo: a leitura é F/Z (começa no topo-esquerda) — a legenda precisa ser lida **antes** do gráfico, alinhada com título e insight numa só coluna de leitura.

- Posição dentro do card: `x ≈ 20`, `y ≈ 62–70` (logo abaixo do insight em y≈50), itens lado a lado (quadradinho 9–10px + rótulo), gutter ~14–18px.
- O quadradinho usa a MESMA cor das marcas no gráfico (verde/vermelho/ação/categórica). A linha de meta também se explica aqui (tracejado + "meta").
- No PBIX: **Formato → Legenda → Posição: Superior, à esquerda**. Registre no racional.

```svg
<!-- legenda no topo-esquerda do card (abaixo do insight, acima do gráfico) -->
<g transform="translate(20,62)" font-size="10">
  <rect x="0"  y="0" width="9" height="9" fill="{{COR_ACAO}}"/><text x="13" y="8" fill="#5C6470">Em foco</text>
  <rect x="84" y="0" width="9" height="9" fill="#39414E"/><text x="97" y="8" fill="#5C6470">Demais</text>
</g>
```

## Template do canvas

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" font-family="'Segoe UI',system-ui,Inter,sans-serif">
  <rect width="1280" height="720" fill="#F5F7FB"/>
  <!-- faixa de título -->
  <text x="32" y="44" font-size="26" font-weight="600" fill="#33394C">Título da página = o ponto/pergunta da tela</text>
  <!-- DOIS carimbos de data, sob o título (NÃO no rodapé) -->
  <text x="32" y="64" font-size="13" fill="#5C6470">Dados: <tspan font-weight="600" fill="#33394C">mar/2025 (último fech.)</tspan> · atualizado em 12/04</text>
  <!-- seletor de período discreto, à direita (sem range início/fim aberto) -->
  <g transform="translate(940,30)" font-size="12">
    <rect x="0" y="0" width="92" height="26" rx="6" fill="#FFFFFF" stroke="#E6E8EC"/>
    <text x="12" y="17" fill="#5C6470">Mês: Mar ▾</text>
    <rect x="100" y="0" width="60" height="26" rx="13" fill="{{COR_ACAO}}" fill-opacity="0.12"/>
    <text x="112" y="17" fill="{{COR_ACAO}}">12 meses</text>   <!-- botão de período ativo (pílula) -->
    <rect x="168" y="0" width="60" height="26" rx="13" fill="#FFFFFF" stroke="#E6E8EC"/>
    <text x="180" y="17" fill="#7C8595">Acum.</text>
  </g>
  <!-- ... KPIs e visuais aqui ... -->
  <!-- rodapé: só fonte + selo (a data subiu pro título) -->
  <text x="32" y="704" font-size="11" fill="#7C8595">Fonte: ...</text>
  <text x="1248" y="704" text-anchor="end" font-size="11" fill="#C9CDD4">MOCKUP — dados ilustrativos</text>
</svg>
```

## Posicionamento calculado pela grid (12 colunas — OBRIGATÓRIO)

Antes de emitir qualquer `<rect>`/`<g>` de card ou visual, defina a grid da tela e **derive toda geometria dela** — nunca informe `x`/`width` avulsos por card (regra inviolável 31; ver `layout-dashboard.md` §Grid estrutural rígida).

```
contentX     = margem_esquerda (ou menu + gutter, quando há trilho)
contentWidth = contentX_direita - contentX      (margem externa 24 dos dois lados)
columns      = 12
gutter       = 20
columnWidth  = (contentWidth - 11 * gutter) / 12

x(coluna)    = contentX + coluna * (columnWidth + gutter)
width(span)  = span * columnWidth + (span - 1) * gutter
```

`coluna` é base-zero: 1º bloco na coluna `0`; depois de um `span 4`, o próximo começa na coluna `4`; depois de um `span 8`, na coluna `8`.

**Fluxo:** primeiro monte a tabela de blocos `id | linha | coluna_inicial | span | y | altura` e só então gere os SVGs, calculando `x`/`width` pela fórmula. Blocos de linhas diferentes com a mesma `coluna_inicial`/`span` caem **exatamente** no mesmo eixo (é isso que faz `8+4` alinhar com `4+4+4`).

Exemplo (trilho 72, margem dir. 24 → contentX=92, contentWidth=1164, columnWidth≈78,67):
- KPIs `4+4+4`: col 0/4/8 → x 92 / 486,67 / 881,33 · w 374,67
- Principal+apoio `8+4`: col 0/8 → x 92 (w 769,33) / 881,33 (w 374,67) — o apoio cai no MESMO eixo do 3º KPI.
- `y`/altura pela escala de 8px, gutter vertical constante (24 entre grupos).

## Seletor de período + carimbos de data

A data é a funcionalidade nº 1 (ver `layout-dashboard.md` §Seleção de data). Desenhe-a como **pílulas discretas**, nunca dois date-pickers de range aberto.

- **Seleção:** uma pílula de **mês** *ou* **ano** + **botões de período** ("12 meses", "Acum.", "6 meses"). O período ativo é a pílula na cor de ação a 12% (mesma linguagem do KPI/menu ativo).
- **Seleção destacada, não branco-no-branco:** o mês/ano selecionado tem **fundo destacado** (pílula colorida), pra o olho achar "de quando é o dado" sem pensar. Demais filtros neutros.
- **Posição à esquerda + ordem mês-ano (BR):** o filtro de data vem **antes** dos outros (à esquerda), e o rótulo é "Mai/2026" (mês-ano), nunca "2026/05" (ano-mês é leitura de modelo, não de negócio).
- **Gestão à vista / TV:** **sem seletor** — só um rótulo "Dados de {data dinâmica}". A tela mostra sempre o último fechamento / D-1 / última operação real.
- **Dois carimbos, sob o título:** `Dados: {referência}` (período que os dados representam, em destaque) + `atualizado em {dd/mm}`. Nunca no rodapé — sem data de referência o usuário lê o número errado.

```svg
<!-- carimbos de data (reutilizável) -->
<text x="32" y="64" font-size="13" fill="#5C6470">Dados: <tspan font-weight="600" fill="#33394C">{referência}</tspan> · atualizado em {dd/mm}</text>
```

## Barra de filtros (N filtros + "Limpar")

O dashboard **pode ter mais de 2 filtros** — não force só 2. A barra de filtros fica na faixa de título (à direita) ou numa fina linha sob o título. Ordem: **data primeiro** (pílula destacada), depois os demais slicers, todos discretos (cinza). Regras:

> ⚠️ **A barra de filtros NÃO pode encostar/sobrepor o título.** Os dois dividem a faixa y24..84. Calcule onde o título termina (~0,55×font-size por caractere a partir de x96) e ancore a barra **depois disso, com ≥20px de folga** — o `translate(X,28)` do grupo de filtros tem de ser maior que `fim_do_título + 20`. Não cabe? Encurte o título (ele deve só **localizar** a tela — ver `layout-dashboard.md` §Princípios) ou mova a barra para uma linha própria. Título longo + filtros na mesma linha = sobreposição (erro comum).

- **A data lidera e é destacada** (pílula na cor de ação ~12%). Os outros filtros são pílulas neutras (`#FFFFFF` + borda `#E6E8EC`, texto `#5C6470`/`#7C8595`).
- **Pílula de filtro:** altura 26, rx 6, com `▾`; `rx 13` (formato cápsula) só nos botões de período.
- **Mais de 4 filtros → adicione "Limpar filtros"** (botão fantasma, à direita do grupo) e, se não couber tudo na faixa do título, mova a barra para uma **linha própria** logo abaixo do título (y ~92, antes dos KPIs — respeitando o gutter). Muitos slicers soltos no corpo é anti-padrão (0-clique): prefira a barra no topo ou um overlay ☰ (ver `layout-dashboard.md` §Menu overlay).
- No PBIX isso vira **segmentações** + um **botão "Limpar todos os filtros"** (Ação → Limpar todos os filtros / marcador). Registre no racional.

```svg
<!-- barra de filtros: data (destacada) + 4 slicers + Limpar. Pílulas de 26px, gutter ~8px entre elas. -->
<g transform="translate(560,30)" font-size="12">
  <!-- data lidera, destacada -->
  <rect x="0"   y="0" width="96"  height="26" rx="13" fill="{{COR_ACAO}}" fill-opacity="0.12"/>
  <text x="14"  y="17" fill="{{COR_ACAO}}" font-weight="600">Mai/2026</text>
  <!-- demais filtros (neutros) -->
  <rect x="104" y="0" width="120" height="26" rx="6" fill="#FFFFFF" stroke="#E6E8EC"/><text x="116" y="17" fill="#5C6470">Regional ▾</text>
  <rect x="232" y="0" width="112" height="26" rx="6" fill="#FFFFFF" stroke="#E6E8EC"/><text x="244" y="17" fill="#5C6470">Canal ▾</text>
  <rect x="352" y="0" width="120" height="26" rx="6" fill="#FFFFFF" stroke="#E6E8EC"/><text x="364" y="17" fill="#5C6470">Categoria ▾</text>
  <rect x="480" y="0" width="112" height="26" rx="6" fill="#FFFFFF" stroke="#E6E8EC"/><text x="492" y="17" fill="#5C6470">Vendedor ▾</text>
  <!-- >4 filtros → botão Limpar (fantasma) -->
  <text x="608" y="17" fill="{{COR_ACAO}}" font-weight="600">✕ Limpar</text>
</g>
```

## Canvas por ambiente

O canvas padrão é desktop (1280×720). Outros ambientes (ver `layout-dashboard.md` §Ambiente) usam viewBox próprio — **não** encolha o desktop:

- **Mobile (dedicado):** `viewBox="0 0 390 844"` (retrato). 1 coluna, KPIs empilhados, ≤3–4 visuais, alvos de toque ≥44px. Refaça a disposição, não reaproveite o grid de desktop.
- **TV / gestão à vista:** `viewBox="0 0 1280 720"` (ou 16:9 da tela), fontes maiores, **sem** seletor/slicer, data dinâmica.
- **Painel de situação:** viewBox no formato da sala (pode ser ultra-wide, ex.: `0 0 2560 720`); cada visual legível à distância.

Quando o mesmo conteúdo tem mais de um ambiente, gere **artes separadas** (`tela-NN-{slug}.svg` e `tela-NN-{slug}-mobile.svg`) e registre no racional que são layouts distintos do mesmo conteúdo.

## KPI card (ícone em box + hierarquia de texto + mini-bullet)

```svg
<g transform="translate(32,84)">
  <rect width="234" height="96" rx="10" fill="#FFFFFF" stroke="#E6E8EC"/>
  <!-- ícone em box de fundo claro do MESMO matiz da ação (Numerro: não ampliar ícone pequeno; preencher com box claro) -->
  <rect x="16" y="20" width="40" height="40" rx="9" fill="{{COR_ACAO}}" fill-opacity="0.12"/>
  <text x="36" y="46" text-anchor="middle" font-size="18" fill="{{COR_ACAO}}">$</text>  <!-- ícone (≈18–20px, NÃO esticar) -->
  <!-- hierarquia: número grande+forte ACIMA; rótulo pequeno, espaçado e claro ABAIXO (Numerro) -->
  <text x="72" y="50" font-size="34" font-weight="700" fill="#33394C">R$ 4,2M</text>
  <text x="72" y="68" font-size="11" letter-spacing="1.4" fill="#7C8595">RECEITA (TRI)</text>
  <!-- mini-bullet: faixa cinza (meta) + barra de valor + alvo -->
  <rect x="72" y="78" width="146" height="7" rx="0" fill="#EDEFF2"/>
  <rect x="72" y="78" width="116" height="7" rx="0" fill="{{COR_ACAO}}"/>
  <rect x="196" y="75" width="2" height="13" fill="#6B7280"/>  <!-- alvo -->
</g>
```
Repita transladando +250px em X para os próximos cards. Mais importante à esquerda. **Ícone:** cor de ação sobre box do mesmo matiz a ~12% de opacidade; nunca ampliar um ícone pequeno — aumente o box, não o traço.

**Regras do card de KPI (do feedback real):**
- **Unidade sempre no número:** "47,2 dias", "R$ 5,3M", "7%" — nunca um número solto que o usuário tem que adivinhar a unidade.
- **% além do absoluto:** quando o valor faz mais sentido relativo (savings, atingimento), mostre o **percentual** (ex.: economia de R$ 359k = **7%** do spend), não só o absoluto. A variação relativa costuma decidir mais que o número bruto.
- **Diga bom ou ruim:** o card precisa sinalizar se o número é bom/ruim — via comparação (Δ vs período/meta, com **direção clara**: a seta ↑ é boa ou ruim aqui?) e/ou um **sparkline** ao lado (tendência flat/sobe/desce). Card sem isso ("47 dias" sozinho) não decide nada.
- **Fundo do card é neutro.** **Não** pinte um fundo de cor diferente por card "porque fica bonito": cor sem significado polui e **mata o destaque semântico** (o vermelho/verde de alerta some sobre um fundo azul). Cor no card só pra codificar status (com legenda) ou seleção. O destaque é o **número/seta**, não o fundo.
- **Nada ao LADO do mini-bullet.** O mini-bullet ocupa a **largura útil do card** (`x=20` até `card_w−20`); a meta é uma marca **sobre** o bullet, e o texto de contexto (`102% da meta`, `▲ 3,9%`) vai em **linha própria** (abaixo do bullet, `y≈87` num card de 92px), **nunca** num `x` à direita do bullet — é o erro que estoura a borda. Num card-padrão (275×92) cabem 3 linhas: número (y38) · rótulo caps (y56) · contexto **ou** bullet+contexto (bullet y66, contexto y87). Não empilhe bullet **e** seta **e** texto lateral.

## Número grande isolado (KPI puro)

```svg
<g transform="translate(32,120)">
  <text x="0" y="0" font-size="64" font-weight="700" fill="{{COR_ACAO}}">9 em 10</text>
  <text x="0" y="34" font-size="18" fill="#5C6470">consumidores preferem nosso produto</text>
</g>
```

## Barra ordenada (1 destacada) — comprimento, começa em 0

```svg
<g transform="translate(32,210)">
  <text x="0" y="0" font-size="15" font-weight="600" fill="#33394C">Receita por regional</text>
  <!-- cada barra: y cresce 38px; largura ∝ valor; ordene maior→menor -->
  <g transform="translate(0,24)">
    <text x="0" y="14" font-size="13" fill="#5C6470" text-anchor="end" transform="translate(90,0)">Sudeste</text>
    <rect x="100" y="2" width="420" height="20" rx="0" fill="{{COR_ACAO}}"/>
    <text x="528" y="17" font-size="12" fill="#33394C">R$ 1,8M</text>
  </g>
  <g transform="translate(0,62)">
    <text x="90" y="14" font-size="13" fill="#5C6470" text-anchor="end">Sul</text>
    <rect x="100" y="2" width="300" height="20" rx="0" fill="#C9CDD4"/>
    <text x="408" y="17" font-size="12" fill="#5C6470">R$ 1,3M</text>
  </g>
  <!-- demais barras em #C9CDD4; só a da história em {{COR_ACAO}} -->
</g>
```
> Barra horizontal quando rótulos longos / >7 categorias. Sem gridline vertical pesada. Sem eixo truncado. **Barra "gorda": espessura ≈2× o vão entre barras** (não barras finas com vãos largos). **Valor logo após a ponta.** Ao colorir por categoria num mesmo gráfico, **≤4 cores**; intensidades da mesma matiz **ordenadas** (sem zebra).

> **FIDELIDADE — cantos retos nas marcas de dado.** No Power BI nativo, **barras, colunas, bullets, células de matriz, data-bars e tiles de treemap NÃO têm canto arredondado** (`rx="0"`). O template de referência não tem nenhuma config de `cornerRadius`/`roundEdges`. Só o **container do card/visual** tem canto arredondado (`rx≈8–12`; o export do PBI mostra ~10). Regra prática: `rx` só em `rect` que é *moldura de card/visual* (e pílulas de slicer/chrome); toda marca que representa dado fica reta.

## Linha com marcadores (tendência)

```svg
<g transform="translate(660,210)">
  <text x="0" y="0" font-size="15" font-weight="600" fill="#33394C">Receita mensal — ano atual</text>
  <!-- grid leve -->
  <line x1="0" y1="150" x2="560" y2="150" stroke="#EDEFF2"/>
  <line x1="0" y1="100" x2="560" y2="100" stroke="#EDEFF2"/>
  <line x1="0" y1="50"  x2="560" y2="50"  stroke="#EDEFF2"/>
  <!-- série: polyline + círculos nos pontos medidos -->
  <polyline fill="none" stroke="{{COR_ACAO}}" stroke-width="2.5"
            points="20,140 110,120 200,128 290,90 380,70 470,60 540,40"/>
  <circle cx="540" cy="40" r="4" fill="{{COR_ACAO}}"/>
  <text x="20" y="170" font-size="12" fill="#7C8595">Jan</text>
  <text x="540" y="170" font-size="12" fill="#7C8595" text-anchor="end">Jul</text>
</g>
```
Eixo Y de linha PODE ser truncado (revelar variação pequena) — registre no racional. Máx. 4–5 linhas; senão small multiples.

## Vs. meta — barra de % + linha constante em 100% (NATIVO)

Para "atingimento por categoria/vendedor", o bullet graph **não é nativo** no Power BI. Use o equivalente **100% nativo**: **barra de % de atingimento** (começa em 0), **formatação condicional** da cor por status, e uma **linha constante em 100%** (painel Análise → Linha Constante). Substitui gauge **e** bullet.

```svg
<g transform="translate(32,90)" font-size="13">
  <!-- linha constante de meta (100%) — nativa: painel Análise -->
  <rect x="231" y="-4" width="2" height="220" fill="#33394C"/>
  <text x="232" y="-10" text-anchor="middle" font-size="10" fill="#33394C">meta 100%</text>
  <!-- por item: rótulo + barra (largura ∝ %, começa em 0) + cor por status + % -->
  <text x="-12" y="14" text-anchor="end" fill="#33394C">Ana Souza</text>
  <rect x="0" y="2" width="272" height="16" fill="{{COR_ACAO}}"/>      <!-- ≥100% = cor de ação -->
  <text x="284" y="14" font-size="12" font-weight="600" fill="{{COR_ACAO}}">118%</text>
  <text x="-12" y="46" text-anchor="end" fill="#5C6470">Diego Alves</text>
  <rect x="0" y="34" width="224" height="16" fill="#E0A458"/>          <!-- 90–100% = próximo -->
  <text x="284" y="46" font-size="12" fill="#5C6470">97%</text>
  <text x="-12" y="78" text-anchor="end" fill="#5C6470">Gustavo Pó</text>
  <rect x="0" y="66" width="141" height="16" fill="#C9CDD4"/>          <!-- <90% = abaixo -->
  <text x="284" y="78" font-size="12" fill="#5C6470">61%</text>
</g>
```
Cor por status (formatação condicional, com **legenda** na tela): acima `{{COR_ACAO}}` · próximo `#E0A458` · abaixo `#C9CDD4`. Escala 0→~130% (100% na linha constante). Barra começa em 0 (regra inviolável). Tudo nativo: barra + linha constante + formatação condicional.

## Slopegraph (comparar 2 grupos em N variáveis)

```svg
<g transform="translate(32,230)" font-size="12">
  <text x="0" y="-10" font-size="15" font-weight="600" fill="#33394C">Pais esperam mais que os próprios alunos</text>
  <line x1="120" y1="0" x2="120" y2="180" stroke="#EDEFF2"/>
  <line x1="320" y1="0" x2="320" y2="180" stroke="#EDEFF2"/>
  <text x="120" y="-2" fill="#7C8595">Pais</text>
  <text x="320" y="-2" fill="#7C8595" text-anchor="end">Alunos</text>
  <!-- linha de destaque (a que cai): cor de ação -->
  <line x1="120" y1="30" x2="320" y2="120" stroke="{{COR_ACAO}}" stroke-width="2.5"/>
  <circle cx="120" cy="30" r="4" fill="{{COR_ACAO}}"/><circle cx="320" cy="120" r="4" fill="{{COR_ACAO}}"/>
  <text x="112" y="34" text-anchor="end" fill="#33394C">Faculdade 88%</text>
  <text x="328" y="124" fill="#33394C">61%</text>
  <!-- demais linhas em cinza -->
  <line x1="120" y1="70" x2="320" y2="55" stroke="#C9CDD4" stroke-width="2"/>
  <circle cx="120" cy="70" r="3.5" fill="#C9CDD4"/><circle cx="320" cy="55" r="3.5" fill="#C9CDD4"/>
</g>
```

## Donut de 1 fatia destacada (reforçar 1 número)

```svg
<g transform="translate(140,360)">
  <circle r="70" fill="none" stroke="#EDEFF2" stroke-width="22"/>
  <!-- arco destacado: stroke-dasharray = [parte, resto] da circunferência (2πr≈440) -->
  <circle r="70" fill="none" stroke="{{COR_ACAO}}" stroke-width="22"
          stroke-dasharray="119 321" transform="rotate(-90)"/>
  <text y="-2" text-anchor="middle" font-size="34" font-weight="600" fill="#33394C">27%</text>
  <text y="22" text-anchor="middle" font-size="12" fill="#5C6470">sem consulta</text>
</g>
```
Use só para destacar UMA fatia. Pizza completa: só ≤3–4 fatias, maior às 12h, horário.

## Lollipop (ranking leve)

```svg
<g transform="translate(60,420)" font-size="13">
  <!-- por item: linha fina até o valor + círculo na ponta -->
  <line x1="120" y1="10" x2="320" y2="10" stroke="#C9CDD4" stroke-width="2"/>
  <circle cx="320" cy="10" r="7" fill="{{COR_ACAO}}"/>
  <text x="110" y="14" text-anchor="end" fill="#5C6470">Produto A</text>
  <text x="320" y="14" text-anchor="middle" font-size="10" fill="#fff">42</text>
</g>
```

## Scatterplot (correlação)

```svg
<g transform="translate(700,420)">
  <line x1="0" y1="160" x2="320" y2="160" stroke="#7C8595"/>   <!-- eixo X -->
  <line x1="0" y1="0"   x2="0"   y2="160" stroke="#7C8595"/>   <!-- eixo Y -->
  <line x1="10" y1="150" x2="310" y2="30" stroke="#C9CDD4" stroke-dasharray="4 4"/> <!-- tendência -->
  <circle cx="40" cy="130" r="5" fill="#C9CDD4"/>
  <circle cx="120" cy="95" r="5" fill="#C9CDD4"/>
  <circle cx="250" cy="55" r="5" fill="{{COR_ACAO}}"/>          <!-- ponto de interesse -->
  <text x="262" y="50" font-size="11" fill="#33394C">outlier</text>
</g>
```

## Sparkline (dentro de card/tabela)

```svg
<polyline fill="none" stroke="{{COR_ACAO}}" stroke-width="1.8"
          points="0,18 12,14 24,16 36,8 48,11 60,4"/>
<circle cx="60" cy="4" r="2.2" fill="{{COR_ACAO}}"/>
```

## Barra empilhada divergente (Likert)

Negativos crescem à esquerda de um eixo central; positivos à direita; neutro no meio. Cor divergente (2 tons opostos), intensidade = força. Uma linha por pergunta, alinhadas no centro. Rotule só os extremos.

```svg
<g transform="translate(360,40)" font-size="12">
  <line x1="0" y1="0" x2="0" y2="120" stroke="#C9CDD4"/>      <!-- eixo central -->
  <!-- pergunta 1 -->
  <text x="-12" y="22" text-anchor="end" fill="#5C6470">Pergunta 1</text>
  <rect x="-110" y="10" width="110" height="18" fill="#D64545" opacity="0.55"/>  <!-- discordo -->
  <rect x="0" y="10" width="160" height="18" fill="{{COR_ACAO}}"/>               <!-- concordo -->
</g>
```

## Tabela com pontos-indicadores (status vs. meta)

```svg
<g transform="translate(32,300)" font-size="13" fill="#33394C">
  <text x="0" y="0" font-size="15" font-weight="600">Indicadores vs. meta</text>
  <line x1="0" y1="14" x2="360" y2="14" stroke="#E6E8EC"/>
  <text x="0" y="36">Indicador A</text>
  <circle cx="340" cy="32" r="6" fill="{{COR_ACAO}}"/>      <!-- só acende quando precisa de atenção -->
  <text x="0" y="62">Indicador B</text>
  <!-- sem ponto = ok; use intensidade de UM tom para níveis, não vermelho/verde -->
</g>
```

## Mapa / Sankey (placeholders)

Para `geografico` e `fluxo`, gere um placeholder de forma reconhecível (silhueta do mapa do cliente com regiões em intensidade de 1 tom; ou bandas Sankey de largura proporcional) e anote no racional que o detalhamento sai no PBIX. Não fabrique precisão geográfica falsa.

**Regras do placeholder de mapa (coroplético em tiles) — para não sair sem sentido nem vazar:**
- **Tiles do MESMO tamanho.** O tamanho do tile **não** codifica nada — quem codifica é a **intensidade da cor**. Tiles de tamanhos diferentes (como uma barra "Sul" fininha ao lado de blocos grandes) confundem: o olho lê tamanho como valor.
- **Intensidade monotônica = valor.** `fill-opacity` cresce junto com a métrica (maior receita = mais saturado). Use uma rampa simples (ex.: `0,30 + 0,70 × valor/valor_máx`); o maior fica sólido (`1.0`) e ganha **texto branco**, os demais texto escuro `#33394C`/`#5C6470`. Sem inversões (uma região menor não pode ficar mais escura).
- **Tudo dentro do card** (ver §Regras de uso do kit): some `tileY+tileH` da última fileira e garanta `≤ card_h − 12`; idem na largura. Layout geográfico aproximado (N/NE em cima, CO/SE no meio, S embaixo) é suficiente — não precisa de silhueta fiel.
- **Cada tile traz nome + valor** (2 linhas, centralizadas). Anote num canto "esquema ilustrativo — mapa real no PBIX".
- Alternativa quando o espaço é baixo/largo demais para tiles legíveis: caia para **barra ordenada de receita por região** e registre no racional (o mapa fiel entra no PBIX). Não force tiles ilegíveis.

## Hierarquia de texto (Numerro · Working with Text)

- **Valor > rótulo.** O número é mais importante que a descrição: número **grande + bold**; rótulo **pequeno, mais claro, com letter-spacing**, posicionado **abaixo** do número.
- **Título de visual = nome descritivo** (sentence-case semibold); **subtítulo = insight** (o takeaway) com **cor condicional** (bom = cor de ação; atenção = laranja; neutro = `#5C6470`). Ver §Títulos de visual. O subtítulo conta o que o visual revela, não só repete a medida.
- **Sem gritar:** caps só em rótulos curtos de KPI (com letter-spacing). **Nunca** caps em título de visual nem em frase/parágrafo — cansa e soa como grito. Diferencie hierarquia por tamanho/peso/espaçamento, não por CAPS.
- **CTA sutil:** "ver mais", "scroll for more" etc. em cinza claro, caps espaçado, pequeno — não rouba atenção do dado.
- **Título sempre maior que o corpo.** O título do visual é uns 2pt maior que o texto do gráfico — hierarquia se faz por **tamanho/peso/espaçamento**, nunca encolhendo o dado a ponto de ilegível. Mínimo legível: não desça o texto de dado/eixo abaixo do tamanho do kit (12–13px); título de visual ≥15px.
- **Ênfase só com peso ou itálico** — **nunca sublinhado** (parece link) nem caps em frase. Evite **hifenizar** rótulo/título.
- **Não rotacione texto**, em especial rótulo de eixo: texto girado custa leitura. Rótulo de categoria longo → use **barra horizontal**, não coluna com rótulo vertical.
- **Teste de legibilidade:** imagine o visual reduzido ao mínimo — o texto-chave (número, rótulo, título) ainda se lê? Se não, está pequeno/denso demais.

## Cor acessível (Numerro · daltonismo)

- Para **2 categorias** ou **escala sequencial**, prefira **o mesmo matiz com lightness diferente** (ex.: HSL 346,86%,55% vs 346,86%,73%) em vez de dois matizes distintos (azul×verde confundem daltônicos).
- Para categóricas independentes (3+), matizes distintos + diferença de luminância; teste em escala de cinza.
- **Teste de escala de cinza (inviolável).** Antes de fechar, imagine o visual em P&B: se a informação se perde (séries viram o mesmo cinza, destaque some, status bom/ruim some), ele falha para ~10% dos homens (daltonismo). Conserte separando por **posição/rótulo/símbolo/intensidade** — cor é reforço, nunca o único canal. Mesma cor = mesmo grupo em **toda a tela e em todas as telas do projeto** (consistência); entre dois visuais, só o dado muda, a construção e a codificação de cor permanecem.

## Regras de uso do kit

- **NADA ultrapassa a moldura do card (inviolável).** Todo `<text>`/`<rect>`/`<path>` dentro de um `<g id="visual-…">` ou `<g id="kpi-…">` tem de caber na moldura daquele card. Antes de fechar cada card, **cheque os limites contra a largura/altura dele**: para texto, `x + largura_estimada_do_texto ≤ card_w − 12` (estime ~0,55×font-size por caractere; `text-anchor="end"` ancora à direita, então respeite a borda esquerda); para qualquer forma, `x+w ≤ card_w` e `y+h ≤ card_h`. Conteúdo que toca a borda do canvas ou vaza para o card vizinho é erro. Quando um conjunto não cabe, **reduza o número de itens / a fonte / reposicione** — não deixe vazar. Erros típicos: texto de contexto largo no canto direito de um KPI; placeholder de mapa/treemap mais alto que o card; última barra de um ranking sem espaço pro rótulo de valor.
- **Cor segue a §Doutrina de cor** (neutro → ação/foco → semântica bom-ruim por direção×polaridade → categórica). Cor de ação só no item que o insight cita; resto em `#C9CDD4`/`#7C8595`. Δ verde/vermelho pela **polaridade do indicador**, não pela seta. Laranja só com legenda.
- **Legenda sempre no topo-esquerda** (ver §Legenda). Nunca à direita/embaixo.
- **Todo gráfico tem que ser legível:** ou **rótulos de dado** (valor em cada marca) **ou eixo de valor** — **nunca os dois ausentes**. E **sempre** rótulo de **categoria** (quem é cada barra/coluna/fatia) e do **eixo de tempo** (meses). Coluna/linha sem rótulo nem eixo nem categoria não comunica nada — é o erro mais comum. Regra prática: poucas marcas → rótulo de dado (mais limpo); muitas marcas → eixo de valor + grid leve. Pelo menos um dos dois, sempre.
- **Recursos de cor condicional são OPCIONAIS (opt-in do cliente), porque custam DAX + formatação condicional:** (a) **destaque do top-1/ofensor por cor** e (b) **subtítulo de insight dinâmico colorido** (o "highlight" abaixo do título). São lindos, mas caros de manter no PBIX. **Pergunte ao cliente** se quer; se não, entregue **tudo neutro + título descritivo estático** (a cor de ação fixa num item-chave continua barata e permitida). Registre a escolha no racional. No mockup, renderize conforme a escolha — não imponha o conditional por padrão.
- **Os esqueletos NÃO são presos ao tema.** Qualquer `canvas-*` serve para claro **ou** escuro — é só **recolorir pelos tokens** (troque bg/card/ink/border/grid do bloco de tokens claro↔escuro e mantenha a cor de ação). Os 2 esqueletos "dark" são só atalhos já recoloridos; para dark, parta do layout que melhor conta a história e aplique os tokens escuros (e vice-versa). Não limite a escolha de layout por causa do tema.
- **Sempre** título de visual (nome descritivo). Barra começa em 0. Sem 3D, sem gauge, sem gridline pesada.
- **Só visuais nativos do Power BI por padrão** (status ✅ em `pbi-visuals.md`). Não desenhe bullet/lollipop/dumbbell/**pirâmide populacional espelhada**/sankey etc. a menos que o usuário **opte explicitamente** pelo 🔧/🧩 — caso contrário use o equivalente nativo (ver `chart-chooser.md`). Pirâmide etária → **barra/coluna agrupada** (faixa etária no eixo, sexo na legenda).
- Rótulos amigáveis (não snake_case).
- Mesma história → mesmo tipo de gráfico em toda a tela (consistência perceptiva).
- Selo "MOCKUP — dados ilustrativos" no rodapé de toda tela.
