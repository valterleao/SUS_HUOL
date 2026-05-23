-- Executar modelo completo (após pipeline Python)
-- psql -h localhost -U postgres -d SUS_HUOL -f sql/00_executar_tudo.sql

\set ON_ERROR_STOP on
\echo 'Use scripts/run_pipeline.py para carga automatizada.'
\i sql/01_staging.sql
