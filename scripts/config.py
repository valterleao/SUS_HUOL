"""Configuração central do projeto AV2 SUS HUOL."""
from pathlib import Path
import os

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

DATA_RAW_DIR = Path(os.getenv("DATA_RAW_DIR", ROOT / "data" / "raw"))
DATA_SAMPLE_DIR = Path(os.getenv("DATA_SAMPLE_DIR", ROOT / "data" / "sample"))

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "sus-huol")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_DATABASE = os.getenv("PG_DATABASE", "SUS_HUOL")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "123456")

# HUOL - Hospital Universitário Onofre Lopes (UFRN), Natal/RN
HUOL_CNES = "2338179"
HUOL_NOME = "HOSPITAL UNIVERSITARIO ONOFRE LOPES"

INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID", "")

BRONZE_PREFIX = "bronze"
SILVER_PREFIX = "silver"
GOLD_PREFIX = "gold"
