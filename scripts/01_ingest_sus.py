"""Ingestão bronze SUS: data/raw ou data/sample → MinIO."""
from datetime import datetime
from hashlib import md5
from pathlib import Path

import pandas as pd

from config import DATA_RAW_DIR, DATA_SAMPLE_DIR
from minio_client import ensure_bucket, get_client, upload_file

BRONZE_OBJ = "bronze/sus_internacoes/internacoes.csv"


def localizar_csv() -> Path:
    raw_dir = Path(DATA_RAW_DIR) / "sus"
    if raw_dir.exists():
        csvs = list(raw_dir.glob("*.csv"))
        if csvs:
            return csvs[0]
    sample = Path(DATA_SAMPLE_DIR) / "internacoes_huol_2024_2025.csv"
    if sample.exists():
        return sample
    raise FileNotFoundError(
        "Coloque CSV em data/raw/sus/ ou execute scripts/00_generate_sample_data.py"
    )


def main() -> None:
    path = localizar_csv()
    h = md5(path.read_bytes()).hexdigest()
    meta_path = Path(DATA_SAMPLE_DIR) / "_bronze_sus_meta.txt"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(
        f"ingested_at={datetime.utcnow().isoformat()}\nsource={path}\nfile_hash={h}\n",
        encoding="utf-8",
    )
    client = get_client()
    try:
        ensure_bucket(client)
        upload_file(path, BRONZE_OBJ, client)
        print(f"Bronze SUS enviado: {BRONZE_OBJ}")
    except Exception as e:
        local_bronze = Path(DATA_SAMPLE_DIR) / "bronze_sus_internacoes.csv"
        pd.read_csv(path, sep=";", encoding="utf-8-sig", low_memory=False).to_csv(
            local_bronze, index=False, encoding="utf-8-sig", sep=";"
        )
        print(f"MinIO indisponível ({e}). Bronze local: {local_bronze}")


if __name__ == "__main__":
    main()
