# Feature Specification: Pipeline da PIM-PF, da extração ao painel analítico

**Feature Branch**: nenhuma criada por este comando (trabalho na branch atual)

**Created**: 2026-11-07

**Status**: Draft

**Input**: User description: "requisitos\case.docx e requisitos\decisoes.md"

## Clarifications

### Session 2026-11-07

- Q: O que a extração faz quando ninguém informa o período? → A: Todo o histórico na primeira carga; depois, os últimos 3 meses publicados, com parâmetro de até 2 anos.
- Q: O que fazem os endpoints por tabela? → A: Acionam a extração só daquela tabela; os dados continuam sendo lidos por SQL.
- Q: O que acontece quando um teste de dados reprova? → A: O lote é validado na área de carga antes de publicar, e uma reprovação ali mantém os dados anteriores. Testes sobre o resultado publicado rodam depois e tornam a falha visível.

## User Scenarios & Testing *(mandatory)*

Os códigos entre parênteses, como (I2), são os IDs de `docs/prova-requisitos.md`. As histórias seguem a
ordem das features definidas pelo candidato. Cada uma entrega valor e pode ser testada isoladamente.

### User Story 1 - Extrair a PIM-PF para a área de carga (Priority: P1)

Como engenheiro de dados, quero extrair os dados da tabela 8888 do IBGE, tratá-los e deixá-los disponíveis
em quatro tabelas (variáveis, território, categoria e produção física), com origem e data de carga, para
que as etapas seguintes partam de dados confiáveis e rastreáveis.

**Why this priority**: sem os dados, nenhuma outra etapa existe. É o início de todo o fluxo (I1, I2, T1).

**Independent Test**: executar a extração diretamente, com a fonte real ou simulada, e consultar as quatro
tabelas da área de carga, conferindo contagens e metadados.

**Acceptance Scenarios**:

1. **Dado** um ambiente sem dados, **Quando** a primeira carga termina, **Então** as quatro tabelas estão
   preenchidas, e cada linha informa o caminho de origem e a data de carga.
2. **Dado** um período já carregado e sem mudança na fonte, **Quando** a extração é repetida, **Então** o
   estado final é o mesmo, sem linhas duplicadas.
3. **Dado** uma falha temporária da fonte, **Quando** a extração está em andamento, **Então** o sistema tenta
   de novo dentro de um limite de tempo e conclui sem intervenção, se a fonte se recuperar.
4. **Dado** uma resposta com estrutura ou símbolo desconhecido, **Quando** ela é validada, **Então** a carga é
   interrompida com a causa registrada, e os dados já publicados não mudam.
5. **Dado** um período já baixado, **Quando** se pede o reprocessamento, **Então** a área de carga é refeita a
   partir do dado bruto guardado, sem chamar a fonte.

---

### User Story 2 - Acionar e acompanhar a ingestão por uma API (Priority: P2)

Como operador do pipeline, quero acionar a extração por um único ponto de entrada, escolhendo o período e a
tabela, e consultar o status da carga, para não depender do acesso direto ao código ou ao contêiner.

**Why this priority**: é o ponto de entrada que a orquestração usa, mas a extração funciona sem ele. A prova
não exige uma API: ela é uma decisão do candidato, justificada por isolar a ingestão atrás de um contrato único.

**Independent Test**: fazer chamadas à API com a extração simulada, cobrindo pedido válido, período inválido,
pedido repetido durante uma execução e consulta de status.

**Acceptance Scenarios**:

1. **Dado** um período válido, **Quando** o operador pede a extração, **Então** recebe logo um identificador de
   execução, sem esperar a carga terminar.
2. **Dado** um identificador de execução, **Quando** o operador consulta o status, **Então** vê a situação, os
   períodos e as linhas processadas e, em caso de falha, a causa resumida.
3. **Dado** um período inválido ou início depois do fim, **Quando** o operador pede a extração, **Então** o pedido
   é recusado com uma mensagem clara, e nada é executado.
4. **Dado** uma execução em andamento, **Quando** chega outro pedido para o mesmo escopo, **Então** ele é recusado,
   e a execução em andamento continua.
5. **Dado** cada uma das quatro tabelas, **Quando** o operador usa o endpoint dela, **Então** a operação definida em
   FR-012 é realizada somente para essa tabela.

---

### User Story 3 - Publicar o modelo analítico e responder às perguntas da prova (Priority: P1)

