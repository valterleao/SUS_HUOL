"""Análise de sentimento e termos frequentes (Instagram)."""
import re
from collections import Counter
from io import BytesIO
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from config import DATA_SAMPLE_DIR
from minio_client import upload_bytes

GOLD_SENT_OBJ = "gold/instagram_sentiment/comentarios_sentimento.parquet"

POS = {
    "excelente", "bom", "boa", "otimo", "ótimo", "parabens", "parabéns", "obrigada", "obrigado",
    "gratidao", "gratidão", "recomendo", "humanizado", "atenciosa", "competente", "qualidade",
    "impecavel", "impecável", "eficiente", "dedicados", "salvou", "melhor", "referencia", "referência",
}
NEG = {
    "pessima", "péssima", "horrivel", "horrível", "ruim", "demora", "lento", "falta", "nunca",
    "desorganizacao", "desorganização", "fila", "enorme", "atraso", "gostei", "limpeza",
}
NEG.discard("gostei")


def tokenizar(texto: str) -> list[str]:
    texto = texto.lower()
    texto = re.sub(r"[^\w\sáàâãéèêíïóôõöúç]", " ", texto)
    return [t for t in texto.split() if len(t) > 2]


def classificar_sentimento(texto: str) -> tuple[str, float]:
    tokens = tokenizar(texto)
    if not tokens:
        return "neutro", 0.0
    pos = sum(1 for t in tokens if t in POS or any(p in t for p in POS))
    neg = sum(1 for t in tokens if t in NEG or any(n in t for n in NEG))
    if "nao gostei" in texto.lower() or "não gostei" in texto.lower():
        neg += 2
    if "nem bom nem ruim" in texto.lower() or "normal" in tokens:
        return "neutro", 0.0
    score = (pos - neg) / max(len(tokens), 1)
    if score > 0.15:
        return "positivo", round(min(score, 1.0), 3)
    if score < -0.15:
        return "negativo", round(max(score, -1.0), 3)
    return "neutro", round(score, 3)


def top_termos_por_sentimento(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    rows = []
    for sent in ["positivo", "negativo", "neutro"]:
        textos = df.loc[df["sentimento"] == sent, "texto_limpo"].tolist()
        if len(textos) < 2:
            continue
        vec = TfidfVectorizer(max_features=top_n, stop_words=list(POS | NEG | {"que", "mas", "com", "para", "uma", "muito"}))
        try:
            mat = vec.fit_transform(textos)
            terms = vec.get_feature_names_out()
            scores = mat.sum(axis=0).A1
            for term, sc in sorted(zip(terms, scores), key=lambda x: -x[1])[:top_n]:
                rows.append({"sentimento": sent, "termo": term, "score_tfidf": float(sc)})
        except ValueError:
            pass
    return pd.DataFrame(rows)


def main() -> None:
    ig = pd.read_parquet(Path(DATA_SAMPLE_DIR) / "gold_instagram_base.parquet")
    resultados = []
    for _, row in ig.iterrows():
        sent, score = classificar_sentimento(row["texto_limpo"])
        tokens = tokenizar(row["texto_limpo"])
        resultados.append(
            {
                **row.to_dict(),
                "sentimento": sent,
                "score_sentimento": score,
                "tokens": " ".join(tokens[:30]),
                "qtd_tokens": len(tokens),
            }
        )
    df = pd.DataFrame(resultados)
    termos = top_termos_por_sentimento(df)

    out = Path(DATA_SAMPLE_DIR)
    df.to_parquet(out / "gold_instagram_sentiment.parquet", index=False)
    termos.to_csv(out / "gold_termos_frequentes.csv", index=False, encoding="utf-8-sig", sep=";")

    buf = BytesIO()
    df.to_parquet(buf, index=False)
    try:
        upload_bytes(buf.getvalue(), GOLD_SENT_OBJ)
    except Exception:
        pass

    dist = df["sentimento"].value_counts()
    print("Distribuição sentimento:")
    print(dist.to_string())
    print(f"Termos salvos: {out / 'gold_termos_frequentes.csv'}")


if __name__ == "__main__":
    main()
