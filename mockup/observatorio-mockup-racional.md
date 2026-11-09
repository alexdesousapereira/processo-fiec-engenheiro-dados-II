# Racional do mockup: painel do Observatório da Indústria

Mockup estático das duas telas do painel, feito antes de ajustar o PBIP e seguindo as regras de `requisitos/pbi-mockup`. Essa pasta não é
versionada, então as regras aplicadas estão resumidas no fim deste documento. Especificação: [specs/002-mockup-power-bi](../specs/002-mockup-power-bi/spec.md).

| Arquivo | Conteúdo |
|---|---|
| [tela-01-capa.svg](tela-01-capa.svg) | Capa: pergunta, recorte, como ler e acesso à análise |
| [tela-02-analise.svg](tela-02-analise.svg) | Análise: Ceará, janeiro de 2025 |
| [observatorio-mockup.html](observatorio-mockup.html) | Índice com as duas telas |
| [dados-referencia.sql](dados-referencia.sql) | Origem de todos os números |
| [conferir_mockup.py](conferir_mockup.py) | Confere as telas contra o warehouse e as regras de SVG |
| [ferramentas/gerar_telas.py](ferramentas/gerar_telas.py) | Gera as telas a partir do warehouse |
| [ferramentas/check_bounds.py](ferramentas/check_bounds.py) | Validador de geometria do `pbi-mockup`, copiado sem alterações |

## Decisões de projeto

**Esqueleto: `topo-marca`.** É uma barra superior com a marca do Observatório e a navegação em abas (Capa e Análise), igual nas duas telas. Há um só perfil,
analistas e estatísticos que consomem telas prontas, e só duas telas. Por isso, a barra superior serve melhor que um trilho lateral, que é o padrão "de
segurança" que o próprio `pbi-mockup` desaconselha sem motivo.

**Cor de ação: `#0E4194`**, a cor de destaque do tema do Observatório. Ela marca só o que o insight cita: o top 3, o mês selecionado e a aba ativa. Todo o resto é neutro.

**Fusão de dois gráficos (regra antirredundância).** O contrato anterior do painel tinha dois gráficos de barras, o top 3 e a diferença para a média. Os dois
decompõem o **mesmo índice pela mesma atividade**, e a ordem é idêntica, porque a diferença é o índice menos uma média constante. Um único gráfico, com
todas as atividades ordenadas, o top 3 destacado, a linha da média e o rótulo "índice (diferença)", responde às duas perguntas e libera espaço para a tendência.

## Visuais da análise

| Bloco | Visual | História | Gráfico e motivo | Recusado | Campo ou medida | Filtro | Power BI |
|---|---|---|---|---|---|---|---|
| `kpi-1` | Atividade líder | `kpi` | Cartão com nome, índice e diferença: diz quem lidera sem obrigar a ler o gráfico | Cartão só com o número, que esconderia o nome | `[Atividade líder]`, `[Índice de produção]`, `[Diferença do líder]` | UF e mês | Cartão (novo) ✅ |
| `kpi-2` | Média das atividades | `kpi` | Número grande com o total de atividades com dado, que é o denominador da média | Velocímetro (proibido) | `[Média das atividades]`, `[Atividades com dado]` | UF e mês | Cartão ✅ |
| `kpi-3` | Acima da média | `kpi` | "5 de 11" com minibarra de proporção: faz a conta pelo leitor | Rosca, um gráfico a mais para 2 fatias | `[Atividades acima da média]`, `[Atividades com dado]` | UF e mês | Cartão ✅ |
| `visual-principal` | Índice de produção por atividade | `ranking` + `comparar-categorias` | Barras horizontais ordenadas, a partir do zero, com top 3 na cor de ação e linha da média | Dois gráficos de barras redundantes; barras divergentes, que esconderiam o índice pedido pela prova | `dim_categorias[categoria_rotulo]`, `[Índice de produção]`, `[Cor do ranking]`, linha constante `[Média das atividades]` | UF e mês | Barra agrupada ✅ |
| `visual-1` | Média das atividades por mês | `tendencia` (suporte) | Linha de 12 meses com eixo de valor, mês selecionado na cor de ação e pico rotulado | Linha no espaço nobre: o ponto da tela é o mês, não a evolução | `dim_calendario[mes_nome]`, `[Média das atividades]` | Só UF, sem responder ao mês | Linha ✅ |

**Detalhes que valem no painel:**
- **Nomes longos:** o rótulo do eixo é "CNAE + nome", cortado com reticências em cerca de 34 caracteres, como o Power BI faz; o nome completo fica na dica. O maior nome tem 87 caracteres.
- **Eixo da linha:** começa em 80, e não em zero. Para linhas isso é permitido, porque revela a variação mensal; barras sempre começam em zero.
- **Legendas:** no topo-esquerda de cada visual. No PBIX, Formato → Legenda → Posição: Superior, à esquerda.
- **Subtítulo com insight e destaque do top 3:** exigem medidas DAX (`[Insight do líder]` e `[Cor do ranking]`) e formatação condicional. É o item mais custoso do painel e já estava em uso.

## Telas

| Tela | Título (o ponto) | Carimbos de data |
|---|---|---|
| Capa | Quais atividades puxam a produção industrial em cada UF? | Dados: jan a dez/2025 · atualizado em 08/11/2026 |
| Análise | Indústria de Transformação — atividades da UF no mês | Dados: jan/2025 · atualizado em 08/11/2026 |

**Filtros:** UF e mês, como pílulas discretas à direita do título. O mês selecionado fica destacado e vem em ordem mês-ano ("Jan/2025"). Não há botão "Limpar",
porque os dois filtros aceitam uma seleção por vez e nunca ficam vazios.

## Desvios em relação ao `pbi-mockup`

