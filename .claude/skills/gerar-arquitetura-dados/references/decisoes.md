# Decisões que a arquitetura precisa responder

Use como roteiro, não como formulário. Pule o que não se aplica e diga por quê.

## Extração

- Como a extração se divide para respeitar os limites da fonte?
- Como tratar falhas parciais, timeouts e novas tentativas?
- O que define que uma carga terminou corretamente? Compare linhas recebidas e esperadas.
- A extração usa os metadados da fonte para descobrir dimensões, em vez de fixar códigos?

## Armazenamento

- Quantas camadas são de fato necessárias e o que cada uma garante?
- Qual formato em cada camada? O bruto preserva o que a fonte entregou?
- Qual a chave de partição? Ela combina com as consultas e evita muitos arquivos pequenos?
- Como cada registro identifica origem, requisição e data de ingestão?
- Sobrescrever ou versionar? Como auditar o que a fonte dizia em determinada data?

## Atualização e reprocessamento

- Como detectar novidades: período novo, data de modificação ou comparação de conteúdo?
- A fonte revisa dados já publicados? Qual janela precisa ser recarregada?
- Dados de um mesmo período chegam em etapas? Como não tratar um período parcial como concluído?
- Como reprocessar um período ou tudo sem duplicar? Qual a chave de idempotência?

## Tratamento

- Qual o grão e a chave natural de cada tabela?
- Qual o significado de cada símbolo ou valor especial? Ele vira nulo, zero ou uma categoria?
- O dado original é preservado ao lado do valor tratado?
- Como a padronização trata nomes, tipos, datas e casas decimais?
- Registros inválidos são descartados, corrigidos ou separados em quarentena?

## Camada analítica

- A tabela atende ao grão pedido? Agregados e totais estão excluídos dos cálculos?
- A regra de filtro usa um atributo estável, e não uma faixa de códigos?
- Como nulos afetam médias, diferenças e rankings?
- Como tratar empates? `RANK`, `DENSE_RANK` e `ROW_NUMBER` respondem a perguntas diferentes.
- O banco suporta a consulta exigida e sobe de forma simples no Compose?
- Colunas calculadas ficam na tabela ou em uma view? Por quê?

## Motor de processamento

- O volume medido exige processamento distribuído?
- Se a prova ou o time pede a ferramenta, como justificar seu uso sem exagerar a necessidade?
- Como o motor roda no Compose e quanta memória consome?

## Orquestração

- Qual a granularidade das tarefas? Cada uma pode ser repetida com segurança?
- Qual o agendamento, considerando o calendário de publicação da fonte?
- Como funcionam `catchup`, retries, alertas e passagem de parâmetros?
- Qual o papel dos sensores ou da verificação prévia de novidades?
- Como reprocessar um período a partir da interface do orquestrador?

## Qualidade e observabilidade

- Quais verificações bloqueiam a publicação e quais apenas alertam?
- Quais invariantes de negócio podem ser testados?
- Quais métricas ficam registradas por execução?

## Ambiente e entrega

- Quais serviços são indispensáveis? Cada contêiner a mais pesa na máquina de quem avalia.
- Versões estão fixadas? Um único comando sobe tudo a partir do README?
- Como os segredos são separados do código?
- O que entra no pacote de entrega, e o histórico do Git está incluído?
