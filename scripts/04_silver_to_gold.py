"""Silver → Gold: agregações SUS e base para sentimento Instagram."""
from io import BytesIO
from pathlib import Path

import pandas as pd

from config import DATA_SAMPLE_DIR
from minio_client import upload_bytes

GOLD_SUS_AGG = "gold/sus_agregados/agregado_mensal.parquet"
GOLD_SUS_FACT = "gold/sus_agregados/fato_grao.parquet"
GOLD_IG_BASE = "gold/instagram_base/comentarios_prata.parquet"


def main() -> None:
    sus = pd.read_parquet(Path(DATA_SAMPLE_DIR) / "silver_sus.parquet")
    ig = pd.read_parquet(Path(DATA_SAMPLE_DIR) / "silver_instagram.parquet")

    agg = (
        sus.groupby(
            ["ano_mes", "especialidade_padrao", "municipio_residencia", "faixa_etaria", "sexo", "capital_interior"],
            as_index=False,
        )
        .agg(qtd_internacoes=("numero_internacoes", "sum"))
        .sort_values("qtd_internacoes", ascending=False)
    )

    fato_grao = sus[
        [
            "data_internacao",
            "ano",
            "mes",
            "ano_mes",
            "trimestre",
            "especialidade_padrao",
            "grupo_especialidade",
            "municipio_residencia",
            "codigo_municipio_ibge",
            "capital_interior",
            "idade",
            "faixa_etaria",
            "sexo",
            "numero_internacoes",
        ]
    ].copy()

    out = Path(DATA_SAMPLE_DIR)
    agg.to_parquet(out / "gold_sus_agregado.parquet", index=False)
    fato_grao.to_parquet(out / "gold_sus_fato_grao.parquet", index=False)
    ig.to_parquet(out / "gold_instagram_base.parquet", index=False)

    for obj, df in [
        (GOLD_SUS_AGG, agg),
        (GOLD_SUS_FACT, fato_grao),
        (GOLD_IG_BASE, ig),
    ]:
        buf = BytesIO()
        df.to_parquet(buf, index=False)
        try:
            upload_bytes(buf.getvalue(), obj)
        except Exception:
            pass

    print(f"Gold SUS agregado: {len(agg)} linhas")
    print(f"Gold SUS fato grão: {len(fato_grao)} linhas")
    print(f"Gold Instagram base: {len(ig)} linhas")


if __name__ == "__main__":
    main()
