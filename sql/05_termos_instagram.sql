-- Termos frequentes por sentimento (carregados via script ou view derivada)
CREATE SCHEMA IF NOT EXISTS olap;

DROP TABLE IF EXISTS olap.dim_termo_sentimento CASCADE;
CREATE TABLE olap.dim_termo_sentimento (
    id_termo SERIAL PRIMARY KEY,
    sentimento TEXT NOT NULL,
    termo TEXT NOT NULL,
    score_tfidf NUMERIC(12,6)
);

-- População a partir de tokens nos comentários
TRUNCATE olap.dim_termo_sentimento RESTART IDENTITY;
INSERT INTO olap.dim_termo_sentimento (sentimento, termo, score_tfidf)
SELECT sentimento, termo, COUNT(*)::NUMERIC
FROM (
    SELECT
        c.sentimento,
        unnest(string_to_array(lower(c.tokens), ' ')) AS termo
    FROM olap.fato_sentimento_comentario c
    WHERE c.tokens IS NOT NULL AND length(trim(c.tokens)) > 0
) x
WHERE length(termo) > 3
  AND termo NOT IN ('que', 'mas', 'com', 'para', 'uma', 'muito', 'mais', 'sobre', 'este', 'essa')
GROUP BY sentimento, termo
ORDER BY COUNT(*) DESC
LIMIT 45;

CREATE OR REPLACE VIEW olap.vw_termos_frequentes AS
SELECT sentimento, termo, score_tfidf,
       RANK() OVER (PARTITION BY sentimento ORDER BY score_tfidf DESC) AS rank_termo
FROM olap.dim_termo_sentimento
ORDER BY sentimento, score_tfidf DESC;
