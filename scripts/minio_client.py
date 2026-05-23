"""Cliente MinIO reutilizável."""
from io import BytesIO
from pathlib import Path

from minio import Minio
from minio.error import S3Error

from config import (
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    MINIO_SECURE,
)


def get_client() -> Minio:
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )


def ensure_bucket(client: Minio | None = None) -> None:
    client = client or get_client()
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)


def upload_file(local_path: Path, object_name: str, client: Minio | None = None) -> str:
    client = client or get_client()
    ensure_bucket(client)
    client.fput_object(MINIO_BUCKET, object_name, str(local_path))
    return object_name


def upload_bytes(data: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
    client = get_client()
    ensure_bucket(client)
    client.put_object(
        MINIO_BUCKET,
        object_name,
        BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return object_name


def download_to_path(object_name: str, local_path: Path) -> Path:
    client = get_client()
    local_path.parent.mkdir(parents=True, exist_ok=True)
    client.fget_object(MINIO_BUCKET, object_name, str(local_path))
    return local_path


def object_exists(object_name: str) -> bool:
    try:
        client = get_client()
        client.stat_object(MINIO_BUCKET, object_name)
        return True
    except (S3Error, Exception):
        return False
