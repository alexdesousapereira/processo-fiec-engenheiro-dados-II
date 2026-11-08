# Quickstart: validação do mockup

Pré-requisito: o ambiente da feature 001 no ar (`docker compose up -d`), com o warehouse carregado.

## 1. Abrir o mockup (SC-006)

Abra `mockup/observatorio-mockup.html` em um navegador.

**Esperado**: duas seções, capa e análise, cada uma com o SVG da tela e uma legenda por visual.

## 2. Conferir a geometria (SC-005)

```bash
MSYS_NO_PATHCONV=1 docker compose run --rm --no-deps -v "$(pwd)/mockup:/app/mockup" ingestao \
  python /app/mockup/ferramentas/check_bounds.py /app/mockup/tela-01-capa.svg /app/mockup/tela-02-analise.svg
```

**Esperado**: 0 erros e 0 colisões. Os avisos são revisados um a um.

## 3. Conferir os números e a estrutura (SC-001)

```bash
MSYS_NO_PATHCONV=1 docker compose run --rm -v "$(pwd)/mockup:/app/mockup" ingestao python /app/mockup/conferir_mockup.py
```

**Esperado**: todos os valores do caso de referência encontrados nas telas, XML bem formado e nenhum `<use>`, `<symbol>` ou `currentColor`.

## 4. Revisar o conteúdo

| Verificação | Esperado |
|---|---|
| Tela de análise, cartão da atividade líder | Têxteis, 145,03, +43,45 |
| Média | 101,58, com 11 atividades com dado |
| Top 3 no gráfico | 3.13, 3.24 e 3.11 na cor de ação |
| Contraste | Texto pequeno ≥ 4,5:1 (SC-004) |
| Escala de cinza | Top 3, média e sinais continuam distinguíveis |
| Racional | Uma seção por visual, com o status no Power BI (SC-003) |

## 5. Painel ajustado (SC-007)

1. Regere o PBIP e valide os JSON contra os esquemas oficiais:

   ```bash
   MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd):/repo" -w /repo python:3.12.13-slim-bookworm python powerbi/ferramentas/gerar_pbip.py
   MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd):/repo" -w /repo python:3.12.13-slim-bookworm sh -c \
     "pip install -q jsonschema==4.26.0 referencing==0.37.0 requests==2.34.2 && python powerbi/ferramentas/validar_pbip.py"
   ```

   **Esperado**: 0 erros. O aviso sobre `visualContainer/2.14.0` é normal: o Desktop grava essa versão, mas a Microsoft ainda não publicou o esquema, e o validador usa o 2.13.0.
2. No Power BI Desktop, abra `powerbi/Observatorio.pbip` e compare cada visual com o mockup.
3. Corrija ou registre no racional cada diferença.