Como estatístico, quero um modelo em fato e dimensões com uma estrutura consultável via SQL que traga, por UF,
mês e atividade da Indústria de Transformação em 2025, o índice, a média e a diferença para a média, além das 3
atividades de maior índice, para acompanhar o comportamento do setor (A1 a A5, S1, S2).

**Why this priority**: é o resultado que a prova cobra diretamente. A prioridade é P1, apesar da ordem das features.

**Independent Test**: carregar a área de carga com dados de exemplo, executar a transformação e comparar a
estrutura analítica e a consulta com os valores esperados, incluindo o caso conferido à mão do Ceará.

**Acceptance Scenarios**:

1. **Dado** a área de carga preenchida, **Quando** a transformação termina, **Então** as cinco tabelas do modelo
   estão disponíveis, com integridade entre o fato e as dimensões, além do caminho de origem e da data de carga.
2. **Dado** Ceará em 01/2025, **Quando** a estrutura analítica é consultada, **Então** a média é 101,58012, e a
   diferença de cada atividade é o seu índice menos essa média.
3. **Dado** cada UF e mês de 2025, **Quando** a consulta do top 3 é executada, **Então** ela retorna exatamente 3
   atividades, em ordem de índice, com desempate determinístico.
4. **Dado** uma atividade com símbolo em vez de número, **Quando** a média é calculada, **Então** ela fica fora
   do cálculo, sem contar como zero.
5. **Dado** uma falha na transformação ou um lote reprovado na validação antes de publicar, **Quando** a execução termina,
   **Então** a falha fica visível, e os consumidores continuam vendo os últimos dados válidos.
6. **Dado** um teste reprovado sobre o resultado já publicado, **Quando** a execução termina, **Então** a execução aparece
   como falha no orquestrador, para o problema ser corrigido e o período reprocessado.

---

### User Story 4 - Executar tudo de forma agendada e reproduzível (Priority: P1)

Como engenheiro de dados, quero subir o ambiente completo com um único comando e ter a ingestão e a transformação
executadas em ordem por um orquestrador agendado, para que novas publicações do IBGE cheguem sem ação manual
(C1 a C4, O1, I3).

**Why this priority**: é a Questão 3 da prova, que exige ambiente em contêineres e orquestração.

**Independent Test**: partir de um clone limpo, seguir o README, disparar o fluxo pelo orquestrador e confirmar
que todas as etapas terminam com sucesso, nos dados e na interface do orquestrador.

**Acceptance Scenarios**:

1. **Dado** um clone limpo e a configuração de exemplo, **Quando** o ambiente é iniciado conforme o README, **Então**
   todos os serviços ficam saudáveis, sem passos manuais não documentados.
2. **Dado** o agendamento ativo e nenhuma novidade na fonte, **Quando** a execução ocorre, **Então** ela termina sem
   recarregar dados.
3. **Dado** uma nova publicação na fonte, **Quando** a execução agendada ocorre, **Então** ingestão, transformação e
   testes rodam nessa ordem, e o modelo passa a refletir a novidade.
4. **Dado** uma falha em uma etapa, **Quando** as tentativas se esgotam, **Então** as etapas seguintes não rodam, e a
   falha aparece no orquestrador.
5. **Dado** uma execução em andamento, **Quando** chega o próximo horário, **Então** não há duas execuções simultâneas.

---

### User Story 5 - Analisar os resultados em um painel (Priority: P3)

Como analista ou pessoa da área de negócio, quero um painel com uma capa e uma tela de análise, para ver os
indicadores da Indústria de Transformação sem escrever SQL.

**Why this priority**: amplia o uso dos dados, mas não é exigido pela prova. Justifica-se porque o enunciado cita
analistas e equipes de negócio como consumidores, e o pipeline não depende dele.

**Independent Test**: abrir o painel com o modelo publicado, filtrar por UF e mês e comparar os números com o
resultado da consulta SQL.

**Acceptance Scenarios**:

1. **Dado** o painel aberto, **Quando** o usuário navega, **Então** encontra apenas duas telas: capa e análise.
2. **Dado** uma UF e um mês selecionados, **Quando** a tela de análise é atualizada, **Então** mostra o índice, a média,
   a diferença e o top 3, iguais aos da consulta SQL.
3. **Dado** uma atividade sem dado na UF, **Quando** ela seria exibida, **Então** não aparece como zero.

---

### Edge Cases

