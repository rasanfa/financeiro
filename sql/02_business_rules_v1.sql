-- =============================================================================
-- 02_business_rules_v1.sql
-- Regras de negócio: CHECK constraints, validações e bloqueio de DELETE.
-- PostgreSQL / Supabase
--
-- Executar depois de 01_schema_v1.sql.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1) Receita exige conta
-- 2) Receita não pode usar cartão
-- 3) Despesa parcelada exige cartão
--    (1x no crédito também usa DESPESA_PARCELADA com total_parcelas = 1)
-- 4) Despesa à vista exige conta
-- 5) Parcelamento válido
-- 6) Data >= 2020-01-01
--
-- Regras extras alinhadas ao modelo:
--   - valor sempre > 0
--   - transferência interna exige origem, destino e contas distintas, sem cartão
--   - FOLHA_DEBITO (pagamento da fatura) exige conta
--   - FOLHA_CREDITO (abatimento no cartão) exige cartão
--   - receita e despesas exigem forma_pagamento_id
-- -----------------------------------------------------------------------------
ALTER TABLE movimentacoes
  DROP CONSTRAINT IF EXISTS movimentacoes_valor_positivo_chk,
  DROP CONSTRAINT IF EXISTS movimentacoes_data_minima_chk,
  DROP CONSTRAINT IF EXISTS movimentacoes_parcelamento_chk,
  DROP CONSTRAINT IF EXISTS movimentacoes_receita_conta_chk,
  DROP CONSTRAINT IF EXISTS movimentacoes_receita_sem_cartao_chk,
  DROP CONSTRAINT IF EXISTS movimentacoes_despesa_parcelada_cartao_chk,
  DROP CONSTRAINT IF EXISTS movimentacoes_despesa_avista_conta_chk,
  DROP CONSTRAINT IF EXISTS movimentacoes_transferencia_chk,
  DROP CONSTRAINT IF EXISTS movimentacoes_folha_debito_chk,
  DROP CONSTRAINT IF EXISTS movimentacoes_folha_credito_chk,
  DROP CONSTRAINT IF EXISTS movimentacoes_forma_pagamento_chk;

ALTER TABLE movimentacoes
  ADD CONSTRAINT movimentacoes_valor_positivo_chk
    CHECK (valor > 0),
  ADD CONSTRAINT movimentacoes_data_minima_chk
    CHECK (data >= DATE '2020-01-01'),
  ADD CONSTRAINT movimentacoes_parcelamento_chk
    CHECK (
      parcela_atual >= 1
      AND total_parcelas >= 1
      AND parcela_atual <= total_parcelas
      AND (
        (
          tipo_movimento = 'DESPESA_PARCELADA'
          AND total_parcelas >= 1
        )
        OR (
          tipo_movimento <> 'DESPESA_PARCELADA'
          AND parcela_atual = 1
          AND total_parcelas = 1
        )
      )
    ),
  ADD CONSTRAINT movimentacoes_receita_conta_chk
    CHECK (
      tipo_movimento <> 'RECEITA'
      OR conta_id IS NOT NULL
    ),
  ADD CONSTRAINT movimentacoes_receita_sem_cartao_chk
    CHECK (
      tipo_movimento <> 'RECEITA'
      OR cartao_id IS NULL
    ),
  ADD CONSTRAINT movimentacoes_despesa_parcelada_cartao_chk
    CHECK (
      tipo_movimento <> 'DESPESA_PARCELADA'
      OR cartao_id IS NOT NULL
    ),
  ADD CONSTRAINT movimentacoes_despesa_avista_conta_chk
    CHECK (
      tipo_movimento <> 'DESPESA_AVISTA'
      OR conta_id IS NOT NULL
    ),
  ADD CONSTRAINT movimentacoes_transferencia_chk
    CHECK (
      tipo_movimento <> 'TRANSFERENCIA_INTERNA'
      OR (
        conta_id IS NOT NULL
        AND conta_destino_id IS NOT NULL
        AND conta_id <> conta_destino_id
        AND cartao_id IS NULL
      )
    ),
  ADD CONSTRAINT movimentacoes_folha_debito_chk
    CHECK (
      tipo_movimento <> 'FOLHA_DEBITO'
      OR conta_id IS NOT NULL
    ),
  ADD CONSTRAINT movimentacoes_folha_credito_chk
    CHECK (
      tipo_movimento <> 'FOLHA_CREDITO'
      OR cartao_id IS NOT NULL
    ),
  ADD CONSTRAINT movimentacoes_forma_pagamento_chk
    CHECK (
      tipo_movimento NOT IN ('RECEITA', 'DESPESA_AVISTA', 'DESPESA_PARCELADA')
      OR forma_pagamento_id IS NOT NULL
    );

-- -----------------------------------------------------------------------------
-- Normaliza competencia para o primeiro dia do mês.
-- Se vier nula, usa o mês de data.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION normalizar_competencia()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.competencia IS NULL THEN
    NEW.competencia := date_trunc('month', NEW.data)::date;
  ELSE
    NEW.competencia := date_trunc('month', NEW.competencia)::date;
  END IF;
  RETURN NEW;
END;
$$;

COMMENT ON FUNCTION normalizar_competencia() IS
  'Garante que competencia seja sempre o dia 1 do mês.';

DROP TRIGGER IF EXISTS trg_movimentacoes_competencia ON movimentacoes;
CREATE TRIGGER trg_movimentacoes_competencia
BEFORE INSERT OR UPDATE OF data, competencia
ON movimentacoes
FOR EACH ROW
EXECUTE FUNCTION normalizar_competencia();

