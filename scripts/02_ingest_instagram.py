"""Ingestão bronze Instagram: API (token) ou amostra local → MinIO."""
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

from config import DATA_SAMPLE_DIR, INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID
from minio_client import ensure_bucket, get_client, upload_bytes, upload_file

BRONZE_OBJ = "bronze/instagram_comments/comentarios.csv"


def coletar_api() -> pd.DataFrame | None:
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_USER_ID:
        return None
    base = "https://graph.facebook.com/v19.0"
    media_url = f"{base}/{INSTAGRAM_USER_ID}/media"
    params = {"fields": "id,caption,timestamp", "access_token": INSTAGRAM_ACCESS_TOKEN}
    try:
        media_resp = requests.get(media_url, params=params, timeout=30)
        media_resp.raise_for_status()
        posts = media_resp.json().get("data", [])[:10]
        rows = []
        for post in posts:
            pid = post["id"]
            comm_url = f"{base}/{pid}/comments"
            comm_resp = requests.get(
                comm_url,
                params={"fields": "id,text,username,timestamp,like_count", "access_token": INSTAGRAM_ACCESS_TOKEN},
                timeout=30,
            )
            if comm_resp.status_code != 200:
                continue
            for c in comm_resp.json().get("data", []):
                rows.append(
                    {
                        "comment_id": c["id"],
                        "post_id": pid,
                        "autor": c.get("username", ""),
                        "data_comentario": c.get("timestamp", "")[:10],
                        "curtidas": c.get("like_count", 0),
                        "texto_comentario": c.get("text", ""),
                    }
                )
        return pd.DataFrame(rows) if rows else None
    except Exception:
        return None


def coletar_local() -> pd.DataFrame:
    path = Path(DATA_SAMPLE_DIR) / "instagram_comentarios_huol.csv"
    if not path.exists():
        raise FileNotFoundError("Execute 00_generate_sample_data.py primeiro.")
    return pd.read_csv(path, sep=";", encoding="utf-8-sig")


def main() -> None:
    df = coletar_api()
    fonte = "instagram_graph_api"
    if df is None or df.empty:
        df = coletar_local()
        fonte = "coleta_manual_amostra"

    tmp = Path(DATA_SAMPLE_DIR) / "_bronze_instagram_tmp.csv"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(tmp, index=False, encoding="utf-8-sig", sep=";")

    meta = Path(DATA_SAMPLE_DIR) / "_bronze_instagram_meta.txt"
    meta.write_text(
        f"ingested_at={datetime.utcnow().isoformat()}\nsource={fonte}\nrows={len(df)}\n",
        encoding="utf-8",
    )

    try:
        ensure_bucket()
        upload_file(tmp, BRONZE_OBJ)
        print(f"Bronze Instagram ({fonte}): {len(df)} comentários → {BRONZE_OBJ}")
    except Exception as e:
        dest = Path(DATA_SAMPLE_DIR) / "bronze_instagram_comments.csv"
        df.to_csv(dest, index=False, encoding="utf-8-sig", sep=";")
        print(f"MinIO indisponível ({e}). Bronze local: {dest}")


if __name__ == "__main__":
    main()
