# Fonte: SIDRA, tabela 8888 (PIM-PF)

Medições feitas em 2026-11-06 nas APIs públicas do IBGE. Reproduza com
`.claude/skills/gerar-arquitetura-dados/scripts/perfil_sidra.py`.

## Endpoints

| Uso | URL |
|---|---|
| Metadados | `https://servicodados.ibge.gov.br/api/v3/agregados/8888/metadados` |
| Períodos e data de modificação | `https://servicodados.ibge.gov.br/api/v3/agregados/8888/periodos` |
| Valores | `https://apisidra.ibge.gov.br/values/t/8888/n1/all/n2/all/n3/all/v/all/p/{AAAAMM}/c544/all/f/a` |

## Estrutura medida

| Item | Valor |
|---|---|
| Períodos | 297, de 200201 a 202609, mensal |
| Última modificação informada | 05/11/2026 |
| Variáveis | 6 |
| Categorias da classificação 544 | 27: Indústria geral, Extrativas, Transformação (agregado) e 24 atividades |
| Territórios | 19: Brasil, Nordeste e 17 UFs |
| Linhas por competência | 3.078 (19 × 6 × 27) |
| Volume total | 914.166 linhas, medido na carga completa |
| Consulta com todos os períodos nas UFs | Recusada com HTTP 400 |

### Variáveis

| ID | Variável |
|---|---|
| 12606 | Número-índice (2022=100), **a usada na camada analítica** |
| 12607 | Número-índice com ajuste sazonal (2022=100) |
| 11601 | Variação M/M-1, com ajuste sazonal (%) |
| 11602 | Variação M/M-12 (%) |
| 11603 | Variação acumulada no ano (%) |
| 11604 | Variação acumulada em 12 meses (%) |

## Índice em 2025, nas UFs

| Medida | Resultado |
|---|---|
| Linhas totais | 5.508 (17 UFs × 27 categorias × 12 meses) |
| Linhas das 24 atividades de transformação | 4.896 |
| Linhas com valor numérico | 2.004 (41%) |
| Linhas com `-` | 2.892 (59%) |
| Pares UF × atividade com valor | 167, todos presentes nos 12 meses |
| Atividades com valor por UF | de 3 (MS, RN) a 17 (SP) |
| UF e mês com menos de 3 atividades | Nenhum |
| Chaves duplicadas (UF, mês, categoria) | 0 |
| Empates entre os 4 maiores índices | 0 |
| Faixa do índice | 0,56255 a 330,62114 |
| Precisão | 5 casas decimais |

## Armadilhas e consequências

| # | Fato medido | Consequência para o desenho |
|---|---|---|
| 1 | **Competência parcial.** Em 202609 só o Brasil tem números; as demais 18 localidades trazem `...` | "Período já existe" não significa "período completo". É preciso recarregar os períodos recentes, ou os que tiveram `...` |
| 2 | **`-` em 59% das atividades de 2025.** O conjunto de atividades de cada UF é o mesmo nos 12 meses | Trata-se de atividade sem dado na UF, de modo estrutural. Converter para 0 distorceria a média; a recomendação é usar nulo e guardar o símbolo original |
| 3 | **Agregado misturado às atividades.** "3 Indústrias de transformação" está na mesma dimensão | Fora da média e do ranking. O filtro usa o padrão `3.NN`, nunca a categoria "3" |
| 4 | **Código fora de ordem.** 3.20 usa o código 56689; as demais vão de 129317 a 129342 | Filtrar por faixa de códigos perderia essa atividade |
| 5 | **Geral = Transformação no Ceará** em 202501 (97,12896), porque a extrativa não tem dado | Mais um motivo para não tratar esses agregados como atividades |
| 6 | **Só 17 UFs existem na fonte** | "Cada UF" significa estas 17. A validação não deve esperar 27 |
| 7 | **Dois símbolos com significados diferentes:** `-` e `...`, ambos presentes em 200201 | O tratamento distingue os símbolos, em vez de fazer uma conversão genérica para nulo |
| 8 | **Resposta da API de agregados vem em gzip** mesmo sem o cliente pedir | O cliente HTTP precisa descompactar |
| 9 | **A primeira linha da API de valores é o cabeçalho** | Usar `/h/n` na URL, que retira o cabeçalho (testado) |
| 10 | **Os 297 períodos têm a mesma data de modificação** em `/periodos` (05/11/2026) | A data avisa que a tabela mudou, mas não qual mês. É preciso comparar o conteúdo de cada mês |
| 11 | **Unidade vazia em 24.111 linhas**, só nas variações 11602, 11603 e 11604, que não têm base de comparação em parte dos meses | A dimensão de variáveis usa apenas linhas com unidade |
| 12 | **Variação de até 11.126.974,6%** (11602, Pernambuco, 04/2021). A base estava perto de zero | `numeric(12,5)` estoura; o projeto usa `numeric(14,5)` |
| 13 | **O nível territorial vem como `1`, `2` e `3`**, sem o prefixo `N` | O tratamento grava `N1`, `N2` e `N3` |

Tempo medido: cerca de 0,5 s por requisição do índice nas UFs para um mês.

## Carga completa (2026-11-07)

Medido nos 297 meses reais, gravados pela DAG.

| Medida | Resultado |
|---|---|
| Linhas por mês | 3.078 em todos os meses |
| Valores numéricos | 258.738 linhas |
| Símbolo `-` | 497.397 linhas |
| Símbolo `...` | 158.031 linhas |
| Outros símbolos (`..`, `X`) | Nenhum |
| Índices (12606, 12607) negativos ou zero | Nenhum |
| Meses sem número nas UFs | Só 202609 |
| Nomes de território, variável e categoria | Não mudam ao longo da série |
| Tempo da extração | Cerca de 3 minutos |

## Metadados e intervalos (2026-11-07)

| Medida | Resultado |
|---|---|
| Requisição de 24 meses (`p/202301-202412`) | HTTP 200, 73.872 linhas (24 × 3.078), 5,5 s e 29,7 MB |
| `/metadados`: variáveis (código, nome, unidade) | Iguais às de `/values` em 202501, nas 6 variáveis |
| `/metadados`: categorias (código e rótulo) | Iguais às de `/values` em 202501, nas 27 categorias |
| `/localidades/N1`, `N2` e `N3` | 1, 1 e 17 itens; código, nome e nível iguais aos de `/values` em 202501 |

Consequência: cada dimensão pode ser extraída sem baixar um mês de valores.

## Documentado por terceiros (não confirmado no IBGE)

- O SIDRA define `-` como zero absoluto, `X` como valor inibido, `..` como não se aplica e `...`
  como dado indisponível, segundo a documentação do pacote
  [sidrar](https://cran.r-project.org/web/packages/sidrar/vignettes/Introduction_to_sidrar.html).
  Atenção: a legenda geral diz "zero absoluto", mas os dados indicam atividade sem dado na UF
  (armadilha 2). Vale registrar esse confronto como uma decisão explícita.
- A API limitaria cada requisição a 100.000 valores, segundo o mesmo pacote. Uma competência tem
  3.078 valores, portanto a extração por mês fica bem abaixo desse limite.

## Hipóteses a confirmar

- A causa do HTTP 400 na consulta total é o limite de valores. A API não foi consultada sobre isso.
- O IBGE pode revisar valores já publicados, inclusive os dessazonalizados. Isso não foi medido e
  exige comparar cargas de datas diferentes.
