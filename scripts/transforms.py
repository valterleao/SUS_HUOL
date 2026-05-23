"""Transformações compartilhadas bronze → prata → ouro."""
import re
import unicodedata
from datetime import datetime

import pandas as pd
from unidecode import unidecode

ESPECIALIDADE_MAP = {
    "CLINICA MEDICA": "Clínica Médica",
    "Clinica Medica": "Clínica Médica",
    "CIRURGIA GERAL": "Cirurgia Geral",
    "PEDIATRIA": "Pediatria",
    "OBSTETRICIA": "Obstetrícia",
    "ORTOPEDIA": "Ortopedia",
    "CARDIOLOGIA": "Cardiologia",
    "NEUROLOGIA": "Neurologia",
    "UTI": "UTI",
    "INFECTOLOGIA": "Infectologia",
}

GRUPO_ESPECIALIDADE = {
    "Clínica Médica": "Clínico",
    "Cirurgia Geral": "Cirúrgico",
    "Pediatria": "Pediatria",
    "Obstetrícia": "Obstetrícia",
    "Ortopedia": "Ortopedia",
    "Cardiologia": "Clínico",
    "Neurologia": "Clínico",
    "UTI": "Terapia Intensiva",
    "Infectologia": "Clínico",
}

COL_SUS = {
    "data_internacao": "data_internacao",
    "data da internacao": "data_internacao",
    "especialidade_hospitalar": "especialidade_hospitalar",
    "especialidade hospitalar": "especialidade_hospitalar",
    "numero_internacoes": "numero_internacoes",
    "número de internações": "numero_internacoes",
    "municipio_residencia": "municipio_residencia",
    "município de residência": "municipio_residencia",
    "idade": "idade",
    "sexo_paciente": "sexo_paciente",
    "sexo do paciente": "sexo_paciente",
}


def normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    cols = {}
    for c in df.columns:
        key = unidecode(str(c).strip().lower())
        cols[c] = COL_SUS.get(key, re.sub(r"\s+", "_", key))
    return df.rename(columns=cols)


def faixa_etaria(idade) -> str:
    if pd.isna(idade):
        return "Não informado"
    i = int(idade)
    if i <= 17:
        return "0-17"
    if i <= 39:
        return "18-39"
    if i <= 59:
        return "40-59"
    return "60+"


def padronizar_sexo(valor) -> str:
    if pd.isna(valor):
        return "Não informado"
    v = str(valor).strip().upper()
    if v in ("M", "MASCULINO", "1"):
        return "Masculino"
    if v in ("F", "FEMININO", "2"):
        return "Feminino"
    return "Não informado"


def padronizar_especialidade(valor) -> str:
    if pd.isna(valor):
        return "Não informado"
    v = str(valor).strip()
    return ESPECIALIDADE_MAP.get(v, v.title())


def transform_sus_silver(df: pd.DataFrame) -> pd.DataFrame:
    df = normalizar_colunas(df.copy())
    df["data_internacao"] = pd.to_datetime(df["data_internacao"], errors="coerce")
    df = df.dropna(subset=["data_internacao"])
    df["especialidade_padrao"] = df["especialidade_hospitalar"].apply(padronizar_especialidade)
    df["grupo_especialidade"] = df["especialidade_padrao"].map(GRUPO_ESPECIALIDADE).fillna("Outros")
    df["faixa_etaria"] = df["idade"].apply(faixa_etaria)
    df["sexo"] = df["sexo_paciente"].apply(padronizar_sexo)
    df["municipio_residencia"] = df["municipio_residencia"].fillna("Não informado").astype(str).str.strip()
    if "codigo_municipio_ibge" not in df.columns:
        df["codigo_municipio_ibge"] = "0000000"
    df["codigo_municipio_ibge"] = df["codigo_municipio_ibge"].fillna("0000000").astype(str)
    df["numero_internacoes"] = pd.to_numeric(df["numero_internacoes"], errors="coerce").fillna(1).astype(int)
    df["ano"] = df["data_internacao"].dt.year
    df["mes"] = df["data_internacao"].dt.month
    df["ano_mes"] = df["data_internacao"].dt.strftime("%Y-%m")
    df["trimestre"] = ((df["mes"] - 1) // 3 + 1).astype(int)
    df["capital_interior"] = df["municipio_residencia"].apply(
        lambda m: "Capital" if "natal" in m.lower() else "Interior"
    )
    df["processed_at"] = datetime.utcnow().isoformat()
    return df


def limpar_texto_instagram(texto: str) -> str:
    if pd.isna(texto):
        return ""
    t = str(texto)
    t = re.sub(r"http\S+", "", t)
    t = re.sub(r"@\w+", "", t)
    t = re.sub(r"#\w+", "", t)
    t = re.sub(r"[^\w\sáàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ.,!?]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def transform_instagram_silver(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    rename = {
        "comment_id": "comment_id",
        "post_id": "post_id",
        "autor": "autor",
        "data_comentario": "data_comentario",
        "curtidas": "curtidas",
        "texto_comentario": "texto_comentario",
    }
    for old, new in rename.items():
        if old not in df.columns and new in df.columns:
            pass
    df = df.rename(columns={c: c for c in df.columns})
    required = ["comment_id", "post_id", "autor", "data_comentario", "curtidas", "texto_comentario"]
    for col in required:
        if col not in df.columns:
            df[col] = None
    df["texto_original"] = df["texto_comentario"].astype(str)
    df["texto_limpo"] = df["texto_original"].apply(limpar_texto_instagram)
    df["data_comentario"] = pd.to_datetime(df["data_comentario"], errors="coerce")
    df["curtidas"] = pd.to_numeric(df["curtidas"], errors="coerce").fillna(0).astype(int)
    df = df.drop_duplicates(subset=["comment_id"])
    df = df[df["texto_limpo"].str.len() >= 3]
    df["processed_at"] = datetime.utcnow().isoformat()
    return df
