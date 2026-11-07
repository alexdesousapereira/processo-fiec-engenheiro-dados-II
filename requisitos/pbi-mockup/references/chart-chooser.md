# Chart chooser — história → gráfico

Base: hierarquia de Cleveland & McGill (posição em escala comum > comprimento > ângulo > área > volume), as 3 famílias de Kirk (confiável, acessível, elegante), regras de dashboard de Few (tela única, sumarização, bullet no lugar de gauge, sparkline, anti-chartjunk) e o "chart chooser" de Evergreen (gráfico certo para a história).

**Regra-mãe:** suba o mais alto possível na hierarquia perceptiva. Comprimento (barra) e posição (ponto/linha) são lidos com precisão; ângulo (pizza), área (bolha) e volume (3D) produzem erro.

**Restrição de produção:** o visual escolhido precisa ser construível no Power BI. Confira o status (✅ nativo · 🔧 workaround · 🧩 custom) em `pbi-visuals.md` e na tabela-resumo no fim deste arquivo. **Por padrão, use SÓ visuais nativos (✅)** — o cliente precisa confiar que o mockup é construível. Quando a 1ª escolha de dataviz for 🔧/🧩 (ex.: bullet, lollipop, dumbbell, sankey), use o **equivalente nativo** (barra de %+linha constante, barra ordenada, etc.) e registre a troca no racional. Só renderize o 🔧/🧩 ideal se o usuário **optar explicitamente** por visual custom.

## Índice

