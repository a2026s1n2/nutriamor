-- NutriAmor — esquema de referência PostgreSQL (alinhado ao DER e à documentação).
-- Em produção com Django, prefira `python manage.py migrate` como fonte de verdade.
-- Este ficheiro serve para revisão, DBA ou criação manual da base `nutriamor`.

BEGIN;

CREATE TABLE IF NOT EXISTS perfis (
  id BIGSERIAL PRIMARY KEY,
  nome VARCHAR(64) NOT NULL,
  codigo VARCHAR(32) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS categorias (
  id BIGSERIAL PRIMARY KEY,
  nome VARCHAR(120) NOT NULL,
  descricao TEXT NOT NULL DEFAULT '',
  ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS tipos_fornecedor (
  id BIGSERIAL PRIMARY KEY,
  nome VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS fornecedores (
  id BIGSERIAL PRIMARY KEY,
  tipo_fornecedor_id BIGINT REFERENCES tipos_fornecedor (id) ON DELETE SET NULL,
  razao_social VARCHAR(200) NOT NULL,
  nome_fantasia VARCHAR(200) NOT NULL DEFAULT '',
  documento VARCHAR(20) NOT NULL DEFAULT '',
  telefone VARCHAR(32) NOT NULL DEFAULT '',
  email VARCHAR(254) NOT NULL DEFAULT '',
  cidade VARCHAR(120) NOT NULL DEFAULT '',
  uf VARCHAR(2) NOT NULL DEFAULT '',
  ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS produtos (
  id BIGSERIAL PRIMARY KEY,
  categoria_id BIGINT NOT NULL REFERENCES categorias (id) ON DELETE PROTECT,
  codigo VARCHAR(40) NOT NULL UNIQUE,
  descricao VARCHAR(255) NOT NULL,
  unidade_medida VARCHAR(16) NOT NULL DEFAULT 'UN',
  estoque_minimo NUMERIC(14, 3) NOT NULL DEFAULT 0,
  controla_validade BOOLEAN NOT NULL DEFAULT TRUE,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lotes (
  id BIGSERIAL PRIMARY KEY,
  produto_id BIGINT NOT NULL REFERENCES produtos (id) ON DELETE PROTECT,
  fornecedor_id BIGINT NOT NULL REFERENCES fornecedores (id) ON DELETE PROTECT,
  codigo_lote VARCHAR(80) NOT NULL,
  data_validade DATE NULL,
  quantidade_atual NUMERIC(14, 3) NOT NULL DEFAULT 0,
  criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lote_prod_valid ON lotes (produto_id, data_validade);

CREATE TABLE IF NOT EXISTS tipos_movimentacao (
  id BIGSERIAL PRIMARY KEY,
  codigo VARCHAR(32) NOT NULL UNIQUE,
  nome VARCHAR(120) NOT NULL
);

-- A tabela `usuarios` e tabelas de grupos/permissoes são geridas pelo Django (AUTH_USER_MODEL).
-- Campos típicos: password, is_superuser, email (único), nome, perfil_id, criado_em, etc.

CREATE TABLE IF NOT EXISTS movimentacoes (
  id BIGSERIAL PRIMARY KEY,
  lote_id BIGINT NOT NULL REFERENCES lotes (id) ON DELETE PROTECT,
  usuario_id BIGINT NOT NULL,
  tipo_movimentacao_id BIGINT NOT NULL REFERENCES tipos_movimentacao (id) ON DELETE PROTECT,
  quantidade NUMERIC(14, 3) NOT NULL,
  data_movimento DATE NOT NULL,
  observacao TEXT NOT NULL DEFAULT '',
  criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS danfes (
  id BIGSERIAL PRIMARY KEY,
  fornecedor_id BIGINT NOT NULL REFERENCES fornecedores (id) ON DELETE PROTECT,
  usuario_id BIGINT NOT NULL,
  numero INTEGER NOT NULL CHECK (numero >= 0),
  serie INTEGER NOT NULL CHECK (serie >= 0),
  chave_44 VARCHAR(44) NOT NULL UNIQUE,
  data_emissao DATE NULL,
  data_vencimento DATE NULL,
  valor_total NUMERIC(14, 2) NOT NULL DEFAULT 0,
  adicionado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT chk_chave_44_digits CHECK (chave_44 ~ '^[0-9]{44}$')
);

CREATE TABLE IF NOT EXISTS danfe_itens (
  id BIGSERIAL PRIMARY KEY,
  danfe_id BIGINT NOT NULL REFERENCES danfes (id) ON DELETE CASCADE,
  produto_id BIGINT NOT NULL REFERENCES produtos (id) ON DELETE PROTECT,
  lote_id BIGINT NULL REFERENCES lotes (id) ON DELETE SET NULL,
  quantidade NUMERIC(14, 3) NOT NULL,
  valor_unitario NUMERIC(14, 4) NOT NULL DEFAULT 0,
  valor_item NUMERIC(14, 2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS inventarios (
  id BIGSERIAL PRIMARY KEY,
  usuario_id BIGINT NOT NULL,
  data_inventario DATE NOT NULL,
  observacao TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS inventario_itens (
  id BIGSERIAL PRIMARY KEY,
  inventario_id BIGINT NOT NULL REFERENCES inventarios (id) ON DELETE CASCADE,
  produto_id BIGINT NOT NULL REFERENCES produtos (id) ON DELETE PROTECT,
  quantidade_sistema NUMERIC(14, 3) NOT NULL,
  quantidade_contada NUMERIC(14, 3) NOT NULL,
  quantidade_diferenca NUMERIC(14, 3) NOT NULL DEFAULT 0,
  observacao TEXT NOT NULL DEFAULT ''
);

COMMIT;
