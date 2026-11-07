# ADR 0003: Detecção de mudanças por hash

**Status:** proposta, 2026-11-06

## Contexto

A prova pede novas cargas mensais e reprocessamento fácil. Medições em 2026-11-06:

- Os 297 períodos de `/periodos` têm a mesma data de modificação.
- 202609 traz números apenas para o Brasil; as outras 18 localidades trazem `...`.

Não se sabe se o IBGE revisa meses antigos. Portanto, buscar só o "próximo mês" pode perder dados.

## Alternativas

| Alternativa | Vantagem | Desvantagem |
|---|---|---|
| Buscar só meses novos | Mínimo de requisições | Perde UFs que chegam depois e revisões |
| Janela móvel de N meses | Cobre atrasos recentes | N arbitrário; perde revisões antigas |
| Regravar tudo a cada mudança | Muito simples | Cada mudança duplica os arquivos brutos e reprocessa tudo |
| Ler tudo e gravar o que mudou, por hash | Um só mecanismo; registra o que mudou | Mais requisições quando há mudança e uma tabela de controle |

## Decisão

Verificar a data da tabela todos os dias. Se mudar, ler todos os meses, comparar o hash com a tabela
`controle.carga_periodo` e gravar nos arquivos brutos só os meses com hash diferente.

## Consequências

- O mesmo fluxo cobre carga inicial, mês novo, mês parcial e revisão.
- A leitura completa foi estimada em cerca de 5 minutos, com pausa entre requisições, e ocorre só
  quando a data muda. Esse tempo será medido na primeira carga.
- O hash precisa de forma canônica, para que a ordem dos campos não gere falsas mudanças.
- O histórico dos arquivos brutos permitirá medir se o IBGE realmente faz revisões.