- [Matriz história → gráfico](#matriz-história-gráfico)
- [Anti-padrões — rodar SEMPRE antes de fechar a escolha](#anti-padrões-rodar-sempre-antes-de-fechar-a-escolha)
- [Mapeamento por intenção (Numerro · Choose Your Visuals)](#mapeamento-por-intenção-numerro-choose-your-visuals)
- [Em Power BI — nativo vs. custom (resumo)](#em-power-bi-nativo-vs-custom-resumo)
- [Parâmetros e acabamento por tipo de gráfico](#parâmetros-e-acabamento-por-tipo-de-gráfico)
- [Faça a conta pelo leitor](#faça-a-conta-pelo-leitor)
- [Teste de escala de cinza (acessibilidade — inviolável)](#teste-de-escala-de-cinza-acessibilidade-inviolável)
- [Sequência de decisão (resumo)](#sequência-de-decisão-resumo)

## Matriz história → gráfico

### `kpi` — um número importa
- **1ª escolha:** número grande (card). Se houver meta → **bullet graph**. Se houver histórico → **sparkline** sob o número.
- **Por quê:** Evergreen — um número impactante grava melhor mostrado grande do que dentro de um gráfico.
- **Evite:** gauge/velocímetro (desperdiça espaço, impreciso → bullet).

### `comparar-categorias`
- **1ª escolha:** **barra ordenada** (maior→menor). Barra **horizontal** se os rótulos forem longos ou >~7 categorias.
- **Destaque:** 1 barra na cor de ação, resto cinza.
- **Evite:** pizza; clustered/colunas agrupadas com >2 séries (difícil comparar barras não-adjacentes).

### `comparar-2-grupos` (2 grupos em N variáveis)
- **1ª escolha:** **slopegraph** (ótimo quando 1 cai e o resto sobe) ou **dumbbell dot plot** (ótimo pra enfatizar o gap).
- **2ª:** barras lado a lado **só** se forem ~poucas variáveis.
- **Por quê:** Evergreen — slope/dumbbell mostram a diferença melhor que clustered bars.

### `parte-do-todo`
- **1ª escolha:** **barra** (rotulada como "partes de um todo") ou **100% barra empilhada** (uma barra) quando o foco é a proporção.
- **Donut de 1 fatia destacada:** ok para reforçar UM número.
- **Pizza:** só ≤3–4 fatias e se dá pra ler sem rótulo numérico; fatia maior começa às 12h, sentido horário, maior→menor.
- **Muitas partes / hierarquia:** **treemap**.
- **Proibido:** múltiplas pizzas lado a lado; pizza 3D explodida.

### `composicao-no-tempo`
- **1ª escolha:** **100% barras empilhadas** (proporção) ou **área empilhada** (volume). **Coluna empilhada** quando uma categoria é minúscula.
- **Cor:** sequencial dentro de um mesmo tom.

### `tendencia`
- **1ª escolha:** **linha** (4–5 linhas no máx.; senão small multiples). Marcadores nos pontos realmente medidos.
- **Down=bom?** inverta a variável (ex.: "kg perdidos") ou troque o tipo p/ sinalizar que é diferente.
- **Eixo Y:** linha pode não começar no zero (pra revelar variação pequena) — registre no racional.

### `vs-meta`
- **1ª escolha (NATIVA):** **barra de % de atingimento** (começa em 0) + **linha constante em 100%** (painel Análise) + **formatação condicional** da cor por status (acima/próximo/abaixo, com legenda). Funciona quando a meta varia por item (a barra já é o %).
- **Realizado vs meta em valor (não %):** **colunas/barras** realizado + **linha de meta** (combo) ou linha de benchmark.
- **Status por item:** **pontos-indicadores** (1 tom, intensidades) em tabela/matriz nativa.
- **Bullet graph:** é o ideal de dataviz, mas **NÃO é nativo** no Power BI → só use se o usuário optar explicitamente por visual custom; por padrão use a barra de % + linha constante acima.
- **Proibido:** gauge.

### `achar-o-ofensor` (decompor o consolidado)
- **Problema:** o número agregado (ex.: "87% de atingimento") **esconde** quem puxa pra baixo. Não basta mostrar o total — tem que revelar o ofensor.
- **1ª escolha:** **cascata** (do ponto inicial ao final, mostrando cada variação +/−) ou **árvore de decomposição** (IA, abre o total por dimensão até a folha). Ambas nativas (✅).
- **Alternativa leve:** **barra ordenada** das contribuições com o **pior contribuinte destacado** na cor de atenção (laranja, com rótulo).
- **Combina com `vs-meta`:** mostre o consolidado no KPI e, ao lado, a decomposição que aponta o ofensor — é o par que vira "insight que o cliente não enxergava".
- **Por quê:** o David chama isso de "achar o ofensor"; o consolidado bom esconde um desempenho ruim por baixo, e é justamente esse recorte que gera decisão.

### `ranking`
- **1ª escolha:** **barra ordenada**. Lista longa → **top N** + (opcional) "Outros".
- **Visual mais leve:** **lollipop** (quando as barras ficariam muito "pesadas" de tinta).

### `correlacao`
- **1ª escolha:** **scatterplot** (X e Y contínuos). Linha de tendência reta opcional.
- **Rotule só os pontos de interesse** (não todos). Título declara a relação.
- **N relações:** matriz de small multiples.
- **Público leigo:** considere diagrama de relação (setas) ou só uma frase — scatter confunde muita gente.

### `survey-likert`
- **1ª escolha:** **barra empilhada divergente** (negativos à esquerda, positivos à direita, neutro no meio).
- **Sequencial → cor sequencial** (escuro = mais forte). **Likert → cor divergente** (2 tons opostos).
- **Pode agregar** "concordo"+"concordo muito" se o detalhe não importa pro público.
- **Ranking/check-all-that-apply:** barra ordenada (NUNCA pizza — não soma 100%).

### `distribuicao`
- **1ª escolha:** **histograma** (sem espaço entre colunas) ou **box plot**.

### `geografico` (só quando a localização importa de fato)
- **1ª escolha:** **mapa preenchido** (choropleth) ou **mapa de símbolos proporcionais**.
- **Cuidado:** área do estado vira viés visual. Se a geografia não acrescenta insight → use **barra**.

### `fluxo`
- **1ª escolha:** **Sankey** (largura = quantidade).

### `qualitativo`
- **Citação:** texto formatado (quebras de linha lógicas, 1–2 palavras na cor de ação, foto da pessoa com consentimento). Não usar como gráfico.
- **Número + ícone:** para destacar 1 estatística qualitativa.
- **Temas por entrevistado:** **tabela heat** (1 tom, intensidades).
- **Word cloud:** só pra "gist", e idealmente com drill-down — baixa profundidade analítica.

## Anti-padrões — rodar SEMPRE antes de fechar a escolha

Se o escopo pedir um destes, **não reproduza**: proponha a alternativa e registre no racional.

| Anti-padrão | Por que falha | Use no lugar |
|---|---|---|
| Pizza/donut com >4 fatias | ângulo + área são imprecisos | barra ordenada |
| Múltiplas pizzas lado a lado | comparação impossível | slopegraph / barras / 100% empilhada |
| Gauge / velocímetro | espaço desperdiçado, impreciso | bullet graph |
| Qualquer 3D | distorce área/ângulo, oclusão | versão 2D |
| Barra com eixo truncado | distorce a proporção do comprimento | eixo começando em 0 |
| Bolha (área) p/ comparar valor | área é mal interpretada | barra |
| Radar p/ dado de negócio | layout circular dificulta leitura | barra |
| Pirâmide populacional espelhada (idade × sexo) | **não é nativa** no Power BI (exige eixo divergente/medida-truque ou custom) | **barra/coluna agrupada**: faixa etária no eixo, sexo na legenda (ou 100% empilhada) |
| Clustered bar com 3+ séries | comparar barras não-adjacentes é difícil | small multiples / slope / dumbbell |
| Rainbow / só vermelho-verde | daltonismo, sem hierarquia | 1 tom + intensidade, ou cor+rótulo |
| Variedade gratuita de gráfico | troca de estratégia perceptiva a cada visual | consistência: mesmo tipo p/ mesma história |
| Tudo em negrito/cor | nada se destaca | cinza + 1 cor de ação |
| Card com fundo colorido decorativo (1 cor por card "porque fica bonito") | cor sem significado, e o vermelho/verde semântico **morre** sobre o fundo colorido | card neutro; cor só pra codificar status/seleção (com legenda) |
| Número sem unidade ("47,2" em vez de "47,2 dias") | ambíguo, não decide | sempre a unidade (dias, %, R$); % além do absoluto quando ajuda |
| Gridline pesada / borda dupla / fundo decorado | chartjunk, baixa razão dado-tinta | minimalismo |
| "Showcase de N categorias" em pizza/3D | (tensão conhecida) impossível de ler | barra ordenada + top N + "Outros" |
| Barras finas com vãos largos | desperdiça espaço, dificulta comparar | barra ≈2× o vão entre grupos |
| Intensidades da mesma matiz embaralhadas (zebra) | hierarquia ilegível | ordenar claro→escuro (ou inverso) |
| Eixo duplo medindo o **mesmo** valor em 2 escalas | engana a comparação | um eixo só (ou normalizar) |
| Eixo de valor sem unidade / texto de eixo em negrito ou girado | ambíguo e cansa a leitura | rotular com unidade, texto reto e não-bold |
| Tracejado/pontilhado para série de dado | confunde com linha de meta | tracejado só p/ referência (meta); dado = sólido |

## Mapeamento por intenção (Numerro · Choose Your Visuals)

Tabela cruzada de corroboração — visuais sugeridos por intenção (todos construíveis no PBI; cheque escala em `pbi-visuals.md`):

| Intenção | Visuais sugeridos |
|---|---|
| **Comparação** | Barra · Barra agrupada · Linha · Bolha · Área · Barra empilhada · Ribbon · Mapa de formas · Rosca · Treemap |
| **Dados no tempo** | Barra · Linha · Barra empilhada · Área · Área empilhada · Bolha · Cascata |
| **Correlação** | Bolha · Linha+Coluna · Dispersão |
| **Distribuição** | Bolha · Barra agrupada (+ histograma via bins) |
| **Parte do todo** | Rosca · Barra empilhada · Treemap |
| **Ranking** | Coluna ordenada · Barra ordenada · Ribbon · Árvore de decomposição · Funil |

Mapeie da `história` (vocabulário do projeto) → intenção acima → visual, mas **decida pela hierarquia perceptiva** (barra/posição acima de pizza/área) e pelos anti-padrões. As duas tabelas (esta e a de história) devem concordar; quando divergirem, vence a hierarquia perceptiva.

## Em Power BI — nativo vs. custom (resumo)

Tradução da 1ª escolha de cada história para o que existe no PBI. Detalhe em `pbi-visuals.md`.

| História | 1ª escolha dataviz | Em PBI |
|---|---|---|
| `kpi` | número grande / bullet | ✅ Cartão / Cartão novo / KPI · bullet = 🔧 combo+linha de meta ou 🧩 custom |
| `comparar-categorias` | barra ordenada | ✅ Coluna/Barra agrupada (ordenar, eixo em 0) |
| `comparar-2-grupos` | slopegraph / dumbbell | ✅ **Linha com 2 categorias** (slopegraph) · dumbbell = 🧩 |
| `parte-do-todo` | barra / 100% / donut-1 / treemap | ✅ Coluna/Barra, 100% empilhada, Pizza/Rosca (≤4), Treemap |
| `composicao-no-tempo` | 100% empilhada / área | ✅ Coluna 100% empilhada / Área empilhada |
| `tendencia` | linha c/ marcadores | ✅ Linha (máx. 4–5; senão pequenos múltiplos) |
| `vs-meta` | **barra de % + linha constante 100%** (nativo) / combo coluna+linha de meta | ✅ Barra de % + **Linha Constante** (painel Análise) + formatação condicional · combo coluna+**linha de meta** · bullet 🧩 (só com opt-in) |
| `achar-o-ofensor` | cascata / árvore de decomposição | ✅ Cascata · Árvore de decomposição (IA) · barra ordenada c/ pior contribuinte destacado |
| `ranking` | barra ordenada / lollipop | ✅ Coluna/Barra ordenada · Funil · lollipop 🧩 |
| `correlacao` | scatterplot | ✅ Dispersão (+ linha de tendência) · Principais influenciadores (IA) |
| `survey-likert` | barra empilhada divergente | 🔧 Barra 100% empilhada (divergente via medida) ou 🧩 custom |
| `distribuicao` | histograma / box plot | 🔧 Histograma via bins → Coluna · box plot 🧩 |
| `distribuicao` demográfica (idade × sexo) | pirâmide populacional | ❌ pirâmide espelhada **não-nativa** → ✅ **Coluna/Barra agrupada** (faixa etária × sexo) ou 100% empilhada |
| `geografico` | mapa preenchido | ✅ Mapa coroplético / bolha / formas / Azure / ArcGIS |
| `fluxo` | Sankey | 🧩 Sankey (custom certificado) |
| `qualitativo` | número+ícone / tabela heat | ✅ Cartão + ícone · Matriz + formatação condicional · Narrativa inteligente |

Recursos que destravam várias dessas: linhas de análise (meta/benchmark), barras de erro, pequenos múltiplos, formatação condicional, sparklines em tabela — todos nativos (ver `pbi-visuals.md`).

## Parâmetros e acabamento por tipo de gráfico

Depois de escolher o gráfico (matriz + anti-padrões), aplique os limiares de acabamento. São o que separa um visual "ok" de um legível de relance.

**Eixos e grade (todos os gráficos com eixo):**
- **Eixo sempre rotulado, com unidade** (R$ milhões, %, dias). Eixo sem unidade é ambíguo.
- **Incrementos naturais** no eixo de valor: 1,2,3,4,5 · 5,10,15,20 · 10,20,30… — nunca cortes quebrados.
- **Texto de eixo nunca em negrito** (distrai do dado) e **não rotacionado** quando dá para evitar — texto girado custa leitura (prefira barra horizontal a rótulos verticais).
- **Dois eixos de valor (eixo duplo)** só para **valores diferentes**, nunca o mesmo valor em duas escalas — e **com parcimônia** (combo coluna+linha; ver `pbi-visuals.md`).
- Grade leve ou ausente (regra anti-chartjunk); se houver, mais fina que as linhas de dado.

**Barra / coluna:**
- **Começa em zero. Sempre** (inviolável). 
- **Largura da barra ≈ 2× o vão** entre grupos de barras (barras "gordas", respiro menor) — não barras finas com vãos largos.
- **Valor logo após a ponta** de cada barra (rótulo de dado), para o leitor ler o valor exato.
- **Ordene** maior→menor (ou ordinal/alfabética com motivo). Rótulo longo / >~7 categorias → **horizontal**.
- **Ao codificar categorias por COR num mesmo gráfico, ≤4 cores.** (Distinto do teto de 8 da paleta: 8 é o tamanho do conjunto; ≤4 é quantas cores **um gráfico** aguenta sem virar arco-íris.) Acima disso, agrupe / rotule / use intensidade.
- **Mesma matiz em intensidades:** ordene escuro→claro (ou claro→escuro), **nunca alternado** (efeito zebra).
- **Agrupada > empilhada.** Use empilhada só quando o **total** do grupo é a comparação que importa.

**Linha:**
- **≤5 linhas.** Mais que isso → pequenos múltiplos / trellis.
- **Dados ocupam ~⅔ da faixa do eixo Y** (nem espremidos embaixo, nem estourando o topo). A faixa não pode esconder nem exagerar a tendência.
- **Rotule as linhas** explicitamente; legenda só quando os rótulos poluiriam. Marque **pontos de interesse**. Marcadores só nos pontos **realmente medidos**.

**Dispersão (scatter):**
- **≤5 grupos.** Grupos por **cor + símbolo**, nunca por **tamanho** (tamanho lê-se como valor).
- **Dados ocupam 87–100% da faixa** dos eixos (não espremer os pontos num canto).
- **Sobreposição de pontos → transparência 0,3–0,7** (revela clusters) — sem exagerar a ponto de sumir outlier.
- Comparando vários scatters com a **mesma variável** num eixo → **mesma escala** em todos.
- Só 2D (3D é anti-padrão). Rotule só os pontos de interesse.

**Histograma:**
- Herda as regras de barra. **Bins de largura igual** (1-5, 5-10, 10-15…). **Barras coladas** (sem vão) — o encoste comunica que é um intervalo contínuo.

**Pizza / donut:**
- **≤3–4 fatias**, e só se dá para ler sem rótulo numérico. Começa às **12h**, sentido horário, maior→menor. **Só cor sólida** (sem gradiente/textura). Múltiplas pizzas lado a lado = proibido.

**Bullet (quando opt-in custom):**
- **Vermelho/verde fora da barra** do valor — eles ficam para o juízo bom/ruim, não para a marca de valor.
- **≤5 estados** de fundo (muito ruim → muito bom), em **tons ordenados** claro→escuro (ou inverso), nunca embaralhados.
- Como barra horizontal: esquerda = negativo, direita = positivo.

**Sparkline:**
- **Direto ao lado do valor** que representa (na linha do KPI/tabela), nunca num gráfico à parte.
- Vários sparklines comparados → **mesma escala** nos dois eixos.
- Destaque de mín/máx/atual → **ponto em cor de alto contraste**.

**Mapa:**
- Só quando a **geografia importa de fato** e há dado para **muitas** áreas. Áreas em **cor sólida**; destaque de uma área = cor da paleta. Tons de **um único matiz** para intensidade (heat). Senão → barra.

## Faça a conta pelo leitor

Qualquer cálculo que o visual **insinua**, já entregue **calculado e exibido**: variação vs. período, % do total, margem, saldo, atingimento. O leitor não deve precisar subtrair de cabeça nem cruzar dois números. Isso vale dobrado em dado financeiro (ver `dados-financeiros.md`).

## Teste de escala de cinza (acessibilidade — inviolável)

Antes de fechar qualquer visual, **imagine-o em preto e branco**. Se em escala de cinza a informação se perde (duas séries viram o mesmo cinza, o destaque some, o status bom/ruim fica indistinguível), o gráfico **falha para ~10% dos homens (daltonismo)** — conserte: separe por **posição/rótulo/símbolo/intensidade**, não só por matiz. Cor é reforço, nunca o único canal.

## Sequência de decisão (resumo)

1. Qual a **história**? (vocabulário em `escopo-input.md`)
2. Pega a 1ª escolha da matriz acima.
3. Roda os **anti-padrões**. Bateu? Troca pela alternativa e anota no racional.
4. **Confere construtibilidade no PBI** (✅/🔧/🧩 na tabela acima) e anota o status no racional.
5. Define **o que destacar** (cor de ação) — geralmente o que o "ponto da tela" enfatiza.
6. Escreve os títulos: **título do visual** = nome descritivo (sentence-case semibold, não caixa alta); **subtítulo do visual** = o insight/takeaway com cor condicional (bom = cor de ação; atenção = laranja). O ponto/pergunta da tela fica no título da **página**.