-- -----------------------------------------------------------------------------
-- 7) Trigger valida categoria / subcategoria
--    - RECEITA, DESPESA_AVISTA e DESPESA_PARCELADA exigem categoria ativa
--    - tipo da categoria deve ser compatível (RECEITA, DESPESA ou AMBOS)
--    - subcategoria, se informada, deve existir, estar ativa e pertencer à categoria
--    - transferência/folha podem omitir categoria; se informada, ainda valida vínculo
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION validar_categoria_subcategoria()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  v_tipo_categoria tipo_categoria;
  v_categoria_ativa boolean;
  v_sub_categoria_id uuid;
  v_sub_ativa boolean;
  v_exige_categoria boolean;
BEGIN
  v_exige_categoria := NEW.tipo_movimento IN (
    'RECEITA',
    'DESPESA_AVISTA',
    'DESPESA_PARCELADA'
  );

  IF NEW.categoria_id IS NULL THEN
    IF v_exige_categoria THEN
      RAISE EXCEPTION
        'Categoria é obrigatória para movimentações do tipo %',
        NEW.tipo_movimento
        USING ERRCODE = 'check_violation';
    END IF;

    IF NEW.subcategoria_id IS NOT NULL THEN
      RAISE EXCEPTION
        'Subcategoria exige categoria_id preenchido'
        USING ERRCODE = 'check_violation';
    END IF;

    RETURN NEW;
  END IF;

  SELECT c.tipo_categoria, c.ativo
    INTO v_tipo_categoria, v_categoria_ativa
  FROM categorias c
  WHERE c.id = NEW.categoria_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Categoria não encontrada'
      USING ERRCODE = 'foreign_key_violation';
  END IF;

  IF v_categoria_ativa IS NOT TRUE THEN
    RAISE EXCEPTION 'Categoria inativa não pode ser usada em movimentações'
      USING ERRCODE = 'check_violation';
  END IF;

  IF NEW.tipo_movimento = 'RECEITA' AND v_tipo_categoria = 'DESPESA' THEN
    RAISE EXCEPTION 'Categoria de despesa não pode ser usada em receita'
      USING ERRCODE = 'check_violation';
  END IF;

  IF NEW.tipo_movimento IN ('DESPESA_AVISTA', 'DESPESA_PARCELADA')
     AND v_tipo_categoria = 'RECEITA' THEN
    RAISE EXCEPTION 'Categoria de receita não pode ser usada em despesa'
      USING ERRCODE = 'check_violation';
  END IF;

  IF NEW.subcategoria_id IS NOT NULL THEN
    SELECT s.categoria_id, s.ativo
      INTO v_sub_categoria_id, v_sub_ativa
    FROM subcategorias s
    WHERE s.id = NEW.subcategoria_id;

    IF NOT FOUND THEN
      RAISE EXCEPTION 'Subcategoria não encontrada'
        USING ERRCODE = 'foreign_key_violation';
    END IF;

    IF v_sub_ativa IS NOT TRUE THEN
      RAISE EXCEPTION 'Subcategoria inativa não pode ser usada em movimentações'
        USING ERRCODE = 'check_violation';
    END IF;

    IF v_sub_categoria_id <> NEW.categoria_id THEN
      RAISE EXCEPTION 'Subcategoria não pertence à categoria informada'
        USING ERRCODE = 'check_violation';
    END IF;
  END IF;

  RETURN NEW;
END;
$$;

COMMENT ON FUNCTION validar_categoria_subcategoria() IS
  'Valida existência, status e compatibilidade de categoria/subcategoria na movimentação.';

DROP TRIGGER IF EXISTS trg_movimentacoes_categoria ON movimentacoes;
CREATE TRIGGER trg_movimentacoes_categoria
BEFORE INSERT OR UPDATE OF tipo_movimento, categoria_id, subcategoria_id
ON movimentacoes
FOR EACH ROW
EXECUTE FUNCTION validar_categoria_subcategoria();

-- -----------------------------------------------------------------------------
-- 8) bloquear_delete()
-- 9) Impede DELETE físico nos cadastros listados.
--    Use UPDATE ... SET ativo = false para inativar.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION bloquear_delete()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION
    'Exclusão física não permitida na tabela %. Inative o registro (ativo = false).',
    TG_TABLE_NAME
    USING ERRCODE = 'restrict_violation';
END;
$$;

COMMENT ON FUNCTION bloquear_delete() IS
  'Impede DELETE físico. Cadastros devem ser inativados.';

DROP TRIGGER IF EXISTS trg_contas_bloquear_delete ON contas;
CREATE TRIGGER trg_contas_bloquear_delete
BEFORE DELETE ON contas
FOR EACH ROW
EXECUTE FUNCTION bloquear_delete();

DROP TRIGGER IF EXISTS trg_categorias_bloquear_delete ON categorias;
CREATE TRIGGER trg_categorias_bloquear_delete
BEFORE DELETE ON categorias
FOR EACH ROW
EXECUTE FUNCTION bloquear_delete();

DROP TRIGGER IF EXISTS trg_cartoes_bloquear_delete ON cartoes;
CREATE TRIGGER trg_cartoes_bloquear_delete
BEFORE DELETE ON cartoes
FOR EACH ROW
EXECUTE FUNCTION bloquear_delete();

DROP TRIGGER IF EXISTS trg_beneficiarios_bloquear_delete ON beneficiarios;
CREATE TRIGGER trg_beneficiarios_bloquear_delete
BEFORE DELETE ON beneficiarios
FOR EACH ROW
EXECUTE FUNCTION bloquear_delete();

DROP TRIGGER IF EXISTS trg_instituicoes_bloquear_delete ON instituicoes;
CREATE TRIGGER trg_instituicoes_bloquear_delete
BEFORE DELETE ON instituicoes
FOR EACH ROW
EXECUTE FUNCTION bloquear_delete();
