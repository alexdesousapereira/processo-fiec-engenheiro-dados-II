---
name: imersao-pbi-mockup
description: 'Gera mockup visual estático em SVG (uma tela por página, canvas PBI 1280×720) de um dashboard Power BI a partir de um intake de perguntas (aceita brief do /imersao-pbi-requisitos ou escopo colado). Decide o tipo de gráfico certo para cada indicador × dimensão × história aplicando boas práticas de dataviz (Kirk, Few, Evergreen) e restringindo às possibilidades reais do Power BI (catálogo de visuais nativos + status nativo/workaround/custom). Organiza o layout de cada página (KPIs no topo, filtros discretos, título = o ponto) e renderiza em paleta neutra + cor de ação da marca do cliente. Saída: 1 SVG por tela + índice HTML navegável + racional de decisões. Roda ANTES do desenvolvimento do PBIX, para validação com o cliente. Use quando pedirem "gerar o mockup do dashboard", "desenhar as telas", "esboço visual antes de construir o Power BI".'
---

# /imersao-pbi-mockup

Transforma um **Escopo Funcional já levantado** em um **mockup visual estático em SVG** — uma tela por página do dashboard, no canvas nativo do Power BI (1280×720, 16:9). A skill **não levanta requisito**: ela traduz requisito em visual, decidindo o gráfico certo para cada história e organizando o layout de cada página com boas práticas de dataviz.

É a etapa entre o **levantamento** e o **desenvolvimento do PBIX** — o esboço/mockup validado com o cliente antes de abrir o Power BI.

**Mockup, não protótipo.** SVG é estático (mostra layout, cor e gráfico; não é clicável/navegável).

## Rodando no claude.ai (navegador)
Esta skill é **autocontida** — todos os `references/`, `templates/` e o `scripts/check_bounds.py` estão dentro da própria pasta.
- Ative em **Configurações → Capacidades**: "Execução de código e criação de arquivos" (**obrigatório** — o Passo 4.5 roda Python).
- **Templates:** ao renderizar, abra (leia) os arquivos em `templates/` desta skill e parta da geometria real deles (ver Passo 4). Eles são a fonte da variedade.
- **Catálogo de indicadores externo:** **não** existe no navegador — é opcional. Sem ele, infira a "história" de cada indicador a partir do brief + `references/chart-chooser.md` (ver §Referências).
- **Saída:** gere os SVGs, o índice HTML e o racional como **arquivos para download** no chat. No navegador **não** há "pasta do projeto" no disco nem caminho `C:\...`.

## Quando usar

- Já existe o Escopo Funcional (telas, indicadores, dimensões, relação tela→indicador→dimensão→filtro) e você quer **ver e validar com o cliente** como o dashboard vai parecer antes de abrir o Power BI.
- Precisa **decidir o tipo de gráfico** de cada visual com base em boas práticas, não no "sempre fizemos assim".
- Quer um artefato de design para anexar à apresentação de kickoff.

**Não usar quando:**
- Você ainda não sabe nem telas/indicadores → rode antes `/imersao-pbi-requisitos` (ele levanta o que falta e gera o brief). Ou descreva o domínio e use o modo express aqui.
- Você quer um protótipo clicável/navegável → este mockup é estático (mostra layout, cor e gráfico; não navega).

## Como a skill recebe o conteúdo

Esta é a **2ª de um trio** que se alimenta:
`/imersao-pbi-requisitos` (levanta requisito + define preferências visuais) → **`/imersao-pbi-mockup`** (este).

Três formas de alimentar o mockup (use a 1ª disponível):
1. **Brief do projeto** (ideal) — se `/imersao-pbi-requisitos` rodou, leia o `project-brief.md` gerado: telas, visuais, história e preferências visuais compartilhadas. Schema em `references/project-brief.md`.
2. **Escopo colado** — usuário cola telas/indicadores/dimensões no chat.
3. **Intake por perguntas** — sem brief nem escopo, a skill pergunta (blocos abaixo).

> **Telas NÃO pré-definidas.** Quando o brief/escopo vier como **decisões (com nível + perfil da audiência) + indicadores + preferências visuais, sem telas**, **não pergunte tela a tela**: agrupe os indicadores em telas por **perfil/pergunta** (regra geral: **uma tela por perfil/decisão**, o executivo/farol primeiro), decida o gráfico certo de cada um e **apresente o agrupamento proposto no racional** para o cliente validar. As dimensões/quebras você infere do indicador e da decisão; confirme as não óbvias no racional em vez de travar.

> **Gate de entrada (obrigatório).** Se a skill for chamada **sem nenhum insumo** — sem `project-brief.md`, sem escopo colado e sem respostas de intake —, **NÃO invente telas nem gere um mockup de suposições.** Pare e peça o mínimo: (a) o `project-brief.md` do `/imersao-pbi-requisitos`, **ou** (b) o escopo colado (telas/indicadores/dimensões), **ou** (c) ao menos **domínio + perfis** para o modo express. Só siga o pipeline com uma dessas três entradas. Invocar a skill não é autorização para adivinhar o dashboard.

### Inputs visuais compartilhados (mockup ↔ tema)

Definem a aparência. Se vierem do brief, use-os; senão pergunte:
- **Tema:** Claro (default) ou Escuro.
- **Paleta:** cor primária/ação (marca) — **único obrigatório**. **Opcionais** (só se o cliente tiver manual de marca): **paleta da marca** (cores extras → viram as **categóricas** das séries, na ordem dada, até ~8); **cores semânticas** bom/ruim (→ verde/vermelho de meta, variação, semáforo); **fonte** e **logo**. Sem os opcionais, derive categóricas neutras a partir da cor de ação.
- **Posição do menu de navegação:** Esquerda (trilho, default) · Topo · Nenhum (tela única).
- **Fonte:** Segoe UI (default, nativa do PBI).