- **Mês parcial**: 202609 tem números só para o Brasil, e as demais localidades trazem `...`. O mês é carregado,
  sinalizado como parcial e carregado de novo quando a fonte o completar.
- **Revisão de mês publicado**: a data de modificação da fonte vale para a tabela inteira, então só o conteúdo
  de cada mês indica o que mudou.
- **Símbolos**: `-` e `...` têm tratamentos registrados. Um símbolo fora da lista conhecida interrompe a carga.
- **Consulta de todos os períodos**: a fonte recusa com HTTP 400, então a extração é feita mês a mês.
- **Agregado "3 Indústrias de transformação"**: fica fora da média e do ranking. A atividade 3.20, de código fora de
  sequência, fica dentro.
- **Menos atividades**: Mato Grosso do Sul e Rio Grande do Norte têm só 3 atividades com valor; o top 3 lista todas.
  Menos de 3 atividades em uma UF e mês de 2025 faz os testes de dados falharem.
- **Valores extremos**: variações de até 11.126.974,6% são legítimas e precisam caber no tipo do campo.
- **Fonte indisponível além das tentativas**: a execução falha, com os dados publicados intactos.
- **Período pedido que a fonte não tem**: o pedido é recusado, ou o status informa quais meses não existem.
- **Mudança de variáveis, categorias ou territórios nos metadados**: a validação falha cedo, com alerta de mudança na fonte.

## Requirements *(mandatory)*

### Functional Requirements

**Ingestão e área de carga**

- **FR-001**: O sistema MUST extrair automaticamente, da tabela 8888, todas as variáveis, categorias e territórios dos
  períodos solicitados, e também os metadados que descrevem esses itens (I1, I2).
- **FR-002**: Sem período informado, o sistema MUST extrair todo o histórico na primeira carga e, nas seguintes, os últimos 3
  meses publicados. O sistema MUST aceitar como parâmetro um intervalo de até 2 anos e oferecer uma carga completa manual, para
  revisões fora dessa janela (I2, I3, I9).
- **FR-003**: O sistema MUST guardar a resposta original da fonte sem alteração, identificada por origem, período e data
  de ingestão, organizada por período e versão (I4 a I8; Princípio IV).
- **FR-004**: O sistema MUST detectar pelo conteúdo quais meses mudaram, e não apenas pela data informada pela fonte (I3, I9).
- **FR-005**: O sistema MUST permitir o reprocessamento de períodos a partir do dado bruto guardado, sem acessar a fonte (I10).
- **FR-006**: O sistema MUST tratar os dados antes da área de carga: padronizar os nomes, definir os tipos, converter
  símbolos por regra explícita, preservar o símbolo original e remover duplicidades, registrando a contagem (T1 a T6).
- **FR-007**: O sistema MUST interromper a carga antes da área de carga diante de uma linha inválida ou de um símbolo
  desconhecido, registrando a causa (T2, T5).
- **FR-008**: O sistema MUST disponibilizar as quatro tabelas da área de carga, com caminho de origem e data de carga em
  cada linha (I7, I8).
- **FR-009**: As chamadas à fonte MUST ter tempo limite e novas tentativas com espera crescente, somente para falhas
  temporárias, e as respostas MUST ser validadas em estrutura e quantidade de linhas.

**API de ingestão**

- **FR-010**: O sistema MUST oferecer uma API como único ponto de entrada da ingestão, com o período informado por campos
  de data validados, na granularidade mensal da fonte.
- **FR-011**: A API MUST aceitar o pedido sem esperar o fim da carga, devolver um identificador de execução, informar o
  status e recusar execuções simultâneas do mesmo escopo.
- **FR-012**: A API MUST ter um endpoint para cada uma das quatro tabelas, que aciona a extração só daquela tabela. Os dados
  continuam sendo lidos por SQL. A extração da produção física MUST carregar também os metadados, para manter a integridade do modelo.
- **FR-013**: A API MUST informar se está saudável e MUST NOT expor detalhes internos nas mensagens de erro.

**Modelo analítico**

- **FR-014**: O sistema MUST transformar a área de carga em cinco tabelas analíticas: quatro dimensões e um fato, com
  integridade garantida pelo banco, além do caminho de origem e da data de carga em cada uma.
- **FR-015**: A publicação MUST ser idempotente e atômica por tabela, depois de validar o lote: repetir a carga não duplica dados,
  e uma falha na carga ou na validação prévia mantém os últimos dados válidos disponíveis (I9).
