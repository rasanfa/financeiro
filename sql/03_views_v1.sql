-- =============================================================================
-- 03_views_v1.sql
-- Views de consulta (saldos, faturas e painéis).
-- PostgreSQL / Supabase
--
-- Executar depois de 01_schema_v1.sql e 02_business_rules_v1.sql.
-- security_invoker = true: a view respeita RLS das tabelas-base (quando houver).
-- Apenas movimentações ATIVA entram nos totais.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- vw_saldos_contas
-- Saldo = saldo_inicial
--   + RECEITA
--   - DESPESA_AVISTA
--   - FOLHA_DEBITO (pagamento de fatura saindo da conta)
--   + FOLHA_CREDITO (se lançado na conta; normalmente no cartão)
--   - TRANSFERENCIA_INTERNA na origem
--   + TRANSFERENCIA_INTERNA no destino
-- DESPESA_PARCELADA não altera saldo da conta (fica na fatura do cartão).
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_saldos_contas
WITH (security_invoker = true) AS
SELECT
  c.id AS conta_id,
  c.usuario_id,
  c.instituicao_id,
  i.nome AS instituicao_nome,
  c.nome AS conta_nome,
  c.tipo_conta,
  c.saldo_inicial,
  c.saldo_inicial + COALESCE(mov.saldo_movimentos, 0) AS saldo_atual,
  c.ativo,
  c.created_at,
  c.updated_at
FROM contas c
LEFT JOIN instituicoes i
  ON i.id = c.instituicao_id
LEFT JOIN LATERAL (
  SELECT
    SUM(
      CASE
        WHEN m.tipo_movimento = 'RECEITA'
          AND m.conta_id = c.id
          THEN m.valor
        WHEN m.tipo_movimento IN ('DESPESA_AVISTA', 'FOLHA_DEBITO')
          AND m.conta_id = c.id
          THEN -m.valor
        WHEN m.tipo_movimento = 'FOLHA_CREDITO'
          AND m.conta_id = c.id
          THEN m.valor
        WHEN m.tipo_movimento = 'TRANSFERENCIA_INTERNA'
          AND m.conta_id = c.id
          THEN -m.valor
        WHEN m.tipo_movimento = 'TRANSFERENCIA_INTERNA'
          AND m.conta_destino_id = c.id
          THEN m.valor
        ELSE 0
      END
    ) AS saldo_movimentos
  FROM movimentacoes m
  WHERE m.status_movimentacao = 'ATIVA'
    AND m.usuario_id = c.usuario_id
    AND (m.conta_id = c.id OR m.conta_destino_id = c.id)
) mov ON true;

COMMENT ON VIEW vw_saldos_contas IS
  'Saldo atual por conta, derivado de saldo_inicial e movimentações ativas.';

-- -----------------------------------------------------------------------------
-- vw_faturas_abertas
-- Compras no cartão (DESPESA_PARCELADA) menos abatimentos (FOLHA_CREDITO),
-- agrupadas por cartão e competência. Só lista saldo_aberto > 0.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_faturas_abertas
WITH (security_invoker = true) AS
SELECT
  ca.id AS cartao_id,
  ca.usuario_id,
  ca.nome AS cartao_nome,
  ca.conta_id AS conta_pagamento_id,
  ca.dia_fechamento,
  ca.dia_vencimento,
  fat.competencia,
  fat.total_compras,
  fat.total_pago,
  fat.saldo_aberto
FROM cartoes ca
INNER JOIN (
  SELECT
    base.cartao_id,
    base.competencia,
    SUM(base.compras) AS total_compras,
    SUM(base.pagos) AS total_pago,
    SUM(base.compras) - SUM(base.pagos) AS saldo_aberto
  FROM (
    SELECT
      m.cartao_id,
      m.competencia,
      CASE
        WHEN m.tipo_movimento = 'DESPESA_PARCELADA' THEN m.valor
        ELSE 0
      END AS compras,
      CASE
        WHEN m.tipo_movimento = 'FOLHA_CREDITO' THEN m.valor
        ELSE 0
      END AS pagos
    FROM movimentacoes m
    WHERE m.status_movimentacao = 'ATIVA'
      AND m.cartao_id IS NOT NULL
      AND m.tipo_movimento IN ('DESPESA_PARCELADA', 'FOLHA_CREDITO')
  ) base
  GROUP BY base.cartao_id, base.competencia
) fat ON fat.cartao_id = ca.id
WHERE fat.saldo_aberto > 0
  AND ca.ativo = true;

COMMENT ON VIEW vw_faturas_abertas IS
  'Faturas de cartão com saldo em aberto por competência.';

