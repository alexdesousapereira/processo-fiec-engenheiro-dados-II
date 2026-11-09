# Feature Specification: Mockup do painel Power BI

**Feature Branch**: nenhuma criada por este comando (trabalho na branch atual, `main`)

**Created**: 2026-11-08

**Status**: Draft

**Input**: User description: "mockup para power bi"

## Clarifications

### Session 2026-11-08

- Q: Em que formato o mockup deve ser entregue? → A: Conforme `requisitos/pbi-mockup`: uma imagem vetorial estática por tela, no canvas do Power BI, mais um índice navegável com todas as telas e um racional das decisões de cada visual. É mockup, não protótipo clicável.
- Q: O mockup é a referência que o painel deve seguir, ou uma entrega independente? → A: Conforme `requisitos/pbi-mockup`: é a referência validada antes do desenvolvimento do painel. O painel e o seu contrato passam a seguir o mockup.
- Q: Depois que o Power BI calcular o top 3 em DAX, o que acontece com a view `vw_top3_transformacao_2025`? → A: A estrutura analítica passa a ser a tabela `warehouse.fato_producao_fisica_industrial_2025`. O dbt mantém uma só view, `vw_top3_transformacao_2025`, que lê dessa tabela e responde à pergunta do top 3; a `vw_transformacao_2025` foi removida, porque a tabela já tem a média e a diferença. O painel importa só a tabela e as dimensões, calcula o top 3, a líder e as cores em DAX, e guarda todas as medidas numa tabela de medidas.

### Session 2026-11-09

- Q: Sem a `meses_linha`, como o gráfico de linha deve continuar mostrando os 12 meses e o subtítulo continuar citando o mês selecionado? → A: O rótulo curto do mês (`mes_curto`: jan, fev…) entra na `dim_calendario` do dbt, e a linha usa `dim_calendario[mes_curto]`, com a interação do filtro de mês desligada para ela. O insight da linha sai do subtítulo do visual e vira um cartão de texto sem moldura no mesmo lugar, que recebe o filtro de mês. A tabela `meses_linha` e o `TREATAS` saem do modelo.

## User Scenarios & Testing *(mandatory)*

Contexto: a feature 001 entregou o painel em duas telas (capa e análise), mas ele foi gerado fora do Power BI Desktop e ainda não
foi aberto (T064). O mockup define como o painel deve ficar, seguindo as regras de visualização de `requisitos/pbi-mockup`, e o painel
é ajustado a ele.

### User Story 1 - Validar o desenho do painel antes de construí-lo (Priority: P1)

Como candidato, quero ver as duas telas do painel com o layout, os títulos, as cores e os números do caso de referência, para aprovar
o desenho antes de ajustar o painel no Power BI.

**Why this priority**: o painel nunca foi visto renderizado, e mudar o desenho é barato no mockup e caro no painel.

**Independent Test**: abrir o índice do mockup em um navegador, sem nenhum software de BI, e percorrer as duas telas.

**Acceptance Scenarios**:

1. **Dado** o índice aberto, **Quando** o candidato percorre as telas, **Então** encontra exatamente duas: capa e análise.
2. **Dado** a tela de análise, **Quando** ela mostra Ceará em janeiro de 2025, **Então** a média é 101,58, e o top 3 é 3.13 Têxteis
   (145,03), 3.24 Metalurgia (136,56) e 3.11 Bebidas (120,05).
3. **Dado** qualquer número exibido, **Quando** ele é comparado com a consulta ao warehouse, **Então** os dois são iguais.
4. **Dado** cada visual, **Quando** o candidato lê o racional, **Então** encontra o gráfico escolhido, o motivo e se ele é nativo do Power BI.

---

### User Story 2 - Ajustar o painel ao mockup (Priority: P2)

Como candidato, quero que cada visual do mockup indique o campo ou a medida que usa, e que o painel seja corrigido para ficar igual
ao mockup, para que o resultado no Power BI seja o desenho aprovado.

**Why this priority**: transforma o mockup em painel. Depende do mockup aprovado na história 1.

**Independent Test**: comparar visual a visual o painel com o mockup e verificar se cada diferença foi corrigida ou registrada.

**Acceptance Scenarios**:

