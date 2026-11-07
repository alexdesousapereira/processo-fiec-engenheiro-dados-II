# Brief do projeto — visão do consumidor (mockup)

O brief é o artefato compartilhado do trio. **Produtor:** `/imersao-pbi-requisitos` (schema completo e autoritativo lá). **Consumidor:** este mockup. Se o brief existir, leia-o e pule perguntas; senão, monte por intake.

## Campos que o mockup lê

```
projeto / cliente
perfis[]:                          (vários por projeto; cada um → sua(s) tela(s))
  nome/cargo · papel: consumidor(0-clique) | produtor(explora)
  altitude: estratégico | tático | operacional · usa_telas[]
  ambiente: desktop | mobile | TV | painel
publico: executivo | operacional | analitico   (legado/derivável das altitudes)
visual:
  tema: dark | light
  cor_primaria (marca) · cor_acao (destaque)
  cores_categoricas[]  (até ~8; senão deriva da primária)
  semanticas: bom · ruim · neutro   (opcional)
  fonte: Segoe UI (default)
  menu_navegacao: esquerda | topo | nenhum   (default esquerda)
telas[]:
  nome · ordem · o_ponto (pergunta/decisão da tela)
  perfil (dono) · ambiente: desktop | mobile | TV | painel
  data: referencia (período dos dados) · selecao (mês|ano|dinâmica|últimos-12m) · comparacao (vs-LY|vs-meta|nenhuma)
  visuais[]:
    indicador(es) · dimensao/quebra · filtro · historia · grafico · status_pbi
atualizacao (freq + defasagem D-1?) / fonte_dados (opcional)
```

`historia`, `grafico` e `status_pbi` podem vir vazios do brief — o mockup infere (`chart-chooser.md` + `pbi-visuals.md`) e confirma. Se `perfis`/`ambiente`/`data` faltarem, assuma os defaults (1 perfil consumidor desktop, seleção mês + últimos 12m) e **confirme**.

## Templates de domínio (modo express)

Quando o usuário só dá o **domínio + público**, proponha este conjunto-padrão e peça ajuste. Não invente além do que faz sentido; confirme indicadores antes de desenhar.

