# AV2 — Data Lake Saúde (HUOL / SUS)

Sistema de análise integrando internações SUS (estruturado) e Instagram @huol_ufrn (não estruturado) para apoio à decisão de credenciamento SUS.

## Stack

- Python 3.10+
- MinIO (Docker, opcional)
- PostgreSQL — banco **`SUS_HUOL`** (host `localhost`, usuário `postgres`, senha `123456`)
- Power BI

## Execução rápida

```powershell
cd h:\UNI7\SAD-Lina\AV2-TRABALHO-2-SUS
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python scripts\run_pipeline.py
```

## Dados reais

1. Baixe CSV em [dados.gov.br — internações hospitalares](https://dados.gov.br/dados/conjuntos-dados/06-internacoes-hospitalares) (jan/2024–dez/2025).
2. Coloque em `data/raw/sus/`.
3. Reexecute o pipeline.

## MinIO (opcional)

```powershell
docker compose -f docker/docker-compose.minio.yml up -d
```

Console: http://localhost:9001 (minioadmin / minioadmin)

## Documentação do trabalho

Ver [`docs/TRABALHO_AV2_SUS_HUOL.md`](docs/TRABALHO_AV2_SUS_HUOL.md).
