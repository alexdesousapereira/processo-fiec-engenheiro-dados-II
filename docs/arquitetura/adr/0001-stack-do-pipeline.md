# ADR 0001: Stack do pipeline

**Status:** proposta, 2026-11-06. Revisada no mesmo dia: pandas no cenário atual, Spark na proposta futura.

## Contexto

A prova exige Python, SQL, Docker Compose e Airflow. O título da Questão 2 cita "Python e PySpark", mas o
enunciado do tratamento aceita "Python e/ou PySpark". A solução precisa rodar na máquina de quem avalia.

Medição do volume total (uma competência real de 3.078 linhas repetida 297 vezes, totalizando 914.166 linhas,
com pandas 3.1.1):

| Medida | Resultado |
|---|---|
| Pico de memória do processo | 343 MB |
| Tratamento: nomes, tipos, símbolos e duplicidades | 1,3 s |
| Escrita em Parquet | 6,7 s |
| Leitura do Parquet | 0,5 s |

O tratamento em pandas também foi aplicado aos 36.936 registros reais de 2025, com os resultados esperados:
2.004 linhas na estrutura analítica e 612 no top 3.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| pandas | Simples, conhecido, sem serviço adicional; atende ao volume | Limitado à memória de uma máquina; não demonstra Spark |
| PySpark em modo local | Atende literalmente ao título da questão; cresce sem reescrever a lógica | Exige Java e driver JDBC; mais memória e complexidade, sem ganho neste volume |
| Cluster Spark | Próximo de um ambiente grande | Vários serviços a mais, sem ganho neste volume |

## Decisão

Python com pandas para extrair e tratar, arquivos em volume local, PostgreSQL para servir, dbt da Stage ao DW
([ADR 0009](0009-dbt-da-stage-ao-dw.md)) e Airflow para orquestrar. O Spark fica para a [proposta futura](../proposta-futura/PROPOSTA-FUTURA.md), pois o volume medido não
justifica seu custo.

## Consequências

- A imagem fica menor e o ambiente tem menos pontos de falha, sem Java nem driver JDBC.
- A entrega não demonstra PySpark. A experiência com a ferramenta continua respondida na Questão 1.
- O título da questão pode criar a expectativa de Spark. A defesa é o enunciado e a medição acima.
- Se o volume crescer muito, a lógica precisará migrar. Mantê-la em funções separadas da DAG reduz esse custo.
