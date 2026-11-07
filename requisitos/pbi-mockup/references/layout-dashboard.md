# Layout de tela única

Base: Few (dashboard = tela única, sem scroll/fragmentação; espaço nobre pro mais importante; sumarização; razão dado-tinta) + Kirk (composição, hierarquia) + Guia Xperiun (filtros com período atual por default; data de referência + atualização visíveis junto ao título) + **Numerro Data Re-Visualized** (hierarquia por andar, escala de visual, margens generosas, 6–10 insights/página).

## Índice

- [Canvas](#canvas)
- [Grid padrão (OBRIGATÓRIO — todos os templates seguem)](#grid-padrão-obrigatório-todos-os-templates-seguem)
- [Grid estrutural rígida (12 colunas — OBRIGATÓRIA)](#grid-estrutural-rígida-12-colunas-obrigatória)
- [Anatomia padrão da tela](#anatomia-padrão-da-tela)
- [Hierarquia por andar e escala do visual (Numerro)](#hierarquia-por-andar-e-escala-do-visual-numerro)
- [Margens e respiro (Numerro)](#margens-e-respiro-numerro)
- [Princípios aplicados](#princípios-aplicados)
- [Posição do menu de navegação (input compartilhado)](#posição-do-menu-de-navegação-input-compartilhado)
- [Um dashboard por perfil (audiência)](#um-dashboard-por-perfil-audiência)
- [Estratégia 0-clique (consumidores)](#estratégia-0-clique-consumidores)
- [Seleção de data (a funcionalidade nº 1)](#seleção-de-data-a-funcionalidade-n-1)
- [Ambiente define o layout](#ambiente-define-o-layout)
- [Faixa de KPIs](#faixa-de-kpis)
- [Checklist de layout por tela](#checklist-de-layout-por-tela)

## Canvas

- `viewBox="0 0 1280 720"` (16:9, página nativa do PBI). Tudo cabe aqui — **sem scroll, sem fragmentar** o que deveria ser visto junto.

## Grid padrão (OBRIGATÓRIO — todos os templates seguem)

Espaçamento padronizado. **Não improvise margens/calhas por tela** — use estes números em todo canvas:

- **Margem externa = 24px** em todos os lados. A área útil de conteúdo é **x: 24 → 1256** e **y: 24 → 696**.
- **Gutter (distância entre elementos internos) = 20px**, na horizontal e na vertical. É a folga mínima entre dois cards/visuais — onde os gráficos serão posicionados no PBIX.
- **Quando há trilho/sidebar de menu à esquerda:** o trilho é flush às bordas (começa em x0); o conteúdo começa em **x = largura_do_trilho + 24** e termina em **x = 1256** (a margem direita continua 24). Larguras de menu padronizadas: **trilho de ícones = 72px** · **sidebar com rótulos = 240px**.

### Zonas verticais (padrão)

| Zona | y | altura |
|---|---|---|
| Faixa de título (título + carimbos de data + filtros) | 24 → 84 | 60 |
| _gutter_ | 84 → 104 | 20 |
| Faixa de KPIs | 104 → 196 | 92 |
| _gutter_ | 196 → 216 | 20 |
| Corpo (visuais) | 216 → 672 | 456 |
| Rodapé (fonte + selo) | 672 → 696 | 24 |

- **Corpo com 2 linhas:** cada linha tem **h = 218** (216→434 e 454→672, gutter 20 no meio).
- Telas sem faixa de KPIs (ex.: grade 2×2) usam o corpo inteiro 104→672.

### Colunas (com gutter 20)

- **Sem menu** (largura útil 1232): 4 cols de **293** (x 24/337/650/963) · 3 cols de **397** (x 24/441/858) · 2 cols de **606** (x 24/650).
- **Com trilho 72** (útil 1160, x início 96): 4 cols de **275** (x 96/391/686/981).
- **Com sidebar 240** (útil 992, x início 264): 4 cols de **233** (x 264/517/770/1023).

> Sempre que um visual "não fecha" com esses x/larguras, recalcule pelo gutter de 20 — **não** encoste cards nem invente um respiro diferente. A consistência do espaçamento é o que faz o dashboard parecer profissional (e é o que o cliente percebe primeiro).

## Grid estrutural rígida (12 colunas — OBRIGATÓRIA)

Toda página é construída sobre **uma única grid modular compartilhada por todos os blocos da tela**. Não dimensione cada linha de forma independente e **não defina larguras/posições "no olho"**. (Regra inviolável 31.)

### Grid horizontal
- **12 colunas** na área útil de conteúdo. Margem externa **24px**, gutter horizontal **20px**.
- **Menu lateral fica FORA da grid** — a área útil começa após `menu + gutter`.
- Todo card/visual começa e termina em **linhas da grid** e ocupa um **número inteiro de colunas**: `2/12`, `3/12`, `4/12`, `6/12`, `8/12`, `9/12` ou `12/12`. Larguras que terminam entre duas colunas são **proibidas**.
- Blocos de linhas diferentes que representam a mesma divisão estrutural **compartilham exatamente os mesmos eixos verticais**.

Divisões válidas: 3 KPIs `4+4+4` · principal+apoio `8+4` · dois visuais `6+6` · quatro visuais `3+3+3+3` · dominante+2 apoios `8+2+2`.

**Alinhamento obrigatório:** se a linha 1 usa `4+4+4` e a linha 2 usa `8+4`, o início do bloco `4/12` da linha 2 coincide **exatamente** com o início do 3º bloco da linha 1.

### Grid vertical
- Escala-base de **8px**. Espaçamentos permitidos: `8`, `16`, `24`, `32`, `40`.
- Gutter vertical entre cards da mesma hierarquia é **constante**.
- Todos os cards da mesma linha compartilham o **mesmo `y` e a mesma altura**.
- Nada de diferenças acidentais de 2–10px entre cards, margens ou gutters.

### Checklist antes de renderizar
1. Bordas esquerdas pertencem a um conjunto pequeno de eixos compartilhados.
2. Bordas direitas terminam em linha da grid.
3. Gutters horizontais têm exatamente a mesma largura.
4. Gutters verticais têm exatamente a mesma altura.
5. Cards da mesma linha têm a mesma altura.
6. `8+4` alinha com `4+4+4`.
7. Nenhum card foi reduzido/ampliado só para acomodar conteúdo.
8. O conteúdo interno se adapta ao card; o card não quebra a grid pra se adaptar ao conteúdo.

> Espaço em branco resulta da **grid e da hierarquia**, não de coordenadas arbitrárias. Cálculo de `x`/`width` pela grid: ver `svg-kit.md` §Posicionamento calculado pela grid.

## Anatomia padrão da tela

```
┌────────────────────────────────────────────────────────────┐
│ [logo] TÍTULO-TAKEAWAY = O PONTO DA TELA       [seletor ▸]   │  ~64px  faixa de título + seletor de data
│        Dados: mar/2025 (último fech.) · atualiz. 12/04       │         dois carimbos VISÍVEIS, sob o título
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│  KPI 1   │  KPI 2   │  KPI 3   │  KPI 4   │  (mais imp. à    │  ~96px  faixa de KPIs
│ (nobre)  │          │          │          │   esquerda)      │
├──────────┴──────────┴────────┬─┴──────────┴─────────────────┤
│                              │                              │
│   VISUAL PRINCIPAL           │   VISUAL SECUNDÁRIO           │  corpo
│   (a história central)       │   (suporte/recorte)          │
│                              │                              │
├──────────────────────────────┴──────────────────────────────┤
│  Fonte: ...                                  MOCKUP — dados  │  ~28px  rodapé
└──────────────────────────────────────────────────────────────┘
```

> **Os dois carimbos de data não ficam no rodapé.** Data de **referência** (período que os dados representam) e data de **atualização** ficam **sob o título**, à vista — dashboard sem data de referência leva o usuário a ler o número errado. No rodapé sobra só a fonte + selo de mockup.

Variações (sempre 6–10 insights/visuais por página):
- **Foco único:** 1 visual grande dominante + KPIs.
- **2 colunas:** principal à esquerda, suporte à direita.
- **3+ visuais:** grade; agrupar por afinidade com **espaço em branco** (não com bordas/blocos coloridos).

## Hierarquia por andar e escala do visual (Numerro)

A leitura é de cima pra baixo. Posicione por nível de detalhe e dimensione conforme o detalhe — **nem todo visual tem o mesmo tamanho**:

- **Topo — alto nível, PEQUENO:** Card, KPI, Donut (visão geral), Filtro. Fáceis de escanear num relance. O estado atual ("o que está acontecendo agora") vive aqui.
- **Meio — CENTRAL e MAIOR = o que responde a pergunta da tela:** geralmente a **quebra/comparação que explica o desvio** (qual regional/tipo/área puxou o número) — é o que vira decisão. Barras/colunas de comparação, vs-meta, achar-o-ofensor.
- **Base — granular, GRANDE mas embaixo:** Tabela, Matriz, Scatterplot, Treemap, Mapa, Ribbon, Waterfall, Funil, Linha+Coluna, Donut (granular).

> **O gráfico evolutivo NÃO é o centro por default.** Vício comum (e que a própria Xperiun ensinou): jogar a linha/área de tendência no espaço nobre. O evolutivo é importante, mas responde só "a tendência sobe ou cai?" — não "o que está acontecendo agora" (isso são os KPIs) nem "quem causou o desvio" (isso é a quebra). Salvo quando **o ponto da tela é a própria tendência**, o evolutivo é **suporte** (menor, lateral/base), e o espaço nobre vai pro estado atual + a quebra que o explica. Se o cliente pedir o evolutivo no centro, **questione** (ver §Postura) antes de aceitar.

| Escala pequena (alto nível) | Escala grande (detalhe) |
|---|---|
| Card · KPI · Filtro · Gauge · Donut(visão) | Barras · Coluna+Linha · Área · Treemap · Mapa · Tabela · Matriz · Scatterplot · Ribbon · Waterfall · Funil |

**Não encolha visuais pra caber mais.** Espremer gera margens irregulares e aparência bagunçada. Se não cabe com folga, vira outra tela/aba.

## Margens e respiro (Numerro)

- **Padding generoso** dentro dos cards (topo/base) — o conteúdo respira e fica legível.
- **Margem entre componentes** maior — não amontoe visuais. Use o espaço do canvas a favor.
- Valores fixos em **§Grid padrão** (margem externa 24px, gutter 20px). Esses são os mínimos e o padrão; só aumente em telas executivas com poucos visuais.

## Princípios aplicados

1. **Espaço nobre = topo-esquerda e centro.** Coloque ali o KPI/visual mais importante. **Nunca** desperdice com logo gigante ou controles de navegação.
2. **Título em dois níveis.** **Página:** o título **localiza o dashboard** — qualquer um bate o olho e sabe **área + assunto** ("Compras — Análise de pedidos"), idealmente já apontando a pergunta. **Nunca** use uma tag de contexto (nome da unidade de negócio, ex.: "Abastecimento") como título: isso identifica a quem pertence, não do que trata. Subtítulo de página com contexto/medida. **Visual:** título = **nome descritivo** do gráfico (sentence-case semibold, "Faturamento mensal · R$ milhões"), e o **insight/takeaway** ("Margem caiu 9% no Sul") vai no **subtítulo do visual** com **cor condicional** (bom = cor de ação; atenção = laranja). Nunca caixa alta em título de visual. Não "Vendas".
3. **Filtros discretos.** Faixa superior à direita ou trilho esquerdo estreito, em cinza apagado. Default: período atual (regra do Guia). Filtro não compete com dado.
   - **Título não colide com a barra de filtros (faixa de título compartilhada).** Título e filtros dividem a zona y24..84. O título começa em `x≈96` (com trilho) e a barra de filtros é ancorada à direita; **o texto do título tem de terminar antes de onde a barra começa** (deixe ≥20px de folga). Orçamento prático a 24px: ~0,55×24 ≈ 13px/caractere → um título de ~45 caracteres já chega perto de x800. Por isso, **título de página = localiza a tela (área + assunto), conciso** (`"Comercial — Resultado do mês vs meta"`), **não** a pergunta longa inteira — a pergunta/“o ponto” fica no brief e no índice HTML, não precisa caber na arte. Se o título precisar ser longo, **mova a barra de filtros para uma linha própria** (e então empurre KPIs/corpo pra baixo no mesmo gutter) — nunca deixe os dois se sobreporem.
4. **Hierarquia por tamanho e posição.** O importante é maior/mais acima. Não dê peso visual igual a tudo.
5. **Agrupar com espaço em branco**, não com molduras. Borda só quando o espaço não basta, e levíssima.
6. **Razão dado-tinta alta.** Sem gridline pesada, sem fundo decorado, sem 3D, sem sombra dramática. Reduza pixels não-dados; realce os pixels-dados.
7. **Contexto em todo número.** Comparar com meta, período anterior, ou série. Um número sem referência não decide nada.
8. **Cor de ação escassa**, espalhada pela tela só onde a história pede. Use a MESMA cor pra MESMO significado em toda a tela (e evite reusar a cor de ação pra coisas diferentes).
9. **Ordem de leitura F/Z.** Posicione os visuais na sequência em que o usuário deve consumi-los pra construir o raciocínio.
10. **Datas sob o título, não no rodapé:** data de referência (em destaque) + data de atualização ficam à vista junto ao título; o rodapé fica só com fonte + selo "MOCKUP — dados ilustrativos".
11. **Coerência KPI ↔ corpo.** Os cards do topo são **os indicadores que a audiência diz serem os principais** — não um conjunto genérico. Se um gráfico do corpo é "o" indicador que o cliente mais olha (ex.: SLA num gráfico do meio), ele **merece um card no topo**: ninguém deve precisar caçar o número-chave numa barra perdida. E as **quebras do corpo devem ser do indicador-líder** (se o spend é o KPI principal, as quebras são spend por tempo/área/tipo — não de outra coisa).
12. **Não esconda o total nem o denominador.** Um dashboard de pedidos precisa do **total de pedidos**; uma taxa precisa do seu denominador visível (taxa de finalização = finalizadas ÷ total). Sem o número-base, o usuário não dimensiona o que vê.
13. **Agrupe pela mente (Gestalt).** O olho junta o que está **próximo, parecido, dentro de um mesmo container, fechado, contínuo ou conectado**. Use esses agrupamentos a favor: visuais da mesma pergunta ficam **perto** e com **tratamento igual** (mesmo tamanho de título, mesma posição de legenda); o que não se relaciona fica **longe**. Delimite com **espaço em branco**; container/borda leve só para isolar um conjunto **completamente** diferente.
14. **O layout responde por comparações significativas e desencoraja as sem sentido.** Coloque **lado a lado** o que se deve comparar (realizado × meta, este ano × ano passado); afaste o que não se compara, para o olho não cruzar dados que não se falam.
15. **Faça a conta pelo leitor.** Todo cálculo que o layout insinua (variação, % do total, saldo, margem) já vem **calculado e exibido** — o usuário não subtrai de cabeça nem cruza dois cards.
16. **Esconda o secundário; revele sob demanda.** Não despeje tudo de uma vez ("mostro porque tenho o dado"): visão geral primeiro, detalhe em **tooltip / drill / overlay**. **Todo jargão, sigla ou acrônimo** tem explicação acessível (tooltip/legenda/descrição) — não assuma que a audiência decora a sigla.

## Posição do menu de navegação (input compartilhado)

Em dashboards multipágina, reserve espaço para o menu **antes** de posicionar os visuais. Escolha vem do brief/intake:

- **Esquerda (trilho, default):** faixa vertical ~64–160px na borda esquerda. Padrão moderno p/ multipágina; libera todo o topo p/ título + KPIs. Ícone+rótulo, item ativo na cor de ação.
- **Topo:** faixa horizontal ~48px sob o título. Bom p/ poucas páginas (≤5). Come altura do corpo.
- **Nenhum:** tela única, sem navegação. Use todo o canvas.

No PBI o menu é feito com **botões + Navegador de página** (não é nativo "de fábrica"); no mockup, desenhe-o como trilho/faixa e estilize na cor neutra, item ativo na cor de ação. O tema JSON (`/corporate-pbi-tema`) estiliza `pageNavigator`/`actionButton` para casar. **Mockup e tema devem usar a MESMA posição de menu.**

**Abas com ícone + estados (Numerro):** use ícones nas abas para acessibilidade e **cor para diferenciar estado** — ativo = cor de ação; inativo = cinza. Abas espalham o conteúdo e criam fluxo lógico (≠ entupir uma tela só).

**Menu overlay (Numerro):** para desentulhar, esconda o que não é essencial num painel overlay acionado pelo ícone ☰ — slicers de baixa prioridade (acessíveis, mas fora da vista) e conteúdo textual (descrição do dashboard, suporte, info da empresa). No mockup, represente o overlay fechado (só o ☰) e, se útil, uma 2ª arte com o overlay aberto.

## Um dashboard por perfil (audiência)

A esmagadora maioria dos usuários são **consumidores**; e um projeto tem **vários perfis** com necessidades distintas. **Cada perfil ganha a sua própria tela**, sobre o mesmo modelo semântico — não um drill hierárquico que tenta servir todos.

- **Estratégico (diretor/conselho):** visão abrangente, pouco tempo, foco em resultado. Margem, comparação vs meta, tendência macro. Menos visuais, mais KPI.
- **Tático (gerente/líder):** visão de processo e do time. Desempenho por vendedor, ofensores, ranking. Já filtrado pela área dele.
- **Operacional (vendedor/PDV):** visão imediata. "Minha carteira hoje, minha meta, quem visitar." Sem análise — entrega pronta. Forte candidato a **mobile**.
- **Revenda/parceiro:** muitas vezes é **outro relatório** (não só outra aba), com camada de segurança/escopo próprio.

Indicadores que um perfil vê e outro não (ex.: **margem** o diretor vê, o vendedor não) justificam telas separadas — não esconder/mostrar na mesma tela. No mockup, **rotule cada tela com o perfil dono**.

## Estratégia 0-clique (consumidores)

Consumidor tem perfil **0-clique**: não vai montar a visão, não vai clicar em 5 filtros, não vai dar Ctrl+clique pra cruzar gráficos. Se precisar disso, ele exporta pro Excel. Então:

- A tela **já vem filtrada e aberta** no estado mais útil (período atual, escopo do perfil).
- Slicer/drill/segmentação são **exceção justificada**, não default — e ficam fora do espaço nobre.
- Aplicar segurança por perfil (RLS) **já abre** a visão certa pra pessoa — não obrigue a selecionar "o nome dela".
- Heavy users (os ~1–2% produtores) ganham interatividade em telas próprias, não na tela do consumidor.

## Seleção de data (a funcionalidade nº 1)

A data define se o número que a pessoa vê está no contexto certo. É o controle que mais quebra análise quando mal feito.

- **Nunca** range início/fim livre: dá liberdade pra comparar coisas incomparáveis (out/ano-passado→fev/ano-atual vs LY = sem sentido) e estraga a análise sazonal/comparativa.
- Use **seleção de 1 mês ou 1 ano** + **botões de período** ("últimos 12m", "acumulado do ano", "últimos 6m").
- **Posição: à esquerda.** O filtro de data é o 1º que o olho procura — coloque-o **antes** dos demais filtros (à esquerda, não jogado no canto direito). Assim, ao ler título → data, o usuário já sabe de quando são os dados.
- **Destaque a seleção ativa.** Mês/ano selecionados com **fundo destacado** (pílula na cor de ação ~12%), não tudo branco — branco-sobre-branco some e o usuário não vê de quando é o dado. Os demais filtros ficam neutros.
- **Ordem mês-ano (BR), não ano-mês.** "Mai/2026", não "2026/05". `ano-mês` é leitura técnica/de modelo; a pessoa de negócio lê mês e ano.
- **Gestão à vista / TV:** sem interação — a tela mostra sempre o **"hoje" certo** de forma **dinâmica**: último fechamento (financeiro), D-1 (vendas), ou a **última operação real** (cobre feriado/fim de semana, evita tela zerada).
- No mockup, desenhe o seletor como pílulas discretas (faixa do título), nunca dois date-pickers abertos. Componente em `svg-kit.md` §Seletor de período.

## Ambiente define o layout

O mesmo conteúdo muda de forma conforme **onde** vive. Capture o ambiente por tela e desenhe a arte certa — não confie em "responsivo automático".

| Ambiente | Canvas | Regras |
|---|---|---|
| **Desktop** (default) | 1280×720 | layout padrão deste guia |
| **Mobile (dedicado)** | ~390×844 (retrato) | 1 coluna, KPIs empilhados, poucos visuais, toque; **não** é o desktop encolhido — refaça a disposição |
| **TV / gestão à vista** | 1280×720 (ou 16:9 da tela) | zero interação, fontes grandes, data dinâmica, roda sozinho |
| **Painel de situação** | formato da sala (pode ser ultra-wide) | composição sob medida; cada visual legível à distância |

Quando um perfil usa mais de um ambiente (ex.: gerente no desktop + alerta no celular), **gere as artes separadas** e registre no racional que são layouts distintos do mesmo conteúdo.

## Faixa de KPIs

- 3–5 cards. Cada card: rótulo (caps, pequeno, cinza) + número grande + micro-contexto (vs. meta / Δ período / sparkline).
- Mais importante à esquerda. Mesma altura e baseline.
- Se o KPI tem meta, embuta um **mini-bullet** no card em vez de só uma seta.

## Checklist de layout por tela

- [ ] Cabe no canvas do ambiente (desktop 1280×720 / mobile retrato / TV) sem scroll?
- [ ] A tela é de **um perfil** (não tenta servir diretor+gerente+vendedor de uma vez)?
- [ ] **0-clique:** já vem filtrada/aberta? slicer/drill são exceção e fora do espaço nobre?
- [ ] Seleção de data sem range aberto (mês/ano + botões, ou dinâmica)?
- [ ] **Data de referência + atualização** visíveis sob o título (não só no rodapé)?
- [ ] Título é o ponto (frase), não o tema?
- [ ] O visual mais importante está no espaço nobre?
- [ ] Filtros apagados e fora do espaço nobre?
- [ ] Grupos delimitados por espaço, não por bordas pesadas?
- [ ] Visuais que se comparam estão **lado a lado**; os que não se comparam, afastados?
- [ ] Cálculo implícito (variação/%/saldo) já **calculado e exibido** (nada de conta de cabeça)?
- [ ] Jargão/sigla com explicação acessível (tooltip/legenda)?
- [ ] Cor de ação só no que a história destaca?
- [ ] Todo número tem contexto (meta/comparação) e diz **bom ou ruim**?
- [ ] Todo número tem **unidade** (dias, %, R$) — não um número solto?
- [ ] Título **localiza** a tela (área + assunto), não é uma tag de unidade?
- [ ] Os **KPIs do topo são os indicadores principais** do cliente? O indicador-chave do corpo virou card?
- [ ] As **quebras são do indicador-líder** (coerência KPI ↔ corpo)?
- [ ] **Total/denominador** presentes (total de pedidos, denominador da taxa)?
- [ ] Filtro de **data à esquerda**, seleção **destacada** (não branco-no-branco), ordem **mês-ano**?
- [ ] O **espaço nobre** responde a pergunta da tela (não foi tomado pelo evolutivo por vício)?
- [ ] 6–10 insights/visuais? (mais que isso → outra tela/aba)
- [ ] Andar certo? alto nível pequeno no topo · quebra que explica central/maior no meio · granular embaixo · evolutivo é suporte (salvo se a tela é sobre tendência)
- [ ] Visuais com folga (não encolhidos pra caber)? padding/margens generosos?
- [ ] Cor de card só com significado (sem fundo colorido decorativo que mata o destaque semântico)?
- [ ] Números arredondados onde faz sentido?
- [ ] Rodapé com fonte + selo de mockup (datas estão sob o título, não aqui)?
