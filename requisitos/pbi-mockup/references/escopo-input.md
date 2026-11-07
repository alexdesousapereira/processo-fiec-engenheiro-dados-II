# Contrato de entrada — Escopo Funcional

A skill consome o escopo já levantado nas **Etapas 2–3 do Guia Xperiun**. Não levanta requisito novo. Aceita o conteúdo colado, o export Word/XLSX do Guia, ou este markdown preenchido.

## Modelo de preenchimento

```markdown
# Mockup — {Nome do Projeto / Cliente}
Cor de ação (marca do cliente): #______   Tema: claro | escuro

## Contexto (Etapa 2 — opcional, mas enriquece os títulos)
- Objetivo do dashboard: ...
- Decisões que ele precisa apoiar: ...

## Telas

### Tela 1 — {Nome da tela}
**O ponto:** {a pergunta/decisão que esta tela responde, em 1 frase}
**Visuais:**
- Indicador: {nome amigável} | Quebra/dimensão: {dimensão} | Filtro: {filtro} | História: {ver vocabulário}
- Indicador: ... | Quebra: ... | Filtro: ... | História: ...

### Tela 2 — {Nome da tela}
**O ponto:** ...
**Visuais:**
- ...
```

## Campos

| Campo | Obrigatório | Default se faltar |
|---|---|---|
| Nome + ordem da tela | sim | — |
| O ponto da tela | sim* | inferir do indicador principal e **confirmar** |
| Indicador (nome amigável) | sim | — (nunca inventar) |
| Regra de cálculo | não | irrelevante para o mockup (forma, não valor) |
| Dimensão / quebra | depende da história | — |
| Filtro | não | filtros padrão da tela (período atual etc.) |
| História | sim* | inferir e **confirmar** |

\* Se faltar, infira a partir do ponto/relação e confirme com o usuário antes de desenhar. Nunca crie indicador fora do escopo.

## Vocabulário de "história" (chave que escolhe o gráfico)

Mapeie cada visual a UMA destas. É o que `chart-chooser.md` usa.

| Palavra-chave da história | Significa |
|---|---|
| `kpi` | um número importa, isolado, talvez vs. meta |
| `comparar-categorias` | A vs B vs C... numa dimensão nominal |
| `comparar-2-grupos` | 2 grupos (ex.: pais×alunos, pré×pós) em várias variáveis |
| `parte-do-todo` | fatias que somam 100% |
| `composicao-no-tempo` | parte-do-todo que muda ao longo do tempo |
| `tendencia` | sobe/desce ao longo do tempo |
| `vs-meta` | desempenho contra meta/benchmark/norma |
| `achar-o-ofensor` | decompor um total/consolidado pra revelar o que puxa pra baixo/cima (o que o agregado esconde) |
| `ranking` | ordenar do maior pro menor (top/bottom N) |
| `correlacao` | como X muda quando Y muda |
| `survey-likert` | escala de concordância/satisfação |
| `distribuicao` | como os valores se espalham |
| `geografico` | padrão por localização (e a localização importa) |
| `fluxo` | de onde vem → pra onde vai, com quantidade |
| `qualitativo` | texto, citações, temas, perfis |

## Exemplo preenchido (mini)

```markdown
### Tela 1 — Visão Executiva Comercial
**O ponto:** Estamos batendo a meta do trimestre e onde está o desvio?
**Visuais:**
- Indicador: Receita | Quebra: — | Filtro: trimestre atual | História: kpi (vs-meta)
- Indicador: Margem % | Quebra: — | Filtro: trimestre atual | História: kpi (vs-meta)
- Indicador: Receita | Quebra: Regional | Filtro: trimestre atual | História: vs-meta
- Indicador: Receita | Quebra: Mês | Filtro: ano atual | História: tendencia
- Indicador: Receita | Quebra: Produto (top 5) | Filtro: trimestre | História: ranking
```
