-- =============================================================================
-- 01_schema_v1.sql
-- Estrutura do banco (tipos, tabelas, chaves, índices e dados iniciais).
-- PostgreSQL / Supabase
--
-- Ordem de execução: 01_schema_v1.sql → 02_business_rules_v1.sql → 03_views_v1.sql
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Extensões
-- -----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- -----------------------------------------------------------------------------
-- ENUMs
-- -----------------------------------------------------------------------------
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_conta') THEN
    CREATE TYPE tipo_conta AS ENUM (
      'CONTA_CORRENTE',
      'CONTA_POUPANCA',
      'BENEFICIO_RESTRITO',
      'CARTEIRA_DIGITAL',
      'INVESTIMENTO'
    );
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_categoria') THEN
    CREATE TYPE tipo_categoria AS ENUM (
      'RECEITA',
      'DESPESA',
      'AMBOS'
    );
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_movimento') THEN
    CREATE TYPE tipo_movimento AS ENUM (
      'RECEITA',
      'DESPESA_AVISTA',
      'DESPESA_PARCELADA',
      'TRANSFERENCIA_INTERNA',
      'FOLHA_CREDITO',
      'FOLHA_DEBITO'
    );
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_movimentacao') THEN
    CREATE TYPE status_movimentacao AS ENUM (
      'ATIVA',
      'CANCELADA'
    );
  END IF;
END
$$;

-- -----------------------------------------------------------------------------
-- Função de auditoria: atualiza updated_at em qualquer UPDATE
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

-- -----------------------------------------------------------------------------
-- usuarios
-- Cadastro de donos dos dados. Pode ser vinculado depois a auth.users (Supabase).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nome        text NOT NULL,
  email       text NOT NULL,
  ativo       boolean NOT NULL DEFAULT true,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT usuarios_email_key UNIQUE (email)
);

COMMENT ON TABLE usuarios IS 'Usuários do sistema financeiro pessoal.';
COMMENT ON COLUMN usuarios.ativo IS 'Cadastro ativo. Preferir inativar em vez de excluir.';

DROP TRIGGER IF EXISTS trg_usuarios_updated_at ON usuarios;
CREATE TRIGGER trg_usuarios_updated_at
BEFORE UPDATE ON usuarios
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- -----------------------------------------------------------------------------
-- instituicoes
-- Bancos, fintechs e emissores (Nubank, Itaú, etc.).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS instituicoes (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id  uuid NOT NULL REFERENCES usuarios (id),
  nome        text NOT NULL,
  ativo       boolean NOT NULL DEFAULT true,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT instituicoes_usuario_nome_key UNIQUE (usuario_id, nome)
);

COMMENT ON TABLE instituicoes IS 'Instituições financeiras vinculadas ao usuário.';

CREATE INDEX IF NOT EXISTS idx_instituicoes_usuario_id ON instituicoes (usuario_id);

DROP TRIGGER IF EXISTS trg_instituicoes_updated_at ON instituicoes;
CREATE TRIGGER trg_instituicoes_updated_at
BEFORE UPDATE ON instituicoes
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- -----------------------------------------------------------------------------
-- contas
-- Contas bancárias, carteiras e investimentos. saldo_inicial é o ponto de partida.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS contas (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id     uuid NOT NULL REFERENCES usuarios (id),
  instituicao_id uuid REFERENCES instituicoes (id),
  nome           text NOT NULL,
  tipo_conta     tipo_conta NOT NULL,
  saldo_inicial  numeric(14, 2) NOT NULL DEFAULT 0,
  ativo          boolean NOT NULL DEFAULT true,
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT contas_usuario_nome_key UNIQUE (usuario_id, nome)
);

COMMENT ON TABLE contas IS 'Contas do usuário. O saldo corrente é derivado nas views.';
COMMENT ON COLUMN contas.saldo_inicial IS 'Saldo de abertura; não é atualizado pelas movimentações.';

CREATE INDEX IF NOT EXISTS idx_contas_usuario_id ON contas (usuario_id);
CREATE INDEX IF NOT EXISTS idx_contas_instituicao_id ON contas (instituicao_id);

