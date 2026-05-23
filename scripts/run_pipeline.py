"""Executa pipeline completo AV2 SUS HUOL."""
import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "00_generate_sample_data.py",
    "01_ingest_sus.py",
    "02_ingest_instagram.py",
    "03_bronze_to_silver.py",
    "04_silver_to_gold.py",
    "05_sentiment_analysis.py",
    "06_load_postgres.py",
]


def main() -> None:
    base = Path(__file__).parent
    for name in SCRIPTS:
        path = base / name
        print(f"\n{'='*60}\n>>> {name}\n{'='*60}")
        r = subprocess.run([sys.executable, str(path)], cwd=str(base))
        if r.returncode != 0:
            print(f"Falha em {name} (código {r.returncode})")
            if name == "06_load_postgres.py":
                sys.exit(r.returncode)
    print("\nPipeline concluído.")


if __name__ == "__main__":
    main()
