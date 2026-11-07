# Prova Prática FIEC 7778 Constitution

## Core Principles

### I. A prova é a fonte dos requisitos

Todo componente MUST atender a um requisito de `docs/prova-requisitos.md`, citando seu ID.
Componentes sem requisito MUST ter justificativa escrita. Isso evita tanto lacunas na entrega
quanto excesso de engenharia.

### II. Toda decisão precisa ser defensável

Decisões de arquitetura MUST ser registradas com contexto, alternativas e consequências. O
candidato MUST conseguir explicar qualquer trecho na entrevista técnica, inclusive os feitos com
IA. Entre duas soluções que atendem à prova, MUST ser escolhida a mais fácil de defender.

### III. Decisões se baseiam em dados medidos

Afirmações sobre a fonte MUST vir de medição registrada em `docs/fonte-sidra-8888.md`. Hipóteses
MUST ser marcadas como hipóteses. Regras de negócio nunca assumem o significado de um símbolo ou
valor sem confronto com os dados.

### IV. Cargas são idempotentes e reprocessáveis

Repetir uma carga MUST produzir o mesmo estado final, sem duplicar dados. O dado bruto MUST ser
preservado sem alteração, com origem e data de ingestão, para que as camadas seguintes possam ser
reconstruídas a partir dele.

### V. O ambiente é reproduzível

A solução MUST rodar do zero em contêineres, seguindo o README e sem passos manuais não
documentados. Versões de imagens e dependências MUST ser fixadas. Testes automatizados MUST cobrir
as regras de transformação e as verificações de qualidade dos dados.

## Restrições

- Fonte: tabela 8888 do SIDRA/IBGE. Stack exigida: Python e/ou PySpark, SQL, Docker Compose e
  Apache Airflow.
- Segredos MUST NOT entrar no Git. Configurações locais usam `.env`, com `.env.example` versionado.
- O arquivo original da prova MUST NOT entrar no Git nem no zip de entrega.
- As respostas da Questão 1 MUST refletir a experiência real do candidato.

## Padrões de engenharia

Estes padrões aplicam os princípios acima às tecnologias do projeto. Valem para as tecnologias em
uso, e uma exceção MUST ter justificativa escrita no plano ou em um ADR. Nenhum padrão, sozinho,
justifica adicionar um componente: isso continua sujeito ao Princípio I.

### Python

- O código MUST rodar na versão de Python da imagem do projeto, nunca na versão local da máquina.
- A lógica MUST ficar em funções importáveis em `src/`, testáveis sem Airflow, API ou banco ativos.
- Funções MUST ter anotação de tipos nos parâmetros e no retorno.
- Registros de execução MUST usar `logging`, sem `print`, com contagens e identificação do período.
- Configurações MUST vir de variáveis de ambiente, sem URLs de banco ou credenciais no código.
- Exceções MUST NOT ser silenciadas: quem captura uma exceção a trata ou a relança com contexto.

### pandas

- Colunas MUST ter tipos explícitos, sem depender da inferência do pandas para códigos e valores.
- Valores da fonte MUST ser convertidos por regras explícitas. Conversões genéricas MUST NOT ocultar
  símbolos desconhecidos, como faz `errors="coerce"` sem verificação posterior.
- Transformações MUST ser vetorizadas. `iterrows` e `apply` linha a linha exigem justificativa.
- Funções de tratamento MUST receber e devolver DataFrames, sem acessar rede ou banco.
- O pico de memória MUST ser medido quando o volume mudar de ordem de grandeza.

### requests

- Toda chamada MUST definir `timeout` e verificar o status com `raise_for_status`.
- Chamadas MUST usar uma `Session` com novas tentativas e espera crescente, somente para falhas
  temporárias (429 e 5xx).
- Respostas MUST ser validadas quanto à estrutura e à quantidade de linhas antes de seguir no fluxo.
- Testes automatizados MUST NOT depender da API real: usam respostas simuladas.

### FastAPI

- Entradas e saídas MUST ter modelos Pydantic, com datas e períodos validados antes da execução.
- Operações longas MUST NOT prender a requisição: a API devolve `202` e um identificador de execução,
  e um endpoint informa o status.