-- -----------------------------------------------------------------------------
-- vw_painel_financeiro
-- Visão consolidada por usuário: saldos, faturas e totais históricos ativos.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_painel_financeiro
WITH (security_invoker = true) AS
SELECT
  u.id AS usuario_id,
  u.nome AS usuario_nome,
  COALESCE(s.saldo_total_contas, 0) AS saldo_total_contas,
  COALESCE(s.qtd_contas_ativas, 0) AS qtd_contas_ativas,
  COALESCE(f.total_faturas_abertas, 0) AS total_faturas_abertas,
  COALESCE(f.qtd_faturas_abertas, 0) AS qtd_faturas_abertas,
  COALESCE(m.total_receitas, 0) AS total_receitas,
  COALESCE(m.total_despesas_avista, 0) AS total_despesas_avista,
  COALESCE(m.total_despesas_parceladas, 0) AS total_despesas_parceladas,
  COALESCE(m.total_despesas_avista, 0)
    + COALESCE(m.total_despesas_parceladas, 0) AS total_despesas,
  COALESCE(m.total_receitas, 0)
    - COALESCE(m.total_despesas_avista, 0)
    - COALESCE(m.total_despesas_parceladas, 0) AS resultado
FROM usuarios u
LEFT JOIN (
  SELECT
    sc.usuario_id,
    SUM(sc.saldo_atual) FILTER (WHERE sc.ativo) AS saldo_total_contas,
    COUNT(*) FILTER (WHERE sc.ativo) AS qtd_contas_ativas
  FROM vw_saldos_contas sc
  GROUP BY sc.usuario_id
) s ON s.usuario_id = u.id
LEFT JOIN (
  SELECT
    fa.usuario_id,
    SUM(fa.saldo_aberto) AS total_faturas_abertas,
    COUNT(*) AS qtd_faturas_abertas
  FROM vw_faturas_abertas fa
  GROUP BY fa.usuario_id
) f ON f.usuario_id = u.id
LEFT JOIN (
  SELECT
    mov.usuario_id,
    SUM(mov.valor) FILTER (WHERE mov.tipo_movimento = 'RECEITA') AS total_receitas,
    SUM(mov.valor) FILTER (WHERE mov.tipo_movimento = 'DESPESA_AVISTA') AS total_despesas_avista,
    SUM(mov.valor) FILTER (WHERE mov.tipo_movimento = 'DESPESA_PARCELADA') AS total_despesas_parceladas
  FROM movimentacoes mov
  WHERE mov.status_movimentacao = 'ATIVA'
  GROUP BY mov.usuario_id
) m ON m.usuario_id = u.id
WHERE u.ativo = true;

COMMENT ON VIEW vw_painel_financeiro IS
  'Indicadores consolidados por usuário (saldos, faturas e totais).';

-- -----------------------------------------------------------------------------
-- vw_painel_mensal
-- Totais por usuário e competência (mês).
-- Transferências e folhas são informativas e não entram no resultado.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_painel_mensal
WITH (security_invoker = true) AS
SELECT
  m.usuario_id,
  m.competencia,
  COALESCE(SUM(m.valor) FILTER (WHERE m.tipo_movimento = 'RECEITA'), 0) AS receitas,
  COALESCE(SUM(m.valor) FILTER (WHERE m.tipo_movimento = 'DESPESA_AVISTA'), 0) AS despesas_avista,
  COALESCE(SUM(m.valor) FILTER (WHERE m.tipo_movimento = 'DESPESA_PARCELADA'), 0) AS despesas_parceladas,
  COALESCE(SUM(m.valor) FILTER (
    WHERE m.tipo_movimento IN ('DESPESA_AVISTA', 'DESPESA_PARCELADA')
  ), 0) AS despesas,
  COALESCE(SUM(m.valor) FILTER (WHERE m.tipo_movimento = 'RECEITA'), 0)
    - COALESCE(SUM(m.valor) FILTER (
        WHERE m.tipo_movimento IN ('DESPESA_AVISTA', 'DESPESA_PARCELADA')
      ), 0) AS resultado,
  COALESCE(SUM(m.valor) FILTER (WHERE m.tipo_movimento = 'TRANSFERENCIA_INTERNA'), 0) AS transferencias,
  COALESCE(SUM(m.valor) FILTER (WHERE m.tipo_movimento = 'FOLHA_DEBITO'), 0) AS folhas_debito,
  COALESCE(SUM(m.valor) FILTER (WHERE m.tipo_movimento = 'FOLHA_CREDITO'), 0) AS folhas_credito,
  COUNT(*) FILTER (WHERE m.tipo_movimento = 'RECEITA') AS qtd_receitas,
  COUNT(*) FILTER (
    WHERE m.tipo_movimento IN ('DESPESA_AVISTA', 'DESPESA_PARCELADA')
  ) AS qtd_despesas
FROM movimentacoes m
WHERE m.status_movimentacao = 'ATIVA'
GROUP BY m.usuario_id, m.competencia;

COMMENT ON VIEW vw_painel_mensal IS
  'Resumo mensal por competência: receitas, despesas e resultado.';