1. **Dado** um visual do mockup, **Quando** o candidato consulta o racional, **Então** encontra o nome do campo ou da medida e o filtro aplicado.
2. **Dado** o painel aberto no Desktop, **Quando** o candidato o compara com o mockup, **Então** cada diferença foi corrigida no painel ou está
   registrada com o motivo, e o contrato do painel reflete o mockup.

---

### User Story 3 - Mostrar o painel na entrevista (Priority: P3)

Como candidato, quero uma imagem do painel para apresentar na entrevista e no README, mesmo sem o Power BI instalado na máquina do avaliador.

**Why this priority**: a prova não exige o painel, mas ele faz parte da solução apresentada.

**Independent Test**: abrir a imagem em qualquer visualizador e reconhecer as duas telas.

**Acceptance Scenarios**:

1. **Dado** o README, **Quando** o avaliador o lê, **Então** vê a tela de análise sem precisar de outro software.

---

### Edge Cases

- **Atividade sem dado na UF**: não aparece no mockup nem é desenhada como zero, como no painel.
- **UF com só 3 atividades**, como Mato Grosso do Sul: o top 3 mostra as 3, e as barras de diferença mostram só essas.
- **Nomes longos de atividades**: precisam caber no visual sem ultrapassar a moldura, com quebra de linha ou abreviação documentada no racional.
- **Mês selecionado no filtro**: o gráfico de linha continua com os 12 meses, porque a interação do filtro de mês com ele é desligada; o insight da linha, em cartão de texto à parte, cita o mês selecionado.
- **Valores negativos na diferença**: distinguíveis por sinal e rótulo, e não só pela cor, e legíveis em escala de cinza.
- **Dados revisados pela fonte**: se os números do warehouse mudarem, o mockup indica a data de referência dos valores mostrados.
- **Regra de `requisitos/pbi-mockup` que não se aplica ao projeto**: segue-se a regra do projeto, com o desvio registrado no racional, como o uso de dados reais.

## Requirements *(mandatory)*

### Functional Requirements

**Conteúdo**

- **FR-001**: O mockup MUST representar as duas telas definidas para o painel, capa e análise, sem acrescentar telas.
- **FR-002**: O mockup MUST ter uma imagem vetorial estática por tela, no tamanho de tela do Power BI (1280 × 720, 16:9), um índice navegável
  com todas as telas e um racional das decisões. Não é um protótipo clicável.
- **FR-003**: Todo número exibido MUST vir do warehouse publicado, no caso de referência Ceará e janeiro de 2025, e nunca ser inventado.
- **FR-004**: Cada tela MUST mostrar, perto do título, a data de referência dos dados e a data de atualização.
- **FR-005**: O mockup MUST usar a paleta, as fontes e as cores do tema do Observatório. A cor de destaque marca só o item que o insight cita.
- **FR-006**: O título da tela MUST expressar a pergunta respondida. O título de cada visual MUST ser descritivo, e o insight MUST ficar em um subtítulo.
- **FR-007**: Acima e abaixo da média MUST ser distinguíveis por sinal ou rótulo numérico, além da cor, e cada visual MUST continuar legível em escala de cinza.
- **FR-008**: Cada visual MUST indicar, no racional, o campo ou a medida, o filtro, o tipo de gráfico, o motivo da escolha e se o visual é nativo do Power BI.
- **FR-009**: O mockup MUST usar só visuais nativos do Power BI, salvo escolha em contrário registrada no racional.
- **FR-010**: Os gráficos MUST seguir as regras de `requisitos/pbi-mockup`: barras começando no zero, sem 3D nem velocímetro, legenda no
  canto superior esquerdo, rótulos amigáveis e um único nome para cada medida em todas as telas.
- **FR-011**: Os filtros MUST ser discretos e ter função clara. A seleção de mês MUST ser por mês, nunca por intervalo livre de datas.
- **FR-012**: O rodapé de cada tela MUST trazer a fonte dos dados e um selo de mockup com a data de referência dos valores.

**Construção e validação**