DROP TRIGGER IF EXISTS trg_contas_updated_at ON contas;
CREATE TRIGGER trg_contas_updated_at
BEFORE UPDATE ON contas
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- -----------------------------------------------------------------------------
-- cartoes
-- Cartões de crédito. dia_fechamento / dia_vencimento em dia do mês (1–28).
-- conta_id: conta usada preferencialmente para pagar a fatura.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cartoes (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id      uuid NOT NULL REFERENCES usuarios (id),
  instituicao_id  uuid REFERENCES instituicoes (id),
  conta_id        uuid REFERENCES contas (id),
  nome            text NOT NULL,
  limite          numeric(14, 2),
  dia_fechamento  smallint,
  dia_vencimento  smallint,
  ativo           boolean NOT NULL DEFAULT true,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT cartoes_usuario_nome_key UNIQUE (usuario_id, nome),
  CONSTRAINT cartoes_dia_fechamento_chk CHECK (
    dia_fechamento IS NULL OR (dia_fechamento BETWEEN 1 AND 28)
  ),
  CONSTRAINT cartoes_dia_vencimento_chk CHECK (
    dia_vencimento IS NULL OR (dia_vencimento BETWEEN 1 AND 28)
  )
);

COMMENT ON TABLE cartoes IS 'Cartões de crédito. Compras parceladas referenciam este cadastro.';

CREATE INDEX IF NOT EXISTS idx_cartoes_usuario_id ON cartoes (usuario_id);
CREATE INDEX IF NOT EXISTS idx_cartoes_conta_id ON cartoes (conta_id);

DROP TRIGGER IF EXISTS trg_cartoes_updated_at ON cartoes;
CREATE TRIGGER trg_cartoes_updated_at
BEFORE UPDATE ON cartoes
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- -----------------------------------------------------------------------------
-- formas_pagamento
-- Catálogo de meios de pagamento (PIX, débito, crédito, etc.).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS formas_pagamento (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo      text NOT NULL,
  nome        text NOT NULL,
  ativo       boolean NOT NULL DEFAULT true,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT formas_pagamento_codigo_key UNIQUE (codigo)
);

COMMENT ON TABLE formas_pagamento IS 'Formas de pagamento utilizadas nas movimentações.';

DROP TRIGGER IF EXISTS trg_formas_pagamento_updated_at ON formas_pagamento;
CREATE TRIGGER trg_formas_pagamento_updated_at
BEFORE UPDATE ON formas_pagamento
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

INSERT INTO formas_pagamento (codigo, nome)
VALUES
  ('PIX', 'PIX'),
  ('DEBITO', 'Débito'),
  ('CREDITO', 'Crédito'),
  ('DINHEIRO', 'Dinheiro'),
  ('TED', 'TED'),
  ('BOLETO', 'Boleto'),
  ('TRANSFERENCIA', 'Transferência')
ON CONFLICT (codigo) DO NOTHING;

-- -----------------------------------------------------------------------------
-- categorias / subcategorias
-- tipo_categoria restringe o uso em receitas, despesas ou ambos.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categorias (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id      uuid NOT NULL REFERENCES usuarios (id),
  nome            text NOT NULL,
  tipo_categoria  tipo_categoria NOT NULL,
  ativo           boolean NOT NULL DEFAULT true,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT categorias_usuario_nome_key UNIQUE (usuario_id, nome)
);

COMMENT ON TABLE categorias IS 'Categorias de receita/despesa. Inative em vez de excluir.';

CREATE INDEX IF NOT EXISTS idx_categorias_usuario_id ON categorias (usuario_id);

DROP TRIGGER IF EXISTS trg_categorias_updated_at ON categorias;
CREATE TRIGGER trg_categorias_updated_at
BEFORE UPDATE ON categorias
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TABLE IF NOT EXISTS subcategorias (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  categoria_id  uuid NOT NULL REFERENCES categorias (id),
  nome          text NOT NULL,
  ativo         boolean NOT NULL DEFAULT true,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT subcategorias_categoria_nome_key UNIQUE (categoria_id, nome)
);

COMMENT ON TABLE subcategorias IS 'Subcategorias. Devem pertencer à categoria da movimentação.';

CREATE INDEX IF NOT EXISTS idx_subcategorias_categoria_id ON subcategorias (categoria_id);