| Domínio | KPIs (topo) | Visuais (corpo) |
|---|---|---|
| **Diretoria / Estratégia** | Receita (vs meta) · Crescimento % · ROIC · EBITDA | Metas do ano (bullet vs meta) · Receita e lucro mensal (linha) · Desempenho por unidade (barra) · Farol de KRIs (cartões) |
| **Comercial / Vendas** | Receita (vs meta) · Margem % · Ticket médio · Nº pedidos | Receita por Regional (barra vs meta) · Receita mensal (linha) · Top 5 Produtos (barra ordenada) · Funil de vendas |
| **Cliente (transversal)** | NPS · Churn % · CSAT · CLV | NPS (linha) · Promotor/neutro/detrator (empilhada divergente) · Saldo de base (cascata) · Base por RFV (barra) |
| **Customer Success** | NRR/GRR · Retenção % · Adoção · Health score | Retenção por coorte (matriz heat) · Renovações (bullet vs meta) · Adoção por conta (barra) · Contas em risco (barra ordenada) |
| **Marketing** | Leads · CAC · Conversão % · ROI | Leads por Canal (barra) · Funil de conversão · Tendência de leads (linha) · Investimento×Retorno (dispersão) |
| **Marketing Digital / Web** | Sessões · Conversão % · Bounce · Taxa de e-mail | Tráfego por canal (barra) · Sessões (linha) · Funil do site · Conversão por campanha (barra ordenada) |
| **Produto** | MAU/DAU · Retenção · MRR · Adoção | Retenção por coorte (matriz heat) · MRR (linha) · Adoção por feature (barra ordenada) · Funil de ativação |
| **Financeiro** | Receita · Despesa · EBITDA/Lucro · Margem % | Ponte de resultado (cascata) · Receita×Despesa mensal (combo) · Despesa por Categoria (barra) · DRE resumida (matriz) |
| **Tesouraria / Liquidez** | Caixa · Liquidez corrente · PMR/PMP · Inadimplência % | Fluxo projetado (linha) · Capital de giro (cascata) · Aging de recebíveis (barra) · Caixa vs mínimo (bullet vs meta) |
| **Operações** | Produtividade · Custo unitário · Lead time · Retrabalho % | Produtividade por área (barra) · Lead time (linha) · Aderência ao plano (bullet vs meta) · Ofensores (barra ordenada) |
| **Produção / Manufatura** | OEE · Capacidade×real · FPY · Paradas | OEE por linha (barra) · OEE (linha) · Pareto de paradas (combo) · Capacidade vs realizado (bullet vs meta) |
| **Qualidade** | Não conformidades · DPU · COPQ · Devoluções % | NC por tipo (barra ordenada) · Defeitos (linha) · Custo da má qualidade (100% empilhada) · CAPA (matriz) |
| **Compras / Suprimentos** | Saving · Spend · Lead time · OTD fornecedor % | Saving×Spend (combo) · Spend por categoria (barra) · Concentração de fornecedor (100% empilhada) · Ranking de fornecedor (barra ordenada) |
| **Logística** | OTIF % · Custo de frete · Prazo de entrega · Avarias % | OTIF (bullet vs meta) · Frete por rota (barra) · Ofensores de atraso (barra ordenada) · Prazo (linha) |
| **Estoque** | Giro · Cobertura (dias) · Acuracidade % · Ruptura % | Giro por categoria (barra) · Cobertura (linha) · Curva ABC (Pareto/barra ordenada) · Ruptura (bullet vs meta) |
| **Armazém / Expedição** | Custo/unidade · Ocupação % · Tempo de expedição · Inconformidades | Movimentação (linha) · Ocupação (bullet vs meta) · Tempo por etapa (barra) · Inconformidades (barra ordenada) |
| **Varejo / Comércio** | Venda/m² · Ticket · Conversão de loja % · Itens/venda | Venda por loja (barra ordenada) · Venda diária (linha) · Conversão (bullet vs meta) · Mix de categoria (100% empilhada) |
| **Atendimento / Suporte** | Chamados · % resolvidos · CSAT · TMA | Chamados por status (barra/funil) · Tendência de chamados (linha) · Top motivos (ranking) · SLA (KPI/bullet vs meta) |
| **RH / Colaboradores** | Headcount · Turnover % · Vagas abertas · Tempo médio contratação | Headcount por área (barra) · Turnover mensal (linha) · Diversidade/faixa etária (100% empilhada) · eNPS (KPI) |
| **Tecnologia da Informação (TI)** | Uptime % · Incidentes · MTTR · Custo/usuário | Disponibilidade (bullet vs meta) · Incidentes por categoria (barra ordenada) · MTTR (linha) · SLA de chamado (barra) |
| **Projetos / PMO** | Execução física % · CV/SV · Carteira · Desvio de prazo | Curva S física×financeira (linha) · Saúde da carteira (barra/matriz) · Marcos (bullet vs meta) · Riscos por projeto (barra ordenada) |
| **Jurídico** | Nº processos · Contingência R$ · Contratos a vencer · Êxito % | Processos por status (barra) · Contingência por risco (100% empilhada) · Contratos a vencer (barra ordenada) · Êxito (linha) |
| **Riscos e Compliance** | Riscos críticos · Controles ok % · NCs abertas · Planos no prazo % | Matriz impacto×probabilidade (dispersão/heatmap) · NCs por área (barra ordenada) · Planos de ação (bullet vs meta) · Riscos (linha) |
| **ESG / Sustentabilidade** | Emissões (tCO₂) · Energia/Água · Resíduos · % Reciclado | Absoluto × intensidade (combo) · Emissões (linha) · Mix de resíduos (100% empilhada) · Metas ESG (bullet vs meta) |

Densidade por público: **executivo** = menos visuais, mais KPI e tendência; **operacional** = status/tabelas/alertas, atualização frequente; **analítico** = mais quebras, dispersão, drill, pequenos múltiplos.
