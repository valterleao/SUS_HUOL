"""Carrega silver/gold no PostgreSQL e executa modelo OLAP."""
import subprocess
import sys
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from config import PG_DATABASE, PG_HOST, PG_PASSWORD, PG_PORT, PG_USER, DATA_SAMPLE_DIR, ROOT

SQL_DIR = ROOT / "sql"


def get_conn():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD,
    )


def ensure_database():
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname="postgres", user=PG_USER, password=PG_PASSWORD
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DATABASE,))
    if not cur.fetchone():
        cur.execute(f'CREATE DATABASE "{PG_DATABASE}"')
        print(f"Banco {PG_DATABASE} criado.")
    cur.close()
    conn.close()


def run_sql_file(conn, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"OK: {path.name}")


def _clean_tuples(df: pd.DataFrame):
    df = df.where(pd.notna(df), None)
    rows = []
    for row in df.itertuples(index=False, name=None):
        rows.append(tuple(None if (isinstance(v, float) and pd.isna(v)) else v for v in row))
    return rows


def load_csv_to_staging(conn) -> None:
    sus = pd.read_parquet(Path(DATA_SAMPLE_DIR) / "silver_sus.parquet")
    ig = pd.read_parquet(Path(DATA_SAMPLE_DIR) / "gold_instagram_sentiment.parquet")

    sus_cols = [
        "data_internacao", "especialidade_hospitalar", "especialidade_padrao",
        "grupo_especialidade", "numero_internacoes", "municipio_residencia",
        "codigo_municipio_ibge", "idade", "faixa_etaria", "sexo",
        "ano", "mes", "ano_mes", "trimestre", "capital_interior",
    ]
    sus_db = sus[sus_cols].copy()
    sus_db["data_internacao"] = pd.to_datetime(sus_db["data_internacao"]).dt.date
    sus_db["idade"] = sus_db["idade"].apply(lambda x: int(x) if pd.notna(x) else None)
    sus_db["numero_internacoes"] = sus_db["numero_internacoes"].astype(int)

    with conn.cursor() as cur:
        cur.execute("TRUNCATE staging.stg_internacoes RESTART IDENTITY CASCADE")
        tuples = _clean_tuples(sus_db)
        execute_values(
            cur,
            """INSERT INTO staging.stg_internacoes (
                data_internacao, especialidade_hospitalar, especialidade_padrao,
                grupo_especialidade, numero_internacoes, municipio_residencia,
                codigo_municipio_ibge, idade, faixa_etaria, sexo,
                ano, mes, ano_mes, trimestre, capital_interior
            ) VALUES %s""",
            tuples,
            page_size=500,
        )
        cur.execute("TRUNCATE staging.stg_comentarios_instagram RESTART IDENTITY CASCADE")
        ig_cols = [
            "comment_id", "post_id", "autor", "data_comentario",
            "curtidas", "texto_original", "texto_limpo", "sentimento",
            "score_sentimento", "tokens", "qtd_tokens",
        ]
        ig_db = ig[ig_cols].copy()
        ig_db["data_comentario"] = pd.to_datetime(ig_db["data_comentario"], errors="coerce").dt.date
        ig_db["curtidas"] = ig_db["curtidas"].astype(int)
        ig_db["qtd_tokens"] = ig_db["qtd_tokens"].astype(int)
        tuples_ig = _clean_tuples(ig_db)
        execute_values(
            cur,
            """INSERT INTO staging.stg_comentarios_instagram (
                comment_id, post_id, autor, data_comentario, curtidas,
                texto_original, texto_limpo, sentimento, score_sentimento, tokens, qtd_tokens
            ) VALUES %s""",
            tuples_ig,
        )
    conn.commit()
    print(f"Staging: {len(sus_db)} internações, {len(ig_db)} comentários.")


def main() -> None:
    ensure_database()
    conn = get_conn()
    for f in ["01_staging.sql", "03_criar_modelo_olap.sql", "04_criar_views_dashboard.sql", "05_termos_instagram.sql"]:
        run_sql_file(conn, SQL_DIR / f)
    load_csv_to_staging(conn)
    run_sql_file(conn, SQL_DIR / "03_criar_modelo_olap.sql")
    run_sql_file(conn, SQL_DIR / "04_criar_views_dashboard.sql")
    run_sql_file(conn, SQL_DIR / "05_termos_instagram.sql")
    conn.close()
    print("PostgreSQL carregado com sucesso.")


if __name__ == "__main__":
    main()