| Regra do `pbi-mockup` | O que foi feito | Motivo |
|---|---|---|
| Dados fictícios e selo "dados ilustrativos" | Números reais do warehouse e selo "números do warehouse em 08/11/2026" | O warehouse já existe, e a constituição exige dados medidos. O conferidor garante que todo número exibido vem do warehouse |
| Uma tela por perfil | Duas telas, capa e análise | Há um só perfil; as telas vêm de `decisoes.md` |
| Barra de filtros com "Limpar" | Sem "Limpar" | Os filtros aceitam uma seleção por vez e nunca ficam vazios |
| Texto pequeno em `#7C8595` e selo em `#C9CDD4` | Texto pequeno em `#5C6470` | Os tons do `pbi-mockup` dão 3,9:1 e 1,5:1, abaixo do mínimo de 4,5:1 (SC-004) |
| Telas desenhadas a partir do arquivo do template | Gerador que reproduz a geometria do template com os números do warehouse | Se o IBGE revisar os dados, basta regerar, sem redesenhar à mão |

## Contraste (WCAG AA)

Calculado pelo gerador (`ferramentas/gerar_telas.py`).

| Par | Cores | Razão | Mínimo |
|---|---|---|---|
| Texto principal sobre cartão | `#33394C` / `#FFFFFF` | 11,5:1 | 4,5:1 |
| Texto secundário sobre cartão | `#5C6470` / `#FFFFFF` | 6,0:1 | 4,5:1 |
| Texto secundário sobre a página | `#5C6470` / `#F5F7FB` | 5,6:1 | 4,5:1 |
| Cor de ação sobre cartão | `#0E4194` / `#FFFFFF` | 9,5:1 | 4,5:1 |
| Pílula ativa | `#0E4194` / `#0E4194` a 12% | 7,8:1 | 4,5:1 |
| Botão | `#FFFFFF` / `#0E4194` | 9,5:1 | 4,5:1 |

**Escala de cinza:** conferida na tela renderizada. O top 3, em tom escuro, segue distinto das demais barras, em cinza claro; a média é tracejada; e as
diferenças têm sinal. A cor nunca é o único canal.

## Verificações

| Verificação | Resultado |
|---|---|
| `check_bounds.py` nas duas telas | 0 erros, 0 colisões e 0 avisos |
| `conferir_mockup.py` | 28 valores obrigatórios presentes, nenhum número sem origem no warehouse e nenhum problema de estrutura |
| Teste negativo do conferidor | Trocar `101,58` por `101,59` faz a conferência falhar |
| Renderização | Telas convertidas para PNG e revisadas a olho; corrigidos o encosto da aba no nome da marca, o texto no limite do cartão e a linha da média sobre os rótulos |

## Correspondência com o painel (PBIP)

O painel é regerado a partir deste mockup por `powerbi/ferramentas/gerar_pbip.py`. Diferenças conhecidas antes de abrir no Desktop:

| No mockup | No painel | Motivo |
|---|---|---|
| Barra de marca e fundo desenhados | Caixa de texto branca, botões para as abas e cor de fundo da página | O Power BI Desktop descartou os fundos em SVG ao salvar a versão anterior do projeto |
| Ícones nos cartões | Sem ícones | O cartão nativo não tem ícone; uma imagem por cartão seria um elemento a mais para manter |
| Minibarra no cartão "5 de 11" | Só o texto "45% das atividades" | O cartão nativo não desenha barras |
| Rótulo "índice (diferença)" nas barras | Rótulo só com o índice; a diferença aparece na dica e no cartão da líder | O rótulo de dados nativo mostra um valor por barra |
| Rótulos só em janeiro e no pico, na linha | Sem rótulos; eixo de valores e dica | Rotular pontos escolhidos exige uma série a mais |
| Carimbos de data alinhados à esquerda | Cartão com a medida, centralizado na própria caixa | A caixa de texto nativa não mostra valores de medida |
| Legenda "■ Top 3 ■ Demais - - - Média da UF (101,58)" em uma linha de texto | Caixa de texto com a parte fixa e um cartão com o valor da média, que pode mostrar um pequeno traço antes do texto | A caixa de texto nativa não mostra valores de medida; aceito pelo candidato |

**Conferência no Desktop (T018), 2026-11-08:** o candidato abriu o painel no Power BI Desktop e o comparou com o mockup.
Confirmados a linha constante da média nas barras, os subtítulos por medida, a cor de fundo das páginas, os marcadores da linha,
as abas e o botão em azul e os números do caso de referência (Ceará, janeiro de 2025: média 101,58, líder 3.13 Têxteis com
+43,45, top 3 com 3.13, 3.24 e 3.11). As diferenças que ficaram estão na tabela acima.

## Regras aplicadas do `pbi-mockup` (resumo)

**Tela e grade:**
- Canvas de 1280 × 720, sem rolagem.
- Grade de 12 colunas com margem 24 e gutter 20; os KPIs `4+4+4` alinham com o corpo `8+4`.
- Camadas nomeadas (`fundo`, `menu`, `cabecalho`, `filtros`, `kpis`, `visuais` e `rodape`) e um grupo por visual.
- Ícones Material como `<path>` com cor fixa, sem `<use>`, `<symbol>` ou `currentColor`, para abrir no Figma.

**Títulos e datas:**
- O título da tela é o ponto; o título do visual é descritivo; o insight fica no subtítulo, na cor do destaque.
- Data de referência e de atualização sob o título, e não no rodapé.

**Gráficos:**
- Barras começam no zero; sem 3D nem velocímetro; legenda no topo-esquerda; um destaque por gráfico.
- Rótulos amigáveis, com o mesmo nome para cada medida em todo o painel.
- Só visuais nativos do Power BI.
