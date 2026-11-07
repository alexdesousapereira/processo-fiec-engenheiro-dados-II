# Dados financeiros — formatação, eixos e escolha de gráfico

Dado financeiro é o mais comum em entrega corporativa e tem armadilhas próprias (escala, sinal, moeda, comparabilidade). Estas regras **complementam** o `chart-chooser.md` e o `svg-kit.md` — não os substituem. Quando algo aqui for específico de finanças, ele vence **só no contexto financeiro**; fora disso, vale a doutrina geral.

## Formatação de número

- **No máximo ~5 dígitos visíveis** por valor. Número comprido (`123.450.000`) não se lê de relance.
- **Reescale o eixo para a unidade certa** (milhares / milhões / bilhões) para que os valores apareçam entre ~`(1.000)` e `1.000`. Ex.: exiba **`123,45`** tanto para `123,45` quanto para `123.450.000` — no 2º caso o rótulo do eixo vira **"R$ milhões"**. No PBIX isso é `labelDisplayUnits` (Milhares/Milhões/Bilhões).
- **Toda unidade explícita** (R$, US$, %, dias). Número solto sem unidade não decide nada (regra geral do kit) — em finanças, **declare a moeda**: `R$ 100,00`, `US$ 100,00` (não só "100,00").
- **Negativos entre parênteses** — `(1.000)`, não `-1.000`. É a convenção contábil e evita o sinal "−" passar despercebido.
- **Arredonde** para a unidade reescalada; não misture grãos (`R$ 1,8 mi` e `R$ 1.234.567` na mesma faixa).
- **Faça a conta pelo leitor.** Qualquer cálculo implícito (variação, %, margem, total, saldo) já vem **calculado e exibido** — não deixe o usuário fazer a subtração de cabeça.

## Percentual sempre em contexto

- Percentual **acompanhado do valor absoluto** a que se refere (próximo, no mesmo visual ou no card-base). `7%` sozinho não diz se são 7% de R$ 5 mi ou de R$ 50 mil.
- Ao comparar grupos por %, **mostre o denominador/total** de cada grupo, ou um valor âncora visível — % entre grupos precisa de um valor monetário real à vista.

## Cor (em cima da Doutrina de cor do `svg-kit.md`)

- **Nunca vermelho para valor positivo.** Vermelho carrega "perda/prejuízo" no negócio. Vermelho só para **negativo** (prejuízo, queda ruim) ou como **destaque de atenção** pontual, sempre com rótulo.
- **1 categoria/grupo só:** positivo em **verde-escuro ou preto/neutro**, negativo em **vermelho**. A posição no eixo (acima/abaixo, à esquerda/direita do zero) já sinaliza o sinal.
- **Vários grupos:** a cor codifica **o grupo** (categórica), e o **sinal** vem da posição em relação ao eixo — não tente codificar grupo *e* sinal só na cor.
- Ao **destacar uma linha** entre várias, deixe-a bem **mais escura ou mais saturada** que as demais (as outras recuam para o cinza de contexto).
- **Traço tracejado é reservado a linhas de referência** (meta/benchmark/limite). **Série de dado e linha de tendência/regressão sobre dado financeiro = traço sólido** — não use tracejado/pontilhado para representar dado real (confunde com a linha de meta).

## Eixos

- **Tempo sempre no eixo X.** Em séries por grupo ao longo do tempo, **o tempo é o eixo mais externo**.
- **Negativos à esquerda do eixo Y / abaixo do eixo X**, e mostrados entre parênteses `(1.000)`.
- **Mesma escala ao comparar gráficos lado a lado.** Não exiba um de `R$ 0–30` ao lado de outro de `R$ 0–100` — a comparação visual fica falsa. Para comparar **variação relativa**, **normalize** (índice/base 100) para que os gráficos fiquem na mesma escala.
- **Incrementos naturais** no eixo de valor (1,2,3… / 5,10,15… / 10,20,30…), não números quebrados.
- **Formato de data:** `dd mmm aaaa` ou variante (`mmm aa`) — ex.: `04 mar 2025`, `mar/25`. Casa com a ordem **mês-ano** do seletor de período (nunca `aaaa/mm`, que é leitura de modelo).

## Escolha de gráfico (financeiro)

- **Comparar valores entre grupos/segmentos → barra/coluna.** **Pizza evitada** — use barra (regra geral; reforçada aqui).
- **Participação/composição (market share, divisões do negócio em % do todo) → barra horizontal em ordem decrescente.**
- **Preço/valor ao longo do tempo → linha.** Relações → dispersão ou linha.
- **Valor vs. limite/benchmark → barra de % + linha constante (nativo)** ou uma linha de referência reta sobre linha/dispersão (ver `chart-chooser.md` §`vs-meta`).
- **Evite área empilhada em dado financeiro.** Em vez de empilhar, mostre **dois gráficos**: um com a **tendência do total** e outro com **uma linha por grupo**. (No geral a área empilhada é aceita para volume; em finanças, prefira separar total e séries.)
- **Muitos valores em pouco espaço → tabela/matriz com sparkline** por linha (valor + mini-tendência ao lado).
- **Mapas com parcimônia**, só para atividade relativa por muitas regiões; dado financeiro geográfico costuma ler melhor em **barra comparativa**.

## Checklist financeiro (rodar junto com o de layout)

- [ ] Valores com ≤5 dígitos visíveis e **unidade de escala** declarada (R$ milhões etc.)?
- [ ] **Moeda explícita** (R$/US$) e **negativos entre parênteses**?
- [ ] Todo **%** tem o **absoluto/denominador** à vista?
- [ ] **Tempo no eixo X**; datas em `dd mmm aaaa` / `mmm aa`?
- [ ] Gráficos comparados na **mesma escala** (ou normalizados)?
- [ ] **Vermelho só para negativo/atenção** (nunca para positivo)?
- [ ] **Cálculo implícito já calculado e exibido** (variação, margem, total)?
- [ ] Composição por barra (não pizza); sem área empilhada (total + séries separados)?
