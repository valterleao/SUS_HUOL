"""Bronze → Silver (Parquet local + MinIO quando disponível)."""
from io import BytesIO
from pathlib import Path

import pandas as pd

from config import DATA_SAMPLE_DIR
from minio_client import download_to_path, get_client, object_exists, upload_bytes
from transforms import transform_instagram_silver, transform_sus_silver

SILVER_SUS_OBJ = "silver/sus_internacoes/data.parquet"
SILVER_IG_OBJ = "silver/instagram_comments/data.parquet"


def ler_bronze_sus() -> pd.DataFrame:
    local = [
        Path(DATA_SAMPLE_DIR) / "bronze_sus_internacoes.csv",
        Path(DATA_SAMPLE_DIR) / "internacoes_huol_2024_2025.csv",
    ]
    for p in local:
        if p.exists():
            return pd.read_csv(p, sep=";", encoding="utf-8-sig", low_memory=False)
    try:
        if object_exists("bronze/sus_internacoes/internacoes.csv"):
            tmp = Path(DATA_SAMPLE_DIR) / "_tmp_bronze_sus.csv"
            download_to_path("bronze/sus_internacoes/internacoes.csv", tmp)
            return pd.read_csv(tmp, sep=";", encoding="utf-8-sig", low_memory=False)
    except Exception:
        pass
    raise FileNotFoundError("Bronze SUS não encontrado. Execute 01_ingest_sus.py")


def ler_bronze_ig() -> pd.DataFrame:
    local = [
        Path(DATA_SAMPLE_DIR) / "bronze_instagram_comments.csv",
        Path(DATA_SAMPLE_DIR) / "instagram_comentarios_huol.csv",
    ]
    for p in local:
        if p.exists():
            return pd.read_csv(p, sep=";", encoding="utf-8-sig")
    try:
        if object_exists("bronze/instagram_comments/comentarios.csv"):
            tmp = Path(DATA_SAMPLE_DIR) / "_tmp_bronze_ig.csv"
            download_to_path("bronze/instagram_comments/comentarios.csv", tmp)
            return pd.read_csv(tmp, sep=";", encoding="utf-8-sig", low_memory=False)
    except Exception:
        pass
    raise FileNotFoundError("Bronze Instagram não encontrado.")


def salvar_parquet(df: pd.DataFrame, local_path: Path, object_name: str) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(local_path, index=False)
    buf = BytesIO()
    df.to_parquet(buf, index=False)
    try:
        upload_bytes(buf.getvalue(), object_name, "application/octet-stream")
    except Exception:
        pass
    print(f"Silver: {local_path} ({len(df)} linhas)")


def main() -> None:
    sus = transform_sus_silver(ler_bronze_sus())
    ig = transform_instagram_silver(ler_bronze_ig())
    salvar_parquet(sus, Path(DATA_SAMPLE_DIR) / "silver_sus.parquet", SILVER_SUS_OBJ)
    salvar_parquet(ig, Path(DATA_SAMPLE_DIR) / "silver_instagram.parquet", SILVER_IG_OBJ)


if __name__ == "__main__":
    main()
