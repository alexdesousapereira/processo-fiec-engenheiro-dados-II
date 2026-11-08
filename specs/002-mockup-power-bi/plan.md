# Implementation Plan: Mockup do painel Power BI

**Branch**: `main` (o script sugere `002-mockup-power-bi`, que não foi criada) | **Date**: 2026-11-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-mockup-power-bi/spec.md`

## Summary

O plano é desenhar as duas telas do painel (capa e análise) como SVGs estáticos de 1280 × 720, seguindo as regras de `requisitos/pbi-mockup`:
esqueleto `topo-marca`, grade de 12 colunas, títulos descritivos com subtítulo de insight, datas de referência e atualização e só visuais nativos
do Power BI. Os números são reais, tirados do warehouse por uma consulta versionada. Um índice HTML e um racional acompanham as telas.

Dois scripts verificam o resultado: o validador de geometria do `pbi-mockup` e um conferidor que compara os números das telas com o warehouse.
Por fim, o contrato do painel e o PBIP são ajustados ao mockup. A principal mudança é fundir os dois gráficos de barras atuais, que se repetem, em um só.

## Technical Context

**Language/Version**: SVG 1.1 e HTML5 nas telas; Python 3.12 nos scripts, na imagem `pim-pf-ingestao:1.0`, que já existe

**Primary Dependencies**: só a biblioteca padrão do Python, com `xml.etree` e `json`; `psycopg2`, que já está na imagem, para ler o warehouse

**Storage**: nenhum novo; leitura do schema `warehouse` (feature 001)

**Testing**: `check_bounds.py` (geometria), conferidor de números contra o warehouse e validação dos JSON do PBIP contra os esquemas oficiais

**Target Platform**: navegador comum, para o mockup; Power BI Desktop, para o painel ajustado, com validação manual na T064 da feature 001

**Project Type**: artefato de design, mais um ajuste no painel existente

**Performance Goals**: não se aplica

**Constraints**: canvas de 1280 × 720; grade de 12 colunas, com margem 24 e gutter 20; SVG compatível com o Figma, sem `<use>`, `<symbol>` ou `currentColor`;
contraste WCAG AA

**Scale/Scope**: 2 telas, 5 visuais na análise, 11 atividades do caso de referência e 12 meses na linha

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Regra | Avaliação | Como é atendida |
|---|---|---|
| I. Prova como fonte | Passa, com justificativa | O painel não é exigido pela prova; a justificativa está no ADR 0005 e na spec 002 |
| II. Decisão defensável | Passa | O racional registra, por visual, o gráfico, o motivo e a alternativa recusada |
| III. Dados medidos | Passa | Os números vêm de `mockup/dados-referencia.sql`, e o conferidor compara as telas com o warehouse |
| IV. Cargas idempotentes | Não se aplica | Não há carga nova |
| V. Ambiente reproduzível | Passa | Os scripts rodam na imagem existente; o validador de geometria é copiado para o repositório, porque `requisitos/` não é versionado |
| Python | Passa | Scripts com tipos anotados, `logging` e configuração por variáveis de ambiente |
| SQL | Passa | A consulta lista as colunas e lê só o warehouse |
| Docker | Passa | Nenhuma imagem nem dependência nova |

**Resultado**: aprovado antes da pesquisa e reavaliado depois do design, sem violações.

## Project Structure

### Documentation (this feature)

```text
specs/002-mockup-power-bi/
├── plan.md
├── research.md
├── data-model.md          # conteúdo das telas e números do caso de referência
├── quickstart.md
├── contracts/
│   └── telas-mockup.md    # blocos, camadas, grade e textos de cada tela
├── checklists/requirements.md
└── tasks.md               # gerado por /speckit-tasks
```

### Source Code (repository root)

```text
mockup/
├── tela-01-capa.svg
├── tela-02-analise.svg
├── observatorio-mockup.html          # índice que embute as duas telas
├── observatorio-mockup-racional.md   # decisões por visual e desvios do pbi-mockup
├── dados-referencia.sql              # consulta de onde saem todos os números
├── conferir_mockup.py                # compara os números das telas com o warehouse
└── ferramentas/check_bounds.py       # validador de geometria, copiado de requisitos/pbi-mockup
powerbi/
├── ferramentas/gerar_pbip.py         # gerador do PBIP, agora versionado
└── Observatorio.*                    # PBIP regerado, seguindo o mockup
specs/001-pipeline-pim-pf/contracts/painel.md   # contrato do painel, atualizado (FR-017)
README.md                                       # mostra a tela de análise
```

**Structure Decision**: o mockup fica em uma pasta própria na raiz, `mockup/`, separada do painel, porque é um artefato de design aberto em navegador.
O gerador do PBIP, até aqui fora do repositório, passa a ser versionado: ele é a forma reproduzível de ajustar o painel ao mockup.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Cópia do `check_bounds.py` no repositório | `requisitos/` não é versionado, e a verificação precisa rodar em um clone | Instalar o pacote inteiro como skill traria 60 arquivos sem uso para a prova |
| Versionar o gerador do PBIP | Ajustar o painel ao mockup exige regerar os 36 arquivos de forma reproduzível | Editar os JSON à mão é sujeito a erro, e a edição não seria explicável na entrevista |
