# ADR 0012: dbt em contêiner próprio, acionado pelo DockerOperator

**Status:** aceita, 2026-11-07. Substitui a parte do [ADR 0009](0009-dbt-da-stage-ao-dw.md) sobre o dbt rodar na imagem do Airflow.

## Contexto

O candidato definiu o dbt em um contêiner próprio, acionado pelo Airflow com `DockerOperator`. Esse operador cria contêineres pela API do
Docker, o que exige acesso ao socket `/var/run/docker.sock`. **Quem controla esse socket controla o Docker da máquina**, inclusive os
contêineres de outros projetos e a montagem de pastas do host. Por isso, a constituição exige este registro.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| `DockerOperator` com o socket só no scheduler | Separa as dependências; é o desenho definido; sem serviço extra | O scheduler passa a controlar o Docker da máquina |
| dbt na imagem do Airflow, em ambiente virtual, chamado por comando | Mais simples, sem socket; já foi testado | Contraria a decisão de manter o dbt em contêiner próprio |
| `DockerOperator` por um proxy do socket | Limita as chamadas à API do Docker | Um serviço a mais; criar contêineres continua permitido, então o risco diminui, mas não some; não confirmamos um tag estável |

## Decisão

- O socket é montado **somente** no `airflow-scheduler`, onde o LocalExecutor roda as tarefas. Confirmado: ele não aparece na API, no `dag-processor` nem na ingestão.
- A imagem `pim-pf-dbt:1.0` já contém o projeto, sem montar pastas do host, cujos caminhos variam no Docker Desktop.
- O serviço `dbt` do Compose executa `dbt --version` e encerra. Ele garante que a imagem exista antes de o scheduler subir.
- A senha do banco vai em `private_environment`, que o Airflow não mostra nos logs.

Medido no Docker Desktop 27.3.1: o socket é `root:root 660`, e o usuário da imagem do Airflow (`uid=50000`, `gid=0`) consegue ler e gravar, sem ajustar grupos.

## Consequências

- O risco é aceitável na avaliação local: a DAG é versionada, o Airflow só atende em `127.0.0.1`, e nenhum serviço externo chega ao scheduler.
- Qualquer DAG colocada nesse Airflow poderia controlar o Docker da máquina. Isso não seria aceitável em um ambiente compartilhado.
- Em produção, a troca seria por um executor em Kubernetes, que cria pods com permissões próprias, ou no mínimo por um proxy com a API restrita.
- A rede `pim_pf_rede` tem nome fixo, porque o operador entra nela pelo nome.
- A imagem do Airflow ficou sem pandas nem dbt, e a DAG não depende do projeto dbt no scheduler.
