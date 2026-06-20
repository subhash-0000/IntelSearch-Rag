from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path

from .chunking import Chunk


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=False))


def _norm(vec: list[float]) -> float:
    return math.sqrt(sum(x * x for x in vec))


class VectorStore:
    def __init__(self, index_dir: Path) -> None:
        self.index_dir = index_dir
        self.index_path = index_dir / "vectors.json"
        self.meta_path = index_dir / "chunks.json"
        self.vectors: list[list[float]] = []
        self.chunks: list[Chunk] = []

    def exists(self) -> bool:
        return self.index_path.exists() and self.meta_path.exists()

    def build(self, chunks: list[Chunk], vectors: list[list[float]]) -> dict:
        if not chunks:
            raise ValueError("No chunks provided for index build.")

        self.index_dir.mkdir(parents=True, exist_ok=True)
        dim = len(vectors[0]) if vectors else 0
        self.index_path.write_text(json.dumps(vectors, ensure_ascii=True), encoding="utf-8")
        self.meta_path.write_text(
            json.dumps([asdict(chunk) for chunk in chunks], indent=2, ensure_ascii=True),
            encoding="utf-8",
        )

        self.vectors = vectors
        self.chunks = chunks
        return {"chunks": len(chunks), "dimension": dim}

    def load(self) -> None:
        if not self.exists():
            raise FileNotFoundError("Vector index has not been built yet.")

        self.vectors = json.loads(self.index_path.read_text(encoding="utf-8"))
        raw = json.loads(self.meta_path.read_text(encoding="utf-8"))
        self.chunks = [Chunk(**item) for item in raw]

    def search(self, query_vector: list[float], top_k: int) -> list[tuple[Chunk, float]]:
        if not self.vectors or not self.chunks:
            self.load()

        q_norm = _norm(query_vector) or 1.0
        scored: list[tuple[int, float]] = []
        for idx, vec in enumerate(self.vectors):
            denom = q_norm * (_norm(vec) or 1.0)
            score = _dot(query_vector, vec) / denom
            scored.append((idx, float(score)))

        scored.sort(key=lambda item: item[1], reverse=True)
        scored = scored[:top_k]

        results: list[tuple[Chunk, float]] = []
        for idx, score in scored:
            results.append((self.chunks[idx], score))
        return results
