from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

    DATA_DIR = ROOT_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    INDEX_DIR = DATA_DIR / "index"
    FEEDBACK_DIR = ROOT_DIR / "feedback"

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    TOP_K = int(os.getenv("RAG_TOP_K", "8"))
    RERANK_TOP_K = int(os.getenv("RAG_RERANK_TOP_K", "4"))
    CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "700"))
    CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "120"))

    ENABLE_HF_GENERATOR = os.getenv("RAG_ENABLE_HF_GENERATOR", "false").lower() == "true"
    HF_MODEL = os.getenv("RAG_HF_MODEL", "google/flan-t5-base")
    DEFAULT_DOMAIN = os.getenv("RAG_DEFAULT_DOMAIN", "").strip() or None