DROP TRIGGER IF EXISTS trg_subcategorias_updated_at ON subcategorias;
CREATE TRIGGER trg_subcategorias_updated_at
BEFORE UPDATE ON subcategorias
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- -----------------------------------------------------------------------------
-- beneficiarios
-- Favorecidos / estabelecimentos (quem recebe ou de quem vem o dinheiro).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS beneficiarios (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id  uuid NOT NULL REFERENCES usuarios (id),
  nome        text NOT NULL,
  ativo       boolean NOT NULL DEFAULT true,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT beneficiarios_usuario_nome_key UNIQUE (usuario_id, nome)
);

COMMENT ON TABLE beneficiarios IS 'Pessoas ou estabelecimentos envolvidos nas movimentações.';

CREATE INDEX IF NOT EXISTS idx_beneficiarios_usuario_id ON beneficiarios (usuario_id);

DROP TRIGGER IF EXISTS trg_beneficiarios_updated_at ON beneficiarios;
CREATE TRIGGER trg_beneficiarios_updated_at
BEFORE UPDATE ON beneficiarios
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- -----------------------------------------------------------------------------
-- movimentacoes
-- Fato financeiro. valor é sempre positivo; o sinal vem de tipo_movimento.
-- grupo_transacao agrupa parcelas, transferências (origem/destino) e folhas.
-- competencia: mês de caixa/orçamento (normalizado para o dia 1 nas regras).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS movimentacoes (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id           uuid NOT NULL REFERENCES usuarios (id),
  tipo_movimento       tipo_movimento NOT NULL,
  status_movimentacao  status_movimentacao NOT NULL DEFAULT 'ATIVA',
  data                 date NOT NULL,
  competencia          date NOT NULL,
  descricao            text NOT NULL,
  valor                numeric(14, 2) NOT NULL,
  conta_id             uuid REFERENCES contas (id),
  conta_destino_id     uuid REFERENCES contas (id),
  cartao_id            uuid REFERENCES cartoes (id),
  forma_pagamento_id   uuid REFERENCES formas_pagamento (id),
  categoria_id         uuid REFERENCES categorias (id),
  subcategoria_id      uuid REFERENCES subcategorias (id),
  beneficiario_id      uuid REFERENCES beneficiarios (id),
  grupo_transacao      uuid NOT NULL DEFAULT gen_random_uuid(),
  parcela_atual        integer NOT NULL DEFAULT 1,
  total_parcelas       integer NOT NULL DEFAULT 1,
  created_at           timestamptz NOT NULL DEFAULT now(),
  updated_at           timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE movimentacoes IS 'Lançamentos financeiros. Cancelar via status; não apagar histórico.';
COMMENT ON COLUMN movimentacoes.valor IS 'Sempre positivo. Crédito/débito é definido por tipo_movimento.';
COMMENT ON COLUMN movimentacoes.grupo_transacao IS 'Agrupa parcelas, os dois lados de uma transferência e folha crédito/débito.';
COMMENT ON COLUMN movimentacoes.competencia IS 'Mês de competência (dia 1). Independente da data do lançamento.';
COMMENT ON COLUMN movimentacoes.conta_destino_id IS 'Conta de crédito em TRANSFERENCIA_INTERNA.';
COMMENT ON COLUMN movimentacoes.parcela_atual IS 'Número da parcela (1 quando não há parcelamento).';
COMMENT ON COLUMN movimentacoes.total_parcelas IS 'Total de parcelas (1 quando não há parcelamento).';

CREATE INDEX IF NOT EXISTS idx_movimentacoes_usuario_competencia
  ON movimentacoes (usuario_id, competencia);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_conta_id
  ON movimentacoes (conta_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_conta_destino_id
  ON movimentacoes (conta_destino_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_cartao_id
  ON movimentacoes (cartao_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_grupo_transacao
  ON movimentacoes (grupo_transacao);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_status
  ON movimentacoes (status_movimentacao);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_forma_pagamento_id
  ON movimentacoes (forma_pagamento_id);

DROP TRIGGER IF EXISTS trg_movimentacoes_updated_at ON movimentacoes;
CREATE TRIGGER trg_movimentacoes_updated_at
BEFORE UPDATE ON movimentacoes
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
