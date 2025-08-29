# clinical_engine_backend_code/scripts/train_tfidf_recommender.py
# Build a lightweight TF-IDF model over your "drugs" table, store artifacts for fast recommendations.

import os
import sys
import re
import json
import pickle
from collections import Counter
from pathlib import Path
from datetime import datetime
import math

# --- Make sure Python can import `app.*` when this script runs from project root ---
# Adds: clinical_engine_backend/clinical_engine_backend_code to sys.path
THIS_FILE = Path(__file__).resolve()
CODE_ROOT = THIS_FILE.parents[1]  # clinical_engine_backend_code/
if str(CODE_ROOT) not in sys.path:
    sys.path.append(str(CODE_ROOT))

from app.database import SessionLocal
from app.models import Drug

# --- Artifacts location ---
ARTIFACT_DIR = CODE_ROOT / "artifacts"
ARTIFACT_DIR.mkdir(exist_ok=True, parents=True)

VOCAB_PKL = ARTIFACT_DIR / "vocab_idf.pkl"
DOCS_PKL  = ARTIFACT_DIR / "drugs_tfidf.pkl"
META_JSON = ARTIFACT_DIR / "model_meta.json"

TOKEN_RE = re.compile(r"[a-z]+")

def normalize(text: str | None) -> str:
    if not text:
        return ""
    return text.lower()

def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())

def build_corpus_row(d: Drug) -> tuple[str, str]:
    """
    Compose a textual profile for each drug from your columns.
    You can adjust the fields here to weight certain info more heavily.
    """
    parts = [
        d.name or "",
        d.description or "",
        d.side_effects or "",
        d.therapeutic_class or "",
        d.action_class or "",
        d.chemical_class or "",
        d.substitutes or "",
        d.habit_forming or "",
    ]
    joined = " ".join(p for p in parts if p)
    return (d.name or "").strip(), normalize(joined)

def main():
    session = SessionLocal()
    try:
        drugs = session.query(Drug).all()
        if not drugs:
            raise RuntimeError("No rows found in drugs table. Ingest drugs first.")

        # 1) Build corpus
        corpus: list[str] = []
        names: list[str] = []
        seen = set()
        for d in drugs:
            name, text = build_corpus_row(d)
            if not name:
                continue
            # skip duplicates by name
            key = name.lower().strip()
            if key in seen:
                continue
            seen.add(key)

            # also skip rows with effectively empty text
            if not text.strip():
                continue

            names.append(name)
            corpus.append(text)

        N = len(corpus)
        if N == 0:
            raise RuntimeError("All drug entries were empty after cleaning; nothing to train on.")

        # 2) Document frequencies
        df = Counter()
        tokenized_docs: list[list[str]] = []
        for doc in corpus:
            toks = tokenize(doc)
            tokenized_docs.append(toks)
            df.update(set(toks))  # DF counts unique occurrence per doc

        # 3) IDF
        idf: dict[str, float] = {}
        for term, c in df.items():
            # +1 smoothing; +1 to IDF to keep positives
            idf[term] = 1.0 + math.log((N + 1) / (c + 1))

        # 4) Build TF-IDF per doc, normalized (L2)
        docs_tfidf: list[dict] = []
        for toks, name in zip(tokenized_docs, names):
            tf = Counter(toks)
            weights: dict[str, float] = {}
            for term, f in tf.items():
                if term not in idf:
                    continue
                w = (1 + math.log(1 + f)) * idf[term]  # sublinear tf
                weights[term] = w
            # L2 normalize
            norm = math.sqrt(sum(v * v for v in weights.values())) or 1.0
            weights = {t: v / norm for t, v in weights.items()}
            docs_tfidf.append({"name": name, "weights": weights})

        # 5) Save artifacts
        with open(VOCAB_PKL, "wb") as f:
            pickle.dump(idf, f)

        with open(DOCS_PKL, "wb") as f:
            pickle.dump(docs_tfidf, f)

        with open(META_JSON, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "built_at": datetime.utcnow().isoformat() + "Z",
                    "num_docs": N,
                    "num_terms": len(idf),
                    "notes": "Lightweight TF-IDF recommender artifacts",
                    "source": "PostgreSQL: drugs table",
                    "script": str(THIS_FILE),
                },
                f,
                indent=2,
            )

        print("✅ Built TF-IDF artifacts")
        print(f"   • Documents (drugs): {N}")
        print(f"   • Vocabulary terms : {len(idf)}")
        print(f"   • Saved -> {VOCAB_PKL.name}, {DOCS_PKL.name}, {META_JSON.name} in {ARTIFACT_DIR}")

    finally:
        session.close()

if __name__ == "__main__":
    main()
