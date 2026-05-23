-- Views para Power BI e perguntas de negócio

-- Q1: Especialidades com mais internações
CREATE OR REPLACE VIEW olap.vw_top_especialidades AS
SELECT
    e.especialidade_padrao,
    e.grupo_especialidade,
    SUM(f.qtd_internacoes) AS total_internacoes,
    RANK() OVER (ORDER BY SUM(f.qtd_internacoes) DESC) AS ranking
FROM olap.fato_internacao f
JOIN olap.dim_especialidade e ON e.id_especialidade = f.id_especialidade
GROUP BY e.especialidade_padrao, e.grupo_especialidade
ORDER BY total_internacoes DESC;

-- Q2: Perfil etário e gênero
CREATE OR REPLACE VIEW olap.vw_perfil_paciente AS
SELECT
    p.faixa_etaria,
    p.sexo,
    SUM(f.qtd_internacoes) AS total_internacoes,
    ROUND(100.0 * SUM(f.qtd_internacoes) / SUM(SUM(f.qtd_internacoes)) OVER (), 2) AS pct_total
FROM olap.fato_internacao f
JOIN olap.dim_paciente p ON p.id_paciente = f.id_paciente
GROUP BY p.faixa_etaria, p.sexo
ORDER BY total_internacoes DESC;

-- Q3: Padrão por município
CREATE OR REPLACE VIEW olap.vw_internacoes_municipio AS
SELECT
    m.municipio_residencia,
    m.capital_interior,
    m.uf,
    SUM(f.qtd_internacoes) AS total_internacoes,
    ROUND(100.0 * SUM(f.qtd_internacoes) / SUM(SUM(f.qtd_internacoes)) OVER (), 2) AS pct_total
FROM olap.fato_internacao f
JOIN olap.dim_municipio m ON m.id_municipio = f.id_municipio
GROUP BY m.municipio_residencia, m.capital_interior, m.uf
ORDER BY total_internacoes DESC;

-- Q4: Sazonalidade 2024-2025
CREATE OR REPLACE VIEW olap.vw_sazonalidade_mensal AS
SELECT
    t.ano,
    t.mes,
    t.ano_mes,
    t.nome_mes,
    t.estacao_br,
    SUM(f.qtd_internacoes) AS total_internacoes
FROM olap.fato_internacao f
JOIN olap.dim_tempo t ON t.id_tempo = f.id_tempo
GROUP BY t.ano, t.mes, t.ano_mes, t.nome_mes, t.estacao_br
ORDER BY t.ano, t.mes;

-- Q5: O que dizem sobre o hospital (amostra + termos)
CREATE OR REPLACE VIEW olap.vw_comentarios_amostra AS
SELECT
    comment_id,
    data_comentario,
    autor,
    curtidas,
    sentimento,
    LEFT(texto_limpo, 200) AS texto_resumo
FROM olap.fato_sentimento_comentario
ORDER BY data_comentario DESC, curtidas DESC;

-- Q6: Sentimento predominante
CREATE OR REPLACE VIEW olap.vw_sentimento_distribuicao AS
SELECT
    sentimento,
    COUNT(*) AS qtd_comentarios,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_comentarios,
    ROUND(AVG(score_sentimento)::NUMERIC, 3) AS score_medio
FROM olap.fato_sentimento_comentario
GROUP BY sentimento
ORDER BY qtd_comentarios DESC;

-- View integrada para decisão
CREATE OR REPLACE VIEW olap.vw_resumo_decisao AS
SELECT
    (SELECT SUM(qtd_internacoes) FROM olap.fato_internacao) AS total_internacoes_huol,
    (SELECT especialidade_padrao FROM olap.vw_top_especialidades LIMIT 1) AS especialidade_lider,
    (SELECT municipio_residencia FROM olap.vw_internacoes_municipio LIMIT 1) AS municipio_lider,
    (SELECT sentimento FROM olap.vw_sentimento_distribuicao ORDER BY qtd_comentarios DESC LIMIT 1) AS sentimento_predominante,
    (SELECT ROUND(pct_comentarios, 1) FROM olap.vw_sentimento_distribuicao WHERE sentimento = 'positivo') AS pct_positivo,
    (SELECT ROUND(pct_comentarios, 1) FROM olap.vw_sentimento_distribuicao WHERE sentimento = 'negativo') AS pct_negativo;
