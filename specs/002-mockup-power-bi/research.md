# Research: Mockup do painel Power BI

Fonte das regras: `requisitos/pbi-mockup` (SKILL.md e referências). Números: warehouse em 2026-11-08.

## 1. Esqueleto (shell)

**Decision**: `canvas-topo-marca`. Ele tem uma barra superior de marca com navegação em abas (Capa e Análise), título com os dois carimbos de data, filtros
à direita, faixa de KPIs e área de visuais. As duas telas usam o mesmo esqueleto, com a mesma navegação, tipografia e cores.

**Rationale**: a marca do Observatório e a navegação entre duas telas pedem uma barra superior. O perfil é um só: analistas que consomem as telas prontas.
A tabela de esqueletos do `pbi-mockup` indica `topo-marca` para visão institucional com poucas telas.

**Alternatives considered**: `left-rail` (o padrão "de segurança", que o próprio `pbi-mockup` desaconselha sem um motivo); `escuro-ranking` (tema escuro, que
não é o do Observatório); `hero-banner` (bom para a capa, mas obrigaria trocar de esqueleto entre as telas).

## 2. Cores

**Decision**:
- Cor de ação: `#0E4194`, o `tableAccent` do tema do Observatório. Ela passa no contraste com texto branco pequeno.
- Neutros e tamanhos: os do `pbi-mockup`.
- Semânticas, nas marcas gráficas: `#0CA30C` e `#D03B3B`, do tema. Em texto pequeno, o sinal (+ ou −) e a seta acompanham o número em `#33394C`.

**Rationale**: mockup e painel devem usar os mesmos tokens. O verde do tema tem contraste de cerca de 3:1 com o branco, o que não basta para texto pequeno (SC-004).

## 3. Visuais da análise e a regra antirredundância

**Decision**: a tela de análise tem 5 visuais.

| Bloco | Grade | Visual | História | Status no Power BI |
|---|---|---|---|---|
| kpi-1 | 4 colunas | Atividade líder: nome, índice e diferença para a média | `kpi` | Cartão (novo) ✅ |
| kpi-2 | 4 colunas | Média das atividades da UF, com o número de atividades com dado | `kpi` | Cartão ✅ |
| kpi-3 | 4 colunas | Atividades acima da média (5 de 11) | `kpi` | Cartão ✅ |
| visual-principal | 8 colunas | Índice de produção por atividade: barras ordenadas, top 3 na cor de ação e linha da média | `ranking` + `comparar-categorias` | Barra agrupada com linha constante ✅ |
| visual-1 | 4 colunas | Média das atividades por mês, em 2025, com o mês selecionado em destaque | `tendencia` (suporte) | Linha ✅ |

**Rationale**: o contrato atual tinha dois gráficos de barras, o top 3 e a diferença para a média. Os dois decompõem o **mesmo índice pela mesma atividade**,
e a ordem é idêntica, porque a diferença é o índice menos uma média constante. A regra antirredundância do `pbi-mockup` manda fundir. Um só gráfico com todas
as atividades, o top 3 destacado e a linha da média responde às duas perguntas e libera espaço. A linha de tendência fica como suporte, à direita, porque
o ponto da tela é o estado do mês, e não a evolução.

**Alternatives considered**: manter os dois gráficos de barras (redundantes); fazer barras divergentes da diferença (mostram a distância para a média, mas
escondem o índice, que é o pedido da prova).

## 4. Nomes longos de atividade

**Decision**: o rótulo é "CNAE + nome", truncado com reticências em cerca de 34 caracteres, como o Power BI faz no eixo de categorias. O nome completo
aparece na dica do visual no painel. O cartão da atividade líder mostra o nome completo, em duas linhas se preciso.

**Rationale**: o maior nome tem 87 caracteres (3.15, couros e calçados). Criar uma coluna de nome curto mudaria o modelo da feature 001, sem necessidade.

## 5. Números reais

**Decision**: todos os números saem de `mockup/dados-referencia.sql`, executado no warehouse. O conferidor (`mockup/conferir_mockup.py`) executa a mesma
consulta e verifica se cada valor aparece no SVG correspondente. Há uma exceção: as alturas e os comprimentos das barras são geometria, calculada a partir
dos valores.

**Rationale**: SC-001 exige 100% de igualdade, e a constituição exige dados medidos. O `pbi-mockup` usa dados fictícios porque costuma vir antes dos dados.
O desvio fica registrado no racional, e o selo do rodapé informa a data dos números.

## 6. Verificações

**Decision**:
- `mockup/ferramentas/check_bounds.py`, cópia sem alterações do `pbi-mockup`, roda nas duas telas e precisa terminar sem erros nem colisões.
- Um teste com `xml.etree` confirma que o XML é bem formado e que não há `<use>`, `<symbol>` nem `currentColor`.
- Os scripts rodam na imagem `pim-pf-ingestao:1.0`, com a pasta `mockup/` montada.

**Rationale**: o validador só usa a biblioteca padrão, e o ambiente do projeto já tem Python 3.12. Assim não entra nenhuma dependência nova.

## 7. Imagem para o README

**Decision**: o README referencia `mockup/tela-02-analise.svg` diretamente. O GitHub exibe SVG em Markdown.

**Rationale**: dispensa uma ferramenta para converter em PNG. A fonte Segoe UI pode não existir no visualizador, e por isso o SVG declara as alternativas
`system-ui` e `sans-serif`, como no `pbi-mockup`.

## 8. Ajuste do painel ao mockup

**Decision**:
- O gerador do PBIP passa a ser versionado em `powerbi/ferramentas/gerar_pbip.py` e é atualizado para o layout do mockup.
- Medidas novas: "Atividade líder" (com índice e diferença), "Atividades com dado", "Cor do ranking" (top 3 na cor de ação) e "Insight do líder" (subtítulo).
- O PBIP é regerado e validado contra os esquemas oficiais.
- O contrato `specs/001-pipeline-pim-pf/contracts/painel.md` é atualizado.

**Rationale**: FR-017. Regerar a partir de um script versionado é reproduzível e explicável.

**Risco**: dois recursos do PBIR não são verificáveis sem o Desktop: a linha constante no gráfico de barras e o subtítulo com formatação condicional. Se
algum não abrir, o racional registra a alternativa nativa: uma série de linha com a média, em um gráfico de combinação, e um subtítulo estático.

## 9. Filtros

**Decision**: UF e mês, como pílulas discretas à direita do título. O mês selecionado fica destacado na cor de ação a 12%, e a ordem é mês-ano ("Jan/2025").
Não há botão "Limpar", porque os dois filtros aceitam uma seleção por vez e nunca ficam vazios.

**Rationale**: o `pbi-mockup` exige filtros com função clara e proíbe filtros de preenchimento. Cada filtro aqui corresponde a uma dimensão real da pergunta.