- Execuções simultâneas do mesmo escopo MUST ser recusadas com `409`, para preservar o Princípio IV.
- Rotas MUST só validar e delegar para o código de `src/`, sem conter regra de negócio.
- A API MUST oferecer `/health` e usar códigos HTTP corretos, sem expor detalhes internos nos erros.
- Consultas que devolvem listas MUST ser paginadas.
- Testes MUST exercitar as rotas com `TestClient`, cobrindo sucesso, entrada inválida e falha.

### Docker

- Imagens MUST ter versão fixa, sem `latest`. Dependências Python MUST ter versão fixa ou seguir as
  constraints oficiais do Airflow.
- Contêineres MUST NOT guardar segredos na imagem nem exigir passos manuais não documentados.
- Serviços dependentes MUST esperar `healthcheck` do serviço de que dependem.
- Dados persistentes MUST ficar em volumes nomeados.
- O Compose MUST expor só as portas de uso externo, e cada porta publicada MUST ter finalidade
  documentada no README.
- O socket do Docker MUST NOT ser montado em um contêiner sem ADR que registre o risco e a alternativa
  considerada, pois ele dá controle sobre o host.

### Apache Airflow

- A DAG MUST conter só a ordem das tarefas e os parâmetros. A lógica fica em `src/`.
- O código no nível superior do arquivo da DAG MUST NOT acessar rede ou banco, pois o Airflow o
  executa a cada leitura.
- Tarefas MUST ser idempotentes, pois novas tentativas podem repeti-las.
- A DAG MUST definir `catchup`, `max_active_runs` e novas tentativas de forma explícita.
- Volumes de dados MUST NOT passar por XCom: tarefas trocam só referências e parâmetros.
- Conexões e segredos MUST vir de variáveis de ambiente ou conexões do Airflow, nunca do código.

### SQL e bancos de dados

- Valores externos MUST entrar em consultas como parâmetros, nunca por concatenação. Nomes de tabela e
  coluna montados dinamicamente MUST vir de constantes do código.
- A publicação no DW MUST ser transacional: uma falha deixa os consumidores com os dados anteriores.
- Integridade MUST ser garantida no banco, com chaves primárias e estrangeiras, além dos testes.
- Consultas publicadas MUST listar as colunas na projeção final, sem `SELECT *`.
- `ROW_NUMBER` e outras ordenações usadas em resultados MUST ter desempate determinístico.
- Médias e agregações MUST definir o tratamento de nulos, com a regra coberta por teste.
- Nomes de objetos MUST seguir `snake_case`, em português, com prefixos documentados.
- Modelos e consultas MUST ser versionados no Git, sem alterações manuais no banco em uso.

### PostgreSQL

- Schemas MUST separar responsabilidades, e os metadados do Airflow MUST ficar em um banco próprio.
- Colunas MUST usar o tipo adequado: `numeric` para valores exatos, `timestamptz` para instantes e
  `text` para textos sem limite de negócio.
- Cargas em volume MUST usar `COPY`, com upsert feito a partir da Stage.
- Índices MUST atender a consultas conhecidas, verificadas com `EXPLAIN`. Particionamento só entra com
  uma medição que o justifique.
- Consumidores analíticos, como o Power BI, MUST usar um usuário somente leitura.

## Fluxo de trabalho

1. Arquitetura com a skill `gerar-arquitetura-dados`.
2. Especificação, plano, tarefas e implementação com o Spec Kit.
3. Commits pequenos e descritivos, pois o histórico faz parte da entrega.
4. Registro de cada etapa em `docs/historico.md`.

## Governance

Esta constituição prevalece sobre outras práticas do projeto. Alterações MUST ser registradas em
`docs/historico.md` e seguir versionamento semântico: MAJOR para remover ou redefinir princípios,
MINOR para acrescentar, PATCH para ajustes de redação. Cada plano MUST verificar a conformidade com
estes princípios antes da implementação.

**Version**: 1.1.0 | **Ratified**: 2026-11-06 | **Last Amended**: 2026-11-07