- **FR-016**: O sistema MUST publicar uma estrutura consultável via SQL no grão UF × mês × atividade da Indústria de
  Transformação, restrita a 2025 e ao Número-índice (2022=100), com índice, média das atividades da UF no mês e
  diferença (A1 a A5).
- **FR-017**: O sistema MUST fornecer uma consulta SQL, baseada nessa estrutura, com as 3 atividades de maior índice por UF e
  mês de 2025, com desempate determinístico (S1, S2).
- **FR-018**: Atividades sem valor numérico MUST ficar fora da média e do ranking, e nunca valer zero (T5).
- **FR-019**: A atividade MUST ser identificada pelo padrão da classificação `3.NN`, nunca por faixa de códigos.
- **FR-020**: Testes automatizados de dados MUST cobrir unicidade, integridade, 17 UFs e 12 meses em 2025, soma das diferenças
  próxima de zero por UF e mês e ao menos 3 atividades por UF e mês.

**Ambiente e orquestração**

- **FR-021**: Um único comando documentado MUST iniciar todos os serviços e dependências, com configurações reproduzíveis e
  sem segredos no repositório (C1, C2, C4).
- **FR-022**: Cada serviço MUST expor somente as portas de uso externo, com finalidade documentada.
- **FR-023**: O sistema MUST disponibilizar um orquestrador (C3) com um fluxo agendado (O1) que acione a ingestão pela API,
  aguarde o resultado e então execute a transformação e os testes, nessa ordem.
- **FR-024**: O fluxo MUST impedir execuções simultâneas, repetir etapas com falhas temporárias e aceitar disparo manual com
  período e modo de reprocessamento como parâmetros (I9, I10).
- **FR-025**: O fluxo MUST verificar novidades ao menos uma vez por dia e encerrar sem recarregar quando não houver (I3).

**Painel**

- **FR-026**: O sistema MUST incluir um painel com exatamente duas telas, capa e análise, que consuma apenas o modelo publicado,
  com acesso somente leitura.
- **FR-027**: A tela de análise MUST permitir filtrar por UF e mês e mostrar índice, média, diferença e top 3, com títulos que
  expressem a pergunta respondida por cada visual.
- **FR-028**: O painel MUST seguir a paleta visual do Observatório definida pelo candidato.

**Qualidade**

- **FR-029**: Testes automatizados, sem depender da fonte real, MUST cobrir as regras de extração, tratamento e API.
- **FR-030**: Cada execução MUST registrar período, linhas e nulos processados, além da causa de falhas, para diagnóstico sem
  acesso ao código.

### Key Entities *(include if feature involves data)*

- **Tabelas da área de carga** (`stage`): `variaveis`, `territorio`, `categoria` e `producao_fisica`, já tratadas, com caminho de
  origem e data de carga.
- **Dado bruto**: resposta original da fonte para um mês, com origem, data de ingestão e hash do conteúdo.
- **Controle de carga**: por mês, o hash, a situação, se está parcial e a execução que o carregou.
- **Execução de ingestão**: identificador, escopo pedido, situação, contagens e causa de falha.
- **`dim_territorio`**: Brasil, Nordeste e 17 UFs, com código, nome e nível (19 itens).
- **`dim_variaveis`**: as 6 variáveis, com código, nome e unidade.
- **`dim_categorias`**: as 27 categorias, com código, CNAE, nome e marca de atividade de transformação (24 marcadas).
- **`dim_calendario`**: uma linha por mês, cobrindo todos os períodos do fato. É gerada pelo modelo, e não pela fonte.
- **`fat_producao_fisica`**: grão território × mês × variável × categoria, com valor, símbolo original e metadados de origem.
- **Estrutura analítica de 2025**: atende a FR-016 e alimenta a consulta do top 3 e o painel.

## Success Criteria *(mandatory)*

### Measurable Outcomes

Os números abaixo foram medidos em 2026-11-07, em `docs/arquitetura/ARQUITETURA.md`. Revisões da fonte podem alterá-los, e nesse
caso o teste de aceite deve registrar a nova medição.

- **SC-001**: Uma pessoa nova no projeto coloca a solução em funcionamento a partir de um clone limpo, só com o README, em até 30
  minutos após baixar as dependências.
- **SC-002**: A cobertura dos dados é de 100%: as linhas por mês são iguais a territórios × variáveis × categorias (3.078), o que
  dava 914.166 linhas em 297 meses na medição.