### Bloco 1 — Projeto (pergunte junto, só o que faltar; use perguntas estruturadas p/ itens fechados)
1. Cliente / nome do projeto.
2. Tema (claro/escuro) + cor de ação (hex). Default azul `#4E7CFF`.
3. Posição do menu (esquerda/topo/nenhum). Default esquerda.
4. **Perfis (audiência):** quem consome? (ex.: diretor, gerente, vendedor, revenda). Pra cada um: papel **consumidor** (0-clique) ou **produtor** (explora) + altitude (estratégico/tático/operacional). **Cada perfil costuma virar a sua própria tela** — não um drill numa tela só. (Define densidade, sofisticação e nº de telas.)
5. Telas/páginas: nome + foco. Se não souber → modo express.
6. Logo do cliente (opcional).
7. **Recursos de cor condicional (opt-in, custam DAX no PBIX):** quer (a) **destaque do top-1/ofensor por cor** e (b) **subtítulo de insight dinâmico colorido**? Default sugerido: **sim no mockup** (vende melhor) mas marcado como **upgrade opcional** no racional; se o cliente prioriza custo de manutenção, renderize **neutro + título estático**. Pergunte e registre.

### Bloco 2 — Por tela (≤3 telas pode juntar)
7. **O ponto:** que pergunta/decisão a tela responde? (→ título-takeaway)
8. **Perfil dono** da tela (de quem é essa visão?) e **ambiente**: desktop (default) · mobile (dedicado) · TV/gestão à vista · painel. (Ambiente muda o layout — ver Passo 3.)
9. **Indicadores:** nome amigável; marque os que têm meta.
10. **Quebras/dimensões** por indicador (ex.: por regional, por mês, por produto).
11. **Data:** seleção (mês/ano/dinâmica/últimos 12m — **nunca** range início/fim aberto) · comparação (vs ano anterior / vs meta / nenhuma) · **data de referência** (período dos dados) + **atualização**.
12. **Filtros** (default: período atual, discretos).

**Modo express:** só com domínio + perfis, proponha KPIs/visuais padrão do domínio (templates em `references/project-brief.md`) e peça ajuste.

A skill infere a **história** de cada visual, escolhe o gráfico (`chart-chooser.md`, restrito a `pbi-visuals.md`), **mostra o plano da tela** (visual · tipo · status PBI) e, ao ok, renderiza.

> Nunca invente indicador. Ambíguo → infira e **confirme**.
> Rótulos amigáveis no visual ("Receita Líquida", "Produto"), nunca snake_case do modelo (`fato_vendas[receita_liquida]`). Regra: "renomear nos visuais".

## Pipeline de execução

### Passo 1 — Normalizar o escopo em uma matriz de visuais
A partir do brief / respostas / escopo, monte, mentalmente ou em tabela, uma linha por **visual**:

`tela | perfil | ambiente | ordem | indicador(es) | dimensão/quebra | filtro | história`

Uma tela tem vários visuais. Confirme a "história" de cada um (vocabulário abaixo). É a história, não o indicador, que decide o gráfico.

**Uma tela por perfil.** Se o projeto tem vários perfis (diretor, gerente, vendedor, revenda), **separe as telas por perfil** — mesmo modelo, telas diferentes. O diretor vê margem/abrangência; o vendedor vê só a carteira e a meta dele. Não tente servir todos numa tela com drill hierárquico (o consumidor 0-clique não vai navegar). O `ambiente` de cada tela (desktop/mobile/TV/painel) também é decidido aqui, porque muda o layout no Passo 3.

**Reorganize as telas se vier mal dividido (não herde a contagem cegamente).** Mesmo recebendo o brief, valide a divisão antes de desenhar: ao montar a matriz, conte os visuais por tela e veja se cada tela tem **uma** pergunta/perfil/grão/métrica-líder. **Force o split** quando uma tela passa de ~7 visuais, mistura mais de uma métrica-líder no espaço nobre, junta perfis diferentes, ou o nome só fecha com "e/,". **Force o merge** quando uma tela tem <3 visuais ou repete a pergunta de outra para o mesmo perfil. Se reorganizar, **proponha a nova estrutura ao usuário** (tabela `# · Tela · perfil · o ponto · por que separar`, cobrindo todas as análises sem deixar nenhuma órfã) e confirme **antes** de renderizar — é barato mexer aqui, caro depois. (Mesma heurística "uma história, uma tela" do `/imersao-pbi-requisitos` §Passo 3.5.)

### Passo 2 — Decidir o tipo de gráfico de cada visual
Use `references/chart-chooser.md` (matriz completa história→gráfico + anti-padrões). **Toda escolha precisa ser construível no Power BI** — confira `references/pbi-visuals.md` (status ✅ nativo / 🔧 workaround / 🧩 custom) e registre o status no racional. Resumo operacional:

| História da tela | Gráfico (1ª escolha) | Observação |
|---|---|---|
| Um número importa (KPI isolado) | **Número grande** (card), + sparkline e/ou bullet | nunca gauge/velocímetro |
| Comparar categorias | **Barra ordenada** (horizontal se rótulo longo/muitas) | ordenar maior→menor; 1 barra na cor de ação |
| Comparar 2 grupos em N variáveis | **Slopegraph** ou **dumbbell** | destaca quem sobe/desce |
| Parte de um todo | **Barra** ou **donut de 1 fatia destacada** | pizza só ≤3–4 fatias; nunca múltiplas pizzas |
| Composição ao longo do tempo | **100% barras empilhadas** ou **área** | |
| Tendência no tempo | **Linha** (com marcadores nos pontos medidos) | |
| Vs. meta / benchmark | **Bullet graph** / linha de meta / pontos-indicadores | substitui o gauge |
| Achar o ofensor (decompor o consolidado) | **Cascata** / **árvore de decomposição** / barra com pior contribuinte destacado | o agregado esconde o que puxa pra baixo |
| Ranking | **Barra ordenada** ou **lollipop** | top N quando a lista é longa |
| Correlação | **Scatterplot** | linha de tendência opcional |
| Survey / Likert | **Barra empilhada divergente** | escala sequencial → cor sequencial |
| Distribuição | **Histograma** / box plot | |
| Geográfico (só se a geografia importa) | **Mapa** / mapa preenchido | senão, barra |
| Fluxo | **Sankey** | |
| Qualitativo / texto | número grande + ícone, ou tabela heat | |

