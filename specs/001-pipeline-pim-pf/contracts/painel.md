# Contrato: painel em PBIP

## Dados

- **Conexão**: PostgreSQL, com servidor e porta em parâmetros, usuário `pim_leitura` e modo de importação.
- **Tabelas**: `vw_transformacao_2025`, `vw_top3_transformacao_2025`, `dim_territorio`, `dim_categorias` e `dim_calendario`, todas do schema `warehouse`.
- **Relacionamentos**: as views se ligam às dimensões por UF, atividade e `periodo`, com filtro em uma só direção.

## Medidas

| Medida | Regra |
|---|---|
| Índice de produção | Média de `indice_producao` no contexto; no grão UF × mês × atividade, é o próprio valor |
| Média das atividades | Média de `media_atividades_uf_mes` no contexto |
| Diferença para a média | Índice de produção menos Média das atividades |
| Atividades acima da média | Contagem de atividades com diferença maior que zero |
| Atividade líder | Nome da atividade com `posicao = 1` |
| Índice do top 3 | Média de `indice_producao` em `vw_top3_transformacao_2025`, usada nas barras do top 3 |
| Cor da diferença | Cor `good` ou `bad` do tema, conforme o sinal da diferença |

O recorte fica nas consultas do modelo: só UFs, só 2025 e só atividades de transformação. Assim, os filtros não listam outros itens.

## Telas

Exatamente duas, com o tema e os fundos em SVG em `powerbi/Observatorio.Report/StaticResources/RegisteredResources/`, pois o formato PBIR exige esse local.

### Capa

- Título, recorte (Indústria de Transformação, 2025, Número-índice 2022=100) e fonte (IBGE, tabela 8888).
- Botão para a tela de análise.

### Análise

Filtros: UF e mês, com uma opção por vez. O painel abre em Ceará e janeiro, um caso conferido à mão.

| Visual | Pergunta que o título responde |
|---|---|
| Cartões: atividade líder, média das atividades, atividades acima da média | Como está a UF neste mês? |
| Barras com o top 3 | Quais atividades mais produziram em relação a 2022? |
| Barras divergentes de todas as atividades, ordenadas pela diferença | Quais atividades estão acima ou abaixo da média da UF? |
| Linha da média por mês, sem responder ao filtro de mês | Como a média da UF evoluiu em 2025? |

## Regras de exibição

- Atividades sem dado não aparecem nem contam como zero, e uma nota explica isso na tela.
- Valores acima da média usam a cor `good` do tema, e os abaixo usam `bad`, sempre com rótulo numérico para não depender só da cor.
- Fonte e recorte ficam visíveis na tela de análise.

## Aceitação

Selecionar Ceará e janeiro de 2025 deve mostrar média 101,58 e top 3 com 3.13 Têxteis (145,03), 3.24 Metalurgia (136,56) e 3.11 Bebidas (120,05).
