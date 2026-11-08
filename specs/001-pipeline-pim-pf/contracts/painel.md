# Contrato: painel em PBIP

**Referência visual:** o mockup aprovado em 2026-11-08, em [mockup/observatorio-mockup.html](../../../mockup/observatorio-mockup.html), cujo racional está em
[mockup/observatorio-mockup-racional.md](../../../mockup/observatorio-mockup-racional.md) (feature 002). O PBIP é gerado por
`powerbi/ferramentas/gerar_pbip.py` e validado por `powerbi/ferramentas/validar_pbip.py`.

## Dados

- **Conexão**: PostgreSQL, com servidor, porta e banco em parâmetros, usuário `pim_leitura` e modo de importação.
- **Tabelas**: `fato_producao_fisica_industrial_2025`, `dim_territorio`, `dim_categorias` e `dim_calendario`, todas do schema `warehouse`. O painel não importa views.
- **Recorte**: fica nas consultas do modelo: só UFs, só 2025 e só atividades de transformação. Assim, os filtros não listam outros itens.
- **Colunas criadas na consulta**: `dim_categorias[categoria_rotulo]` ("CNAE + nome", rótulo do eixo) e `dim_territorio[data_carga]` (para o carimbo de atualização).
- **Relacionamentos**: a tabela analítica se liga às dimensões por `territorio_codigo`, `categoria_codigo` e `periodo`, com filtro em uma só direção.

## Medidas

Todas ficam na tabela `Medidas`, que tem uma coluna oculta e nenhuma linha. Índice, média e diferença vêm prontos da tabela analítica, para o painel mostrar os mesmos números da consulta SQL. As regras de exibição, como o top 3 e a líder, são calculadas em DAX.

| Medida | Regra |
|---|---|
| Índice de produção | Média de `indice_producao` no contexto |
| Média das atividades | Média de `media_atividades_uf_mes` no contexto |
| Atividades com dado | Atividades distintas com valor no contexto |
| Atividades acima da média | Atividades com diferença maior que zero |
| Acima da média | Texto "5 de 11" |
| Detalhe acima da média, Detalhe da média | Linhas de contexto dos cartões ("45% das atividades", "11 atividades com dado no mês") |
| Posição no ranking | Posição da atividade pelo índice, entre as atividades com dado; no empate, vence o menor código (igual ao `ROW_NUMBER` do SQL) |
| Cor do ranking | `#0E4194` para posição até 3; `#C9CDD4` para as demais |
| Código do líder (oculta) | Código da atividade de maior índice, com o mesmo desempate |
| Atividade líder, Índice do líder, Diferença do líder | Nome, índice e diferença para a média da atividade líder |
| Legenda da média | Texto "Média da UF (101,58)" da legenda das barras |
| Detalhe do líder, Insight do líder | Subtítulos do cartão da líder e do gráfico de barras |
| Insight da linha | Mês selecionado e pico de 2025 |
| Carimbo de data, Carimbo do período | "Dados: {mês}/2025 · atualizado em {data}" e a versão anual da capa |

Os textos usam `FORMAT` com `"pt-BR"`, para mostrar vírgula decimal como no mockup.

## Telas

Exatamente duas, com o tema do Observatório e fundo `#F5F7FB`, sem imagem de fundo. Os elementos do mockup são feitos com visuais nativos:

- **Barra de marca:** caixa de texto.
- **Abas de navegação:** botões.
- **Carimbos de data:** cartões com medida.

### Capa

Barra de marca com as abas (Capa ativa), título com a pergunta da tela, carimbo do período, recorte, perguntas respondidas, como ler e o botão "Abrir a análise".

### Análise

| Visual | Posição (grade de 12 colunas) | Conteúdo |
|---|---|---|
| `analise_titulo`, `analise_carimbo` | Topo esquerdo | Título da tela e carimbo de data |
| `filtro_mes`, `filtro_uf` | Topo direito | Mês e UF, uma opção por vez; abre em janeiro e Ceará |
| `cartao_lider` | Colunas 0 a 3 | Atividade líder, com subtítulo "Índice · diferença sobre a média" |
| `cartao_media` | Colunas 4 a 7 | Média das atividades, com subtítulo do número de atividades com dado |
| `cartao_acima` | Colunas 8 a 11 | "5 de 11", com subtítulo do percentual |
| `barras_indice` | Colunas 0 a 7 | Barras ordenadas por índice, top 3 na cor de ação, linha constante na média e subtítulo "Insight do líder" |
| `linha_media` | Colunas 8 a 11 | Média por mês de 2025, sem responder ao filtro de mês, com subtítulo "Insight da linha" |

## Regras de exibição

- Atividades sem dado não aparecem nem contam como zero, e o rodapé explica isso.
- O destaque usa só a cor de ação, em um item por gráfico, e os valores aparecem como rótulos, para não depender só da cor.
- Fonte e recorte ficam visíveis nas duas telas.

## Aceitação

Selecionar Ceará e janeiro de 2025 deve mostrar a líder Fabricação de produtos têxteis (145,03; +43,45), a média 101,58, "5 de 11" e o top 3 com
3.13, 3.24 e 3.11 em destaque. Diferenças em relação ao mockup ficam registradas em `mockup/observatorio-mockup-racional.md`.