**Antes de finalizar cada escolha, rode o filtro de anti-padrões** (`references/chart-chooser.md` §Anti-padrões). Se o escopo pedir algo que viola (ex.: "pizza com 16 categorias", "velocímetro", "3D"), **proponha a alternativa correta e registre no racional** — não reproduza o anti-padrão calado. (Tensão conhecida "showcase de N categorias": resolva com barra ordenada + top N + "outros", nunca pizza/3D.)

### Passo 3 — Decidir o layout de cada página
Use `references/layout-dashboard.md`. Princípios (Few + Kirk):
- **Uma tela inteira**, sem scroll. Canvas 1280×720 (desktop). **Ambiente muda o canvas:** mobile = layout vertical dedicado (não o desktop "espremido"); TV/gestão à vista = sem interação, data dinâmica; painel = formato da sala. Ver `references/layout-dashboard.md` §Ambiente.
- **Estratégia 0-clique (consumidores).** A maioria é consumidor: a tela já vem **pronta, filtrada e aberta**. Slicer e drill são exceção, não regra. Nada de obrigar o usuário a montar a visão — ele não monta, exporta pro Excel.
- **Seleção de data é a funcionalidade nº 1.** **Nunca** range início/fim livre (quebra comparativo/sazonal). Use mês/ano + botões (últimos 12m, acumulado) ou data dinâmica. Ver `references/layout-dashboard.md` §Seleção de data.
- **Dois carimbos de data, visíveis (não no rodapé):** **data de referência** (período que os dados representam) perto do título/KPIs + **data de atualização**. Dashboard sem data de referência não decide nada.
- **Título da página** no topo = o ponto/pergunta da tela (frase, não "Vendas"). Isto é o nível **página**.
- **Título de cada visual** (nível **visual**, ver §Títulos de visual abaixo): **nome descritivo** do gráfico, sentence-case semibold (ex.: "Faturamento mensal · R$ milhões") — **não** o insight, **não** caixa alta. O **insight** vai no **subtítulo dinâmico** (com cor condicional).
- **Faixa de KPIs** no topo (3–5 cards); o mais importante à esquerda.
- **Filtros discretos** (faixa superior ou trilho esquerdo estreito), visualmente apagados — nunca no espaço nobre. **Todo filtro tem função clara e distinta** (período + no máx. 2–3 quebras que o perfil realmente usa). **Nada de slicer de preenchimento** — não invente "Comparar ▾", "Visão ▾", "Tipo ▾" só para encher a barra — e **não** adicione um slicer que **duplica** o que o visual já mostra (ex.: "Comparar ▾" quando o gráfico já traz vs meta/vs mês/vs ano). Na dúvida, menos filtro. Cada slicer tem de mapear a uma dimensão/decisão real do brief.
- Agrupar visuais relacionados; **espaço em branco** delimita (não bordas pesadas).
- Ordem de leitura F/Z. Máx. ~5–7 visuais por página.
- Rodapé com fonte + selo de mockup (a data de atualização sobe pra junto do título).

### Passo 3.5 — Escolher o SHELL do projeto e variar o conteúdo dentro dele — OBRIGATÓRIO

Há **duas alavancas diferentes** aqui; não confunda uma com a outra:

- **Coerência (entre as telas do MESMO projeto):** escolha **um shell** no começo do projeto — **navegação** (menu/trilho/topo), **chrome de card** (forma, raio, borda, sombra, faixa de acento), **tipografia** e **sistema de cor** — e **mantenha-o idêntico em todas as telas**. Telas do mesmo dashboard têm de parecer o mesmo produto: escolheu o padrão na tela 1, ele **segue** nas demais.
- **Variedade (dentro do shell, e entre projetos diferentes):** o que **muda** é o **formato de cada card** (número grande, sparkline, donut+valor, vs-meta/bullet, multi-métrica…), o **tipo e o fundo de cada gráfico**, e o **layout interno** de cada tela. É **daqui** que vem a riqueza — **não** de trocar o shell a cada tela.

> **Por que os testes saíam todos iguais:** (1) o shell nunca era **escolhido pelo contexto** — caía sempre no mesmo default (`left-rail` claro azul); e (2) os cards/gráficos eram **reconstruídos de cabeça** (flat, sempre o mesmo "número grande") em vez de **puxados das bibliotecas ricas** (`cards.svg` = 22 cards, `components.svg` = 14 gráficos). Corrigir esses dois pontos é o que gera outputs distintos.

**Escolha do shell — pelo contexto DOMINANTE do projeto** (perfil principal + marca + tema + ambiente), tomando como referência a **tela-farol** (normalmente a executiva). Tabela de candidatos:

| Contexto dominante do projeto | Candidatos de shell (escolha 1) |
|---|---|
| Executivo/estratégico · poucos números-âncora · "visão geral" | `hero-banner` · `topo-marca` · `moldura` · `banda-kpi-colorida` |
| Consolidado **por segmento** (número-âncora por categoria) | `cartoes-segmento` · `cards-accent` · `kpi-footer` |
| Operacional · **ranking** · "top-1 e o ofensor" | `escuro-ranking` · `5kpi-list` · `left-rail` |
| **Uma pergunta**, vários visuais que se apoiam | `grouped-panel` · `2x2` |
| **Produtor que explora** (muitos filtros/drill) | `wide-sidebar` · `left-rail` |
| App-shell padrão do produto (navega entre telas) | `left-rail` · `topbar-grid` · `base` |
| Tema escuro · TV/gestão à vista premium | `escuro-ranking` · `left-rail-dark` |

