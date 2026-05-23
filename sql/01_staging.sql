-- Staging: dados silver antes do modelo OLAP
CREATE SCHEMA IF NOT EXISTS staging;

DROP TABLE IF EXISTS staging.stg_internacoes CASCADE;
CREATE TABLE staging.stg_internacoes (
    id_carga BIGSERIAL PRIMARY KEY,
    data_internacao DATE NOT NULL,
    especialidade_hospitalar TEXT,
    especialidade_padrao TEXT NOT NULL,
    grupo_especialidade TEXT,
    numero_internacoes INTEGER NOT NULL DEFAULT 1,
    municipio_residencia TEXT NOT NULL,
    codigo_municipio_ibge TEXT,
    idade INTEGER,
    faixa_etaria TEXT NOT NULL,
    sexo TEXT NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    ano_mes TEXT NOT NULL,
    trimestre INTEGER NOT NULL,
    capital_interior TEXT NOT NULL
);

DROP TABLE IF EXISTS staging.stg_comentarios_instagram CASCADE;
CREATE TABLE staging.stg_comentarios_instagram (
    id_carga BIGSERIAL PRIMARY KEY,
    comment_id TEXT NOT NULL,
    post_id TEXT,
    autor TEXT,
    data_comentario DATE,
    curtidas INTEGER DEFAULT 0,
    texto_original TEXT,
    texto_limpo TEXT,
    sentimento TEXT NOT NULL,
    score_sentimento NUMERIC(6,3),
    tokens TEXT,
    qtd_tokens INTEGER
);