- **SC-003**: Repetir qualquer carga, com a fonte igual, resulta em 0 linhas duplicadas e nenhuma diferença no estado final.
- **SC-004**: A estrutura analítica tem 2.004 linhas, e o top 3 tem 612 (17 UFs × 12 meses × 3).
- **SC-005**: Em Ceará, 01/2025, a média é 101,58012, e o top 3 é 3.13 Têxteis (145,03), 3.24 Metalurgia (136,56) e 3.11 Bebidas (120,05).
- **SC-006**: Reprocessar um período publicado termina com sucesso sem nenhum acesso à fonte.
- **SC-007**: O operador recebe a confirmação de um pedido de extração em até 5 segundos, mesmo em uma carga completa.
- **SC-008**: Em 100% das falhas simuladas antes da publicação (fonte fora do ar, linha inválida, lote reprovado na validação), os dados publicados continuam iguais aos anteriores. Em 100% dos testes reprovados depois da publicação, a execução aparece como falha.
- **SC-009**: Falhas temporárias simuladas da fonte são superadas sem intervenção humana em 100% dos casos dentro do limite de tentativas.
- **SC-010**: Um analista encontra o top 3 de uma UF e um mês no painel em menos de 1 minuto, e os números são 100% iguais aos da consulta SQL.
- **SC-011**: Todos os requisitos da Questão 2 e da Questão 3 estão ligados a um componente e a uma forma de verificação.

## Assumptions

- **Tratamento antes da área de carga**: a prova exige o tratamento em Python e/ou PySpark (T1), então ele ocorre na ingestão. A etapa
  seguinte só modela os dados, embora `decisoes.md` possa ser lido como deixando o tratamento para ela.
- **Dado bruto preservado**: `decisoes.md` não cita arquivos brutos, mas o Princípio IV da constituição e os itens I4 a I10 da prova os
  exigem. Esta spec mantém esse armazenamento.
- **"Últimos meses"**: refere-se aos últimos períodos publicados na fonte, e não ao calendário.
- **Limite de 2 anos**: vale para o intervalo pedido por parâmetro, não para a carga completa. A extração é mês a mês, então o limite não vem da fonte.
- **Símbolos**: `-` e `...` viram nulo, com o símbolo preservado (ADR 0004).
- **Territórios**: a fonte traz 17 UFs, Brasil e Nordeste. Todos são carregados, e a estrutura analítica usa só as UFs.
- **Sem quarentena**: uma linha inválida interrompe a carga, como já decidido na arquitetura.
- **Código existente**: o pipeline atual serve de base e será adaptado ao novo desenho. A decisão de reaproveitar é do plano.
- **Nomes do modelo**: `decisoes.md` substitui os nomes do ADR 0010 (`dw`, `d*`, `f*`). O plano MUST registrar essa mudança em um novo ADR.
- **Acesso local**: a API não tem autenticação porque roda em um ambiente local de avaliação; isso fica documentado como ajuste para produção.
- **Painel**: abre no aplicativo de desktop para Windows, fora dos contêineres, e sua verificação é manual.
- **Fora do escopo**: respostas da Questão 1 (são do candidato), envio do zip, lakehouse em camadas e PySpark.
- **Dependência**: disponibilidade das APIs públicas do IBGE, cujo comportamento está em `docs/fonte-sidra-8888.md`.

## Restrições de tecnologia definidas pelo candidato

Estas escolhas vêm da prova e de `decisoes.md`. Ficam aqui, fora dos requisitos, para orientar o plano.

| Tema | Definição |
|---|---|
| Linguagem e bibliotecas | Python, com `requests` na extração e `pandas` no tratamento |
| API | FastAPI, no mesmo contêiner da ingestão, com só a porta da API exposta nesse contêiner |
| Banco | PostgreSQL em contêiner próprio, com os schemas `stage` e `warehouse` criados de início |
| Transformação | dbt em contêiner próprio, ligado à `stage` e gravando na `warehouse` |
| Orquestração | Apache Airflow em contêiner: ingestão via API, e dbt por comando em `DockerOperator` |
| Ambiente | Docker Compose para todos os contêineres |
| Painel | Power BI em formato PBIP, com fundo em SVG e o tema `tema_powerbi_fiec_observatorio.json` |

Dois pontos para o plano:

- O `DockerOperator` costuma exigir o socket do Docker, o que requer um ADR pela constituição.
- `requisitos/` está no `.gitignore`, então uma cópia do tema MUST ser versionada junto com o painel para entrar no zip de entrega.