- **FR-013**: Cada tela MUST seguir uma grade única de 12 colunas, com margem e espaçamento constantes, e nenhum elemento MUST ultrapassar a moldura do seu visual nem sobrepor outro visual.
- **FR-014**: A geometria de cada tela MUST ser verificada automaticamente, conforme `requisitos/pbi-mockup`, e só é aceita com zero erros e zero colisões.
- **FR-015**: Cada tela MUST ser editável, organizada em camadas nomeadas (fundo, cabeçalho, filtros, indicadores, visuais e rodapé), e abrir corretamente em ferramentas de design.
- **FR-016**: O mockup MUST ser versionado no repositório e abrir sem software de BI. A tela de análise MUST ter uma versão em imagem para o README (história 3).

**Painel**

- **FR-017**: O contrato do painel MUST ser atualizado para refletir o mockup aprovado, e o painel MUST ser ajustado a ele.
- **FR-018**: Toda diferença entre o painel aberto no Desktop e o mockup MUST ser corrigida no painel ou registrada com o motivo.
- **FR-019**: O painel MUST importar a tabela `fato_producao_fisica_industrial_2025` e as dimensões, e nenhuma view nem tabela criada só no Power BI, além da tabela `Medidas`; colunas de apoio ao visual, como o rótulo curto do mês, vêm das dimensões do dbt. As regras do painel (top 3 com desempate pelo código, atividade líder, cor do ranking e atividades acima da média) MUST ser medidas DAX, guardadas na tabela `Medidas`.

### Key Entities *(include if feature involves data)*

- **Tela**: capa ou análise, com título em forma de pergunta, datas de referência e de atualização, filtros e lista de visuais.
- **Visual**: tipo de gráfico, posição na grade, título descritivo, subtítulo de insight, campo ou medida, filtro, valores do caso de referência e status no Power BI.
- **Caso de referência**: Ceará, janeiro de 2025, com média, top 3 e diferenças conferidos no warehouse.
- **Racional**: registro, por visual, do gráfico escolhido, do motivo, dos anti-padrões recusados e dos desvios de `requisitos/pbi-mockup`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos números do mockup são iguais aos do warehouse na data de referência.
- **SC-002**: Uma pessoa que não conhece o projeto identifica, só pelo mockup, a atividade líder e a média do Ceará em janeiro de 2025 em menos de 1 minuto.
- **SC-003**: 100% dos visuais do mockup têm o gráfico, o motivo e o status no Power BI registrados no racional.
- **SC-004**: Todo texto do mockup tem contraste de pelo menos 4,5:1 com o fundo, ou de 3:1 em texto grande ou em negrito.
- **SC-005**: A verificação de geometria aponta zero erros e zero colisões em todas as telas.
- **SC-006**: O mockup abre em um navegador comum, sem instalar nada.
- **SC-007**: Depois da validação no Desktop, 100% das diferenças entre o painel e o mockup estão corrigidas ou registradas.

## Assumptions

- **Fonte das regras**: as regras de `requisitos/pbi-mockup` valem para esta feature. As regras aplicadas ficam registradas no racional; a pasta passou a ser versionada em 2026-11-09.
- **Telas**: as duas telas de `decisoes.md` são mantidas. Há um só perfil, analistas e estatísticos que só consomem as telas prontas, então não há uma tela por perfil.
- **Dados reais, e não fictícios**: `requisitos/pbi-mockup` usa dados ilustrativos porque o mockup costuma vir antes dos dados. Aqui o warehouse já existe, e a constituição exige dados medidos. O selo de mockup informa a data de referência, em vez de "dados ilustrativos".
- **Mudança de desenho**: onde as regras de `requisitos/pbi-mockup` divergirem do contrato atual do painel, prevalece o mockup. Exemplo: título de visual descritivo e insight no subtítulo.
- **Tema**: claro, com a paleta do tema do Observatório já versionado no painel.
- **Cor condicional**: o destaque por cor e o insight colorido já são usados no painel. Eles exigem medidas no modelo e ficam registrados no racional.
- **Dependência**: o warehouse da feature 001 precisa estar carregado para obter os números.

## Restrições definidas pelo candidato

| Tema | Definição |
|---|---|
| Regras e processo | `requisitos/pbi-mockup` (SKILL.md e referências) |
| Formato das telas | SVG estático por tela, 1280 × 720, com grupos nomeados, sem `<use>`, `<symbol>` ou `currentColor` |
| Índice | HTML navegável que embute os SVGs |
| Racional | Markdown com as decisões por visual |
| Verificação | `check_bounds.py` de `requisitos/pbi-mockup`, sem erros nem colisões |
