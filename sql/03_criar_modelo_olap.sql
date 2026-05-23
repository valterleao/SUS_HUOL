-- Modelo estrela OLAP - internações HUOL
CREATE SCHEMA IF NOT EXISTS olap;

DROP TABLE IF EXISTS olap.fato_internacao CASCADE;
DROP TABLE IF EXISTS olap.fato_sentimento_comentario CASCADE;
DROP TABLE IF EXISTS olap.dim_municipio CASCADE;
DROP TABLE IF EXISTS olap.dim_paciente CASCADE;
DROP TABLE IF EXISTS olap.dim_especialidade CASCADE;
DROP TABLE IF EXISTS olap.dim_tempo CASCADE;

CREATE TABLE olap.dim_tempo AS
SELECT
    ROW_NUMBER() OVER (ORDER BY d.data_internacao)::INTEGER AS id_tempo,
    d.data_internacao,
    d.ano,
    d.mes,
    d.trimestre,
    d.ano_mes,
    TO_CHAR(d.data_internacao, 'TMMonth') AS nome_mes,
    CASE d.mes
        WHEN 12 THEN 'Verão'
        WHEN 1 THEN 'Verão'
        WHEN 2 THEN 'Verão'
        WHEN 3 THEN 'Outono'
        WHEN 4 THEN 'Outono'
        WHEN 5 THEN 'Outono'
        WHEN 6 THEN 'Inverno'
        WHEN 7 THEN 'Inverno'
        WHEN 8 THEN 'Inverno'
        ELSE 'Primavera'
    END AS estacao_br
FROM (
    SELECT DISTINCT
        data_internacao,
        ano,
        mes,
        trimestre,
        ano_mes
    FROM staging.stg_internacoes
) d;

ALTER TABLE olap.dim_tempo ADD PRIMARY KEY (id_tempo);
CREATE UNIQUE INDEX ux_dim_tempo_data ON olap.dim_tempo (data_internacao);

CREATE TABLE olap.dim_especialidade AS
SELECT
    ROW_NUMBER() OVER (ORDER BY e.especialidade_padrao)::INTEGER AS id_especialidade,
    e.especialidade_padrao,
    e.grupo_especialidade
FROM (
    SELECT DISTINCT especialidade_padrao, grupo_especialidade
    FROM staging.stg_internacoes
) e;

ALTER TABLE olap.dim_especialidade ADD PRIMARY KEY (id_especialidade);
CREATE UNIQUE INDEX ux_dim_esp ON olap.dim_especialidade (especialidade_padrao);

CREATE TABLE olap.dim_paciente AS
SELECT
    ROW_NUMBER() OVER (ORDER BY p.faixa_etaria, p.sexo, p.idade)::INTEGER AS id_paciente,
    p.faixa_etaria,
    p.sexo,
    p.idade
FROM (
    SELECT DISTINCT faixa_etaria, sexo, COALESCE(idade, -1) AS idade
    FROM staging.stg_internacoes
) p;

ALTER TABLE olap.dim_paciente ADD PRIMARY KEY (id_paciente);

CREATE TABLE olap.dim_municipio AS
SELECT
    ROW_NUMBER() OVER (ORDER BY m.municipio_residencia)::INTEGER AS id_municipio,
    m.municipio_residencia,
    m.codigo_municipio_ibge,
    m.capital_interior,
    'RN' AS uf
FROM (
    SELECT DISTINCT municipio_residencia, codigo_municipio_ibge, capital_interior
    FROM staging.stg_internacoes
) m;

ALTER TABLE olap.dim_municipio ADD PRIMARY KEY (id_municipio);
CREATE UNIQUE INDEX ux_dim_mun ON olap.dim_municipio (municipio_residencia);

CREATE TABLE olap.fato_internacao AS
SELECT
    t.id_tempo,
    e.id_especialidade,
    p.id_paciente,
    m.id_municipio,
    SUM(s.numero_internacoes)::INTEGER AS qtd_internacoes
FROM staging.stg_internacoes s
JOIN olap.dim_tempo t ON t.data_internacao = s.data_internacao
JOIN olap.dim_especialidade e ON e.especialidade_padrao = s.especialidade_padrao
JOIN olap.dim_paciente p
    ON p.faixa_etaria = s.faixa_etaria
   AND p.sexo = s.sexo
   AND p.idade = COALESCE(s.idade, -1)
JOIN olap.dim_municipio m ON m.municipio_residencia = s.municipio_residencia
GROUP BY t.id_tempo, e.id_especialidade, p.id_paciente, m.id_municipio;

ALTER TABLE olap.fato_internacao
    ADD CONSTRAINT pk_fato_internacao PRIMARY KEY (id_tempo, id_especialidade, id_paciente, id_municipio);

CREATE TABLE olap.fato_sentimento_comentario AS
SELECT
    ROW_NUMBER() OVER (ORDER BY c.comment_id)::INTEGER AS id_comentario,
    c.comment_id,
    c.post_id,
    c.autor,
    c.data_comentario,
    c.curtidas,
    c.texto_original,
    c.texto_limpo,
    c.sentimento,
    c.score_sentimento,
    c.tokens,
    c.qtd_tokens
FROM staging.stg_comentarios_instagram c;

ALTER TABLE olap.fato_sentimento_comentario ADD PRIMARY KEY (id_comentario);