**Regras:**
1. **Escolha o shell pelo contexto, não pelo default.** A escolha do shell é o que faz **projetos diferentes** parecerem diferentes — registre no racional o sinal que puxou (perfil dominante, marca, tema). `left-rail` claro azul só quando nenhum sinal puxa pra outro (rede de segurança, não 1ª opção).
2. **Coerência do shell em todas as telas.** Escolhido o shell, **não troque** de navegação, de chrome de card, de tipografia nem de sistema de cor entre as telas do projeto. **Exceção de ambiente:** uma tela genuinamente de outro ambiente (TV, mobile dedicado) pode ter o seu layout, mas mantém a **mesma linguagem** de cor/tipografia/marca.
3. **A variedade vem de DENTRO — e é obrigatória.** Dentro do shell coerente, **varie o formato dos cards** (`cards.svg`: escolha o card certo por indicador — sparkline p/ tendência, donut+valor p/ parte-do-todo, vs-meta p/ atingimento…) e o **tipo/fundo de cada gráfico** (`components.svg`, guiado pelo `chart-chooser`). Uma tela inteira de "número grande" repetido é tão pobre quanto trocar o shell é incoerente. **Não** empobreça a tela usando só 1 formato de card.
4. **Menu e tema são recolor, não outro shell:** o shell escolhido vira claro/escuro e recebe o menu na posição pedida sem deixar de ser o mesmo shell. **A posição de menu do brief é OBRIGATÓRIA e não-negociável:** se o brief diz *esquerda*/*topo*, essa navegação **tem** de ser renderizada — escolher um shell que "não tem trilho" **não dispensa** o menu. Adicione-o na posição pedida e **recalcule a grid a partir dele** (trilho esquerdo consome ~72px — o conteúdo começa depois, ex.: `x` inicial ≈ 92). Só use *nenhum* quando o brief pedir explicitamente. **Faixa de filtros no topo ≠ menu de navegação** — não troque um pelo outro. (Falha recorrente: escolher `banda-kpi-colorida`/`hero-banner` e "esquecer" o trilho que o brief pediu.)

### Passo 4 — Renderizar o SVG de cada tela
Use os primitivos de `references/svg-kit.md` (template de canvas + componentes por tipo de gráfico, já nos tokens). Para cada tela:
- **Abra (leia) o arquivo do shell escolhido no Passo 3.5** (`templates/canvas-*.svg`) e **parta da geometria REAL dele** — copie a árvore do arquivo e edite dados/cor/rótulos por cima. **E puxe os cards de `templates/cards.svg` (22 formatos) e os gráficos de `templates/components.svg` (14) que a história de cada visual pede** — é daí que vem a variedade dentro do shell coerente. **Não reconstrua cards/gráficos de cabeça a partir dos tokens** (hand-build gera sempre o mesmo card flat "número grande" e joga fora a biblioteca). Quando o esqueleto replica um exemplo (mapa exemplo→template em `svg-kit.md`), você pode ainda puxar paths exatos do `templates/novos/exemplo_NN.svg`. Comece do arquivo, nunca do zero.
- **Preserve a estrutura de camadas nomeadas** (`<g id="fundo|menu|cabecalho|filtros|kpis|visuais|rodape">`, cada KPI/visual/filtro um grupo) ao editar — é o que deixa o arquivo editável no Figma (ver svg-kit §Camadas nomeadas).
- **Ícones = Google Material Symbols** (`templates/icons-material.svg` = biblioteca de onde se copia o `d=`). **Asse cada ícone como `<path>` com transform+fill hex** — **Figma-safe; NUNCA `<use>`/`<symbol>`/`currentColor`** (quebra no Figma → ícone preto/gigante). Ver `svg-kit.md` §Figma-safe.
- Canvas `viewBox="0 0 1280 720"`.
- Preencha com **dados-dummy plausíveis** (nomes reais de categorias do cliente quando souber; valores fictícios coerentes) para o cliente enxergar a forma. **Cada tela/visual tem a SUA forma:** varie a curva/mix conforme o grão daquela tela — o total costuma ser suave e crescente; uma categoria específica é sazonal e volátil; um realizado pode furar ou cair abaixo da meta. **Nunca copie os mesmos valores de uma tela para outra só trocando o rótulo do eixo** (o gráfico de tendência do total ≠ o da categoria) — dados idênticos entre telas viram *déjà-vu* e o cliente percebe na hora.
- **O dado-dummy tem de CONCORDAR com o insight/subtítulo do visual — direção, magnitude e destaque.** Se o subtítulo diz "cresce", a série sobe da esquerda p/ a direita; se diz "passa de 70%", o valor realmente ultrapassa 70%; se cita um item ("App lidera", "Acessório abaixo da meta"), é **esse** item que recebe o destaque/cor. Num **empilhado 100%**, lembre que a fatia de baixo crescer implica a de cima encolher — não deixe as duas em sentidos trocados. Insight e desenho apontando para lados opostos é o erro que mais salta aos olhos do cliente: a série parece "invertida/trocada" mesmo com a geometria perfeita. Ao terminar cada visual, **leia o subtítulo e confira a forma**.
- Cinzas para o "contexto", **cor de ação só no que importa** na história daquela tela.
- **Título de visual** = nome descritivo (sentence-case semibold); **subtítulo** = insight (o takeaway) com **cor condicional** (bom = cor de ação; atenção = laranja semântico). Mostre o subtítulo já colorido no mockup, e **registre no racional** que o insight dinâmico + cor condicional exige **medida DAX + formatação condicional** no PBIX (é o item mais custoso de desenvolver; pode ficar como upgrade opcional para o cliente).
- Texto é texto SVG real (`<text>`), não imagem — fica nítido e editável.
- Marque visualmente que é mockup: rótulo "MOCKUP — dados ilustrativos" discreto no rodapé.

### Passo 4.5 — Validar geometria (limites de moldura) — OBRIGATÓRIO

Depois de renderizar cada SVG e **antes** de gerar o índice, rode o validador de limites — a regra "nada ultrapassa a moldura do card" é fácil de violar a olho (texto/título/chip que estoura a borda direita ou inferior). O script está **dentro da pasta desta skill** (`scripts/check_bounds.py`); rode-o no sandbox de código apontando para os SVGs gerados:

```bash
python scripts/check_bounds.py tela-*.svg
```

> O caminho do `scripts/check_bounds.py` é resolvido a partir da pasta da skill em runtime; ajuste o prefixo se o sandbox montar a skill em outro diretório. Se por algum motivo o Python não estiver disponível, faça a checagem manualmente (nenhum elemento cruza a moldura do card; cards não se sobrepõem).

Ele abre cada card (`<g id="kpi-*|visual-*">`) e reporta: **ERRO** (elemento cruza a moldura do card), **COLISÃO** (dois cards se sobrepõem na grid — mede as molduras absolutas acumulando os transforms) e **AVISO** — respiro < 4px **e cor semântica no chrome do KPI** (barra de acento / chip de ícone / ícone em laranja/vermelho/verde). O acento é decorativo → cor da **marca/neutro**; status bom/ruim vai no **número/contexto**. **Só siga para o Passo 5 com 0 erros/colisões** e revise os avisos. Se acusar, encurte o texto/título, reposicione pela grid ou troque o acento pela cor de marca. Complementa (não substitui) a validação de XML bem-formado.

### Passo 5 — Gerar índice HTML + racional
- `{Projeto}-mockup.html`: índice navegável que embute os SVGs, uma seção por tela, com o título-takeaway e uma linha de legenda por visual.
- `{Projeto}-mockup-racional.md`: por visual, registra **qual gráfico, por quê** (história → escolha + qualquer anti-padrão recusado e o que foi proposto no lugar). É o que sustenta a conversa com o cliente e com o time.
- Entregue os SVGs, o HTML e o racional como **arquivos para download** no chat.

## Design system do mockup

É um tema de **dashboard**, fiel ao PBI final. Tokens completos em `references/svg-kit.md`. Resumo:

- **Fonte:** `Segoe UI` (a fonte nativa do Power BI → mockup fiel), fallback `system-ui, Inter, sans-serif`.
- **Fundo:** claro (`#FFFFFF` cards sobre `#F5F7FB` página). Tema escuro disponível como variante.
- **Neutros (contexto/dados não-destacados):** cinzas `#C9CDD4` (claro) a `#7C8595` (médio); texto `#33394C` / `#5C6470` / `#7C8595`; grid `#EDEFF2`.
- **Cor de ação:** `{{COR_ACAO}}` = hex da marca do cliente (do intake). Usada **só** no que a história destaca. Default `#4E7CFF` se não informada.
- **Semântico (com parcimônia, colorblind-safe):** positivo `#2E9E5B`, negativo `#D64545`. Prefira intensidade de um mesmo tom a hue diferente; nunca dependa só de vermelho/verde.
- **Meta/benchmark:** linha tracejada `#6B7280`.

## Regras invioláveis (dataviz)

1. **Barra/coluna começa no zero.** Sempre. (Eixo de linha pode ser truncado para revelar variação pequena — mas registre a escolha no racional.)
2. **Sem 3D.** Nunca. Distorce área e ângulo.
3. **Sem gauge/velocímetro.** Use **barra de % + linha constante em 100%** (nativo). Bullet graph é o ideal mas **não é nativo** — só com opt-in do usuário.
4. **Pizza só com ≤3–4 fatias** e quando dá pra ler sem rótulo numérico. Múltiplas pizzas lado a lado = proibido (use barra/slopegraph).
5. **Cor de ação é escassa e com significado.** Destaca **só o item que o insight cita**; o **texto do insight usa a mesma cor da marca destacada** (liga frase↔dado). **Laranja** (atenção/oportunidade) só com **legenda/rótulo** que o explique. Nunca destaque "solto" sem significado, nem destaque numa cor e insight em outra. Ver `references/svg-kit.md` §Regra de cor do insight ↔ destaque.
6. **Não dependa de cor sozinha** para significado (10% dos homens têm daltonismo): combine com posição/rótulo/ícone.
6b. **Só visuais nativos do Power BI (✅) por padrão.** Confirme em `references/pbi-visuals.md`. Para histórias cujo ideal é 🔧/🧩 (bullet, lollipop, dumbbell, sankey…), use o equivalente nativo e registre no racional; o ideal custom só com opt-in explícito do usuário. O cliente precisa confiar que o mockup é construível.
7. **Dois níveis de título.** **Página:** o título do topo é o ponto/pergunta da tela ("Estamos batendo a meta?"). **Visual:** o título de cada gráfico é o **nome descritivo** (sentence-case semibold, ex.: "Faturamento mensal · R$ milhões") e o **insight** (o takeaway, ex.: "2025 superou a meta") vai no **subtítulo dinâmico**, com **cor condicional** (bom = cor de ação; atenção = laranja semântico). Nunca caixa alta em título de visual. Ver `references/svg-kit.md` §Títulos de visual.
8. **Sem chartjunk**: sem gridline pesada, sem borda dupla, sem variedade gratuita de gráfico, sem decoração que não é dado.
9. **Rótulos amigáveis**, nunca snake_case do modelo.
10. **Uma tela = uma ideia central.** Se a tela tem 9 visuais sem hierarquia — ou mistura perguntas/perfis/grãos/métricas-líderes — repense (provavelmente são 2–3 telas). Aplique a heurística "uma história, uma tela" (Passo 1), **proponha a nova divisão e confirme** com o usuário antes de renderizar. Não herde uma contagem de telas ruim só porque veio no pedido.
11. **Uma tela por perfil.** Diretor, gerente, vendedor e revenda têm necessidades diferentes — cada um sua tela, mesmo modelo. Não confie no drill hierárquico pra atender perfis distintos numa tela só.
12. **0-clique por padrão.** Consumidores (a maioria) não garimpam: a tela já vem filtrada e pronta. Interatividade (slicer/drill) é exceção justificada, não regra — e nunca no espaço nobre.
13. **Seleção de data sem range aberto.** Mês/ano + botões (últimos 12m, acumulado) ou data dinâmica (hoje/último fechamento/D-1/última operação). Range início/fim livre é proibido — quebra análise comparativa/sazonal. Filtro de data **à esquerda**, seleção **destacada**, ordem **mês-ano**.
14. **Data de referência + data de atualização visíveis.** Dois carimbos distintos, perto do título/KPIs (não escondidos no rodapé). Sem data de referência, o número não decide nada.
15. **Título localiza a tela.** Área + assunto na cara ("Compras — Análise de pedidos"), nunca uma tag de unidade de negócio como título.
16. **Coerência KPI ↔ corpo.** Os cards do topo são os indicadores que a audiência diz serem os principais; o indicador-chave do corpo vira card; as quebras são do indicador-líder. Não esconda o total/denominador.
17. **Número com unidade e com juízo.** Todo número tem unidade (dias, %, R$) e sinaliza bom/ruim (Δ com direção clara e/ou sparkline). % além do absoluto quando ajuda. Fundo de card é neutro — cor só com significado.
18. **O evolutivo não é o centro por default.** O espaço nobre responde a pergunta da tela (estado atual + quebra que explica). Tendência é suporte, salvo quando o ponto da tela é a própria tendência.
19. **SVG editável e Figma-safe.** Cada tela é uma **árvore de grupos nomeados** (`<g id="fundo|menu|cabecalho|filtros|kpis|visuais|rodape">`, com cada KPI/visual/filtro num grupo próprio deletável de uma vez) e **NUNCA usa `<use>`/`<symbol>`/`currentColor`** (ícones assados como `<path>`+transform+fill hex). Filtros sempre dentro da margem (respiro ≥24px da borda, texto não vaza da pílula). **id de grupo nunca colide com id de gradiente** (senão `url(#x)` aponta pro grupo e a forma some) — sufixe gradientes (`-grad`). Ver `references/svg-kit.md` §Camadas nomeadas e §Figma-safe.
20. **Contraste WCAG AA.** Texto pequeno ≥4,5:1, texto grande/bold ≥3:1 contra o fundo onde ele está. A cor de ação `#4E7CFF` é clara demais p/ texto branco pequeno → sob texto branco use tons PROFUNDOS (`#2E50C8`/`#6A2BD9`/`#B5283C`/`#0E6E62`/`#14215C`); fundo claro (`#1FB8A6`, `#F4A261`…) pede texto escuro `#15171C`; gradiente sob texto deve passar nas DUAS pontas; filtro sobre faixa colorida = chip branco com texto escuro. Ver `references/svg-kit.md` §Contraste.
21. **Legenda sempre no topo-esquerda.** Séries/status/meta no canto superior-esquerdo do visual, sob o título/insight, na horizontal — nunca à direita/embaixo/solta. Ver `references/svg-kit.md` §Legenda.
22. **Cor pela Doutrina de cor.** neutro (contexto) → ação (foco, 1 por gráfico) → semântica (bom/ruim) → categórica (séries). O Δ é **verde/vermelho por direção × polaridade do indicador**, não pela seta (turnover↓=verde; custo↑=vermelho). Laranja só "atenção sem veredito", com legenda. Ver `references/svg-kit.md` §Doutrina de cor.
23. **Todo gráfico legível: rótulos de dado OU eixo de valor — nunca os dois ausentes** — e sempre rótulo de categoria + eixo de tempo. Coluna/linha sem rótulo, sem eixo e sem categoria é proibido (erro comum). Ver `references/svg-kit.md` §Regras de uso do kit.
24. **Cor condicional é opt-in do cliente.** O **destaque do top-1/ofensor por cor** e o **subtítulo de insight dinâmico colorido** ("highlight abaixo do título") custam DAX + formatação condicional. **Pergunte** se o cliente quer; sem opt-in, entregue neutro + título descritivo estático (a cor de ação fixa num item-chave é barata e permitida). Registre no racional.
25. **Layout independe do tema.** Qualquer esqueleto `canvas-*` serve para claro ou escuro — recolore pelos tokens (claro↔escuro) mantendo a cor de ação. Escolha o layout pela história, não pelo tema; os 2 esqueletos "dark" são só atalhos já recoloridos.
26. **Teste de escala de cinza.** Todo visual tem de se sustentar em P&B: se em cinza as séries se confundem, o destaque some ou o bom/ruim some, conserte com posição/rótulo/símbolo/intensidade. Cor é reforço, nunca o único canal (daltonismo). Ver `references/chart-chooser.md` §Teste de escala de cinza.
27. **Consistência de cor por grupo no projeto inteiro.** Mesma cor = mesmo grupo em **todas as telas** (ex.: Sul sempre no mesmo tom). Entre dois visuais, só o dado muda — a construção e a codificação de cor permanecem. Não varie o tipo de gráfico "por variar". **Mas coerência é de CONSTRUÇÃO (tipo/cor/eixos/rótulos), não de DADOS:** o mesmo gráfico de tendência na tela do total e na tela de uma categoria mantém o tipo, porém tem de ter **desenho de dados diferente** (escala, sazonalidade e atingimento próprios daquele grão). Reutilizar a mesma curva/valores-dummy entre telas faz elas parecerem copy-paste — "mesma história → mesmo gráfico" fixa o **tipo**, jamais a forma dos dados.
28. **Faça a conta pelo leitor.** Todo cálculo que o visual insinua (variação, % do total, margem, saldo, atingimento) já vem **calculado e exibido**; o usuário não subtrai de cabeça nem cruza dois números. Todo número com referência comparativa (meta/média/período).
29. **Acabamento por tipo de gráfico.** Respeite os limiares de cada visual (barra ≈2× o vão e começa em 0; linha ≤5 séries ocupando ~⅔ do eixo; dispersão ≤5 grupos + transparência 0,3–0,7; histograma com bins iguais e barras coladas; pizza ≤3–4 e cor sólida; eixo rotulado com unidade, texto reto e não-bold). Detalhe em `references/chart-chooser.md` §Parâmetros e acabamento.
30. **Dado financeiro tem regras próprias.** ≤5 dígitos visíveis (reescale o eixo p/ milhares/milhões), moeda explícita, negativos entre parênteses, % sempre com o absoluto à vista, tempo no eixo X, datas `dd mmm aaaa`/`mmm aa`, gráficos comparados na mesma escala, vermelho só para negativo. Ver `references/dados-financeiros.md`.
31. **Grid global, nunca grids independentes por linha.** Toda tela usa uma única grid de 12 colunas, com margem e gutter constantes. Cards só podem começar e terminar em linhas dessa grid e devem ocupar spans inteiros (`2/3/4/6/8/9/12`). Divisões equivalentes entre linhas precisam compartilhar os mesmos eixos: uma linha `8 + 4` deve alinhar exatamente com uma linha `4 + 4 + 4`. Coordenadas e larguras arbitrárias são proibidas — todo `x`/`width` é derivado de `coluna_inicial` e `span`. O conteúdo se adapta ao card; o card nunca quebra a grid para caber o conteúdo. Ver `references/layout-dashboard.md` §Grid estrutural rígida e `references/svg-kit.md` §Posicionamento calculado pela grid.
32. **Shell coerente no projeto; variedade vem de dentro; partir do arquivo real.** O **shell** (navegação + chrome de card + tipografia + sistema de cor) é escolhido **uma vez** pelo contexto dominante do projeto (Passo 3.5) e **segue idêntico em todas as telas** — não troque de esqueleto/navegação/estilo de card entre telas do mesmo dashboard (exceção só de ambiente: TV/mobile dedicado, mantendo a mesma linguagem de cor/marca). A **variedade** é obrigatória e vem **de dentro**: varie o **formato dos cards** (`cards.svg`) e o **tipo/fundo dos gráficos** (`components.svg`) conforme a história de cada visual — nunca uma tela toda no mesmo card repetido. Ao renderizar (Passo 4), **abra (leia) o `templates/canvas-*.svg`, `cards.svg` e `components.svg` e parta da geometria real**; reconstruir cards/gráficos de cabeça a partir dos tokens é proibido (é o que colapsava todo teste no mesmo mockup médio). Ver Passo 3.5 e `references/svg-kit.md` §Esqueletos.

## Postura (consultor, não executor de pedidos)

O storytelling é trabalho de **consultor**: quem fez o levantamento e domina a ferramenta tem a autoridade — e o dever — de **questionar pedidos e defaults**, não obedecer cegamente.

- **Cliente pediu algo que prejudica a leitura?** (título = nome da unidade, evolutivo no centro, filtro escondido) — não reproduza calado. Questione, entenda o porquê, e **se discordar, explique com argumento e traga uma solução**. Registre a recomendação no racional.
- **"É o padrão / sempre fizemos assim" não é justificativa.** Se um default não tem racional ("filtro sempre à direita", "ano-mês", "cor por card"), ele está em aberto pra melhorar. Padrão bom se sustenta com argumento.
- **Indicador sem referência?** Se o cliente não tem um SLA/meta formal, pergunte o que ele consideraria bom — ou busque a referência de mercado — pra que todo número possa dizer bom/ruim.

## Validação narrativa (antes de renderizar e de apresentar)

Antes de desenhar (e antes de apresentar), **percorra a história na matriz de visuais**, não a navegação ("aqui tem isso, aqui tem aquilo"). Vá do **KPI que chama atenção → quebra que explica → ofensor**, em poucos saltos. Isso revela os furos cedo: total faltando, indicador-chave sem card, número sem unidade, quebra que não existe pro indicador certo. Ache os furos aqui — não na frente do cliente.

**Checagem anti-redundância (dentro da mesma tela).** Dois visuais **não podem responder à mesma pergunta pela mesma quebra** só mudando o formato. Ex.: barra "GMV por categoria" + donut "GMV por grupo" decompõem o **mesmo total pela mesma dimensão** (grupo é só o pai de categoria) = redundante. Regra: se dois visuais compartilham **indicador E dimensão** (ou uma dimensão é hierarquia da outra), funda-os ou **troque um por uma quebra/grão que a tela ainda não mostra** (ex.: novo × recorrente, canal, tempo). Cada card só ganha lugar se responde algo que os outros da tela não respondem.

**Checagem de coerência insight ↔ dados (dentro do mesmo visual).** O desenho dos dados-dummy tem de **fazer o que o subtítulo afirma**. Antes de fechar cada visual, leia o insight em voz alta e confira contra a forma em três eixos: **direção** ("cresce/cai" ↔ a série sobe/desce no sentido certo), **magnitude** ("passa de X%", "lidera com Y" ↔ o valor realmente cruza esse limiar) e **destaque** (o item citado é o colorido/realçado). Atenção ao **empilhado 100%**: a fatia de baixo crescer obriga a de cima a encolher — inverter as duas faz a série de baixo aparecer *decrescente* enquanto o texto diz que cresce (a falha clássica). Insight e dados divergentes fazem o visual parecer quebrado mesmo com a geometria perfeita e o `check_bounds` zerado — é um defeito de conteúdo, que o validador de limites **não** pega.

**Checagem de sobreposição interna (legenda × gráfico × título — dentro do mesmo card).** O `check_bounds` só valida a moldura do card; **não** enxerga um elemento colando em cima do outro *dentro* dele. O erro recorrente: a **legenda/insight** (topo-esquerda, y≈60–72) e a **área do gráfico** brigam pela mesma faixa — barras/colunas altas que sobem até y≈34 invadem a legenda que está em y≈65. Regra de zonas verticais dentro de um card de ~218px de altura: título y≈30 · insight y≈48 · **legenda y≈60–72** · **plot começa em y≥84** e a base fica em y≈190 · rótulos de eixo y≈200–210. **A borda superior do gráfico (topo da barra/coluna/linha mais alta) nunca pode entrar na faixa da legenda** — se a série mais alta chega perto de y84, comprima as alturas (baseline mais baixa) em vez de deixar invadir. Confira a olho: nenhuma barra/ponto/rótulo do gráfico toca a legenda ou o título.

**Checagem de rótulo único por medida (entre TODAS as telas).** A mesma medida usa **um único nome amigável** no projeto inteiro. Não alterne "GMV", "Faturamento" e "Receita" (nem "Receita Líquida"/"Vendas") para o mesmo indicador entre telas — além de parecer desleixo, sugere ao leitor que são **números diferentes** (e, em rigor financeiro, GMV ≠ faturamento ≠ receita contábil, sobretudo em marketplace). Fixe o rótulo do brief (o "nome-mãe" que o cliente usa) e repita idêntico em todo título/legenda/eixo/KPI. Cuidado com **rótulos que vazam dos templates** (`components.svg` traz exemplos como "Faturamento mensal", "Ponte do faturamento", "Receita por região") — ao copiar o gráfico, renomeie para o termo do cliente. Faça um grep final dos sinônimos antes de fechar.

## Output / nomeação

```
{Projeto}-mockup.html              ← índice navegável (arquivo para download)
{Projeto}-mockup-racional.md       ← decisões de gráfico/layout
tela-01-{slug}.svg
tela-02-{slug}.svg
...
```
No navegador, entregue os SVGs, o HTML e o racional como **arquivos para download** no chat.

## Referências da skill (todas dentro desta pasta — autocontidas)

- `references/project-brief.md` — schema do brief compartilhado do trio (consumido se `/imersao-pbi-requisitos` rodou) + templates de domínio (modo express) + vocabulário de "história".
- `references/escopo-input.md` — formato de escopo colado (atalho) + vocabulário de "história".
- `references/chart-chooser.md` — matriz história→gráfico, anti-padrões, **§Parâmetros e acabamento por tipo de gráfico** (limiares de barra/linha/dispersão/histograma/pizza/bullet/sparkline/eixos), **§Faça a conta pelo leitor**, **§Teste de escala de cinza** e tradução nativo/custom do PBI.
- `references/dados-financeiros.md` — regras de dado financeiro: formatação de número (escala, moeda, negativos entre parênteses), % em contexto, eixos (tempo no X, mesma escala, datas), cor (vermelho só p/ negativo) e escolha de gráfico (barra > pizza, sem área empilhada).
- `references/pbi-visuals.md` — catálogo dos visuais nativos do Power BI (campos + config) e status nativo/workaround/custom.
- `references/layout-dashboard.md` — **§Grid padrão (margem 24, gutter 20)**, layout de tela única, faixa de KPI, filtros, posição do menu, ordem de leitura.
- `references/svg-kit.md` — tokens (claro/escuro) + primitivos SVG + **barra de filtros (N + Limpar)** + lista dos templates + regra de cor do insight ↔ destaque.
- `scripts/check_bounds.py` — **validador de geometria** (Passo 4.5): ERRO (elemento cruza a moldura do card), COLISÃO (dois cards se sobrepõem na grid) e AVISO (respiro < 4px · cor semântica no acento/chip/ícone do KPI). Rodar em toda tela antes de fechar o mockup.
- **Ícones (Google Material Symbols):** `templates/icons-gallery.svg` (galeria **visível** — abra p/ escolher) · `templates/icons-material.svg` (biblioteca de `<symbol>`; abre branco, é normal — copie os símbolos p/ o `<defs>`).
- **Esqueletos (`templates/canvas-*.svg`, 16):** `canvas-base` · `canvas-left-rail`(-`dark`) · `canvas-topbar-grid` · `canvas-cards-accent` · `canvas-2x2` · `canvas-5kpi-list` · `canvas-hero-banner` · `canvas-wide-sidebar` · `canvas-kpi-footer` · `canvas-grouped-panel` · `canvas-banda-kpi-colorida` · `canvas-moldura` · `canvas-cartoes-segmento` · `canvas-topo-marca` · `canvas-escuro-ranking`. Todos no **grid padrão** (margem 24, gutter 20), **filtros dentro da margem** (respiro ≥24px) + "✕ Limpar", ícones Material assados como `<path>` (Figma-safe), e **camadas nomeadas** (`<g id>` por bloco).
- `templates/cards.svg` — **22 cards de KPI** (cada um `<g id="card-NN-...">`): 12 por função + 10 variações de acento.
- `templates/components.svg` — **catálogo de 14 gráficos** (cada um `<g id="grafico-NN-tipo">`) com "Quando usar".
- `templates/novos/` — backgrounds-referência (`exemplo_01..22`) · `templates/novos/Card/` — 10 cards-referência.

<!-- DS: gold · /imersao-pbi-mockup -->
