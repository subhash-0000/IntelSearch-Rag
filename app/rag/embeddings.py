from __future__ import annotations

import math
from collections import Counter


class EmbeddingService:
    """Lightweight embedding via hashed character trigrams.

    This avoids heavy binary dependencies and keeps the project portable.
    """

    def __init__(self, model_name: str, dimension: int = 384) -> None:
        self.model_name = model_name
        self.dimension = dimension

    def _trigrams(self, text: str) -> list[str]:
        cleaned = " ".join(text.lower().split())
        if len(cleaned) < 3:
            return [cleaned] if cleaned else []
        return [cleaned[i : i + 3] for i in range(len(cleaned) - 2)]

    def _vectorize(self, text: str) -> list[float]:
        vec = [0.0] * self.dimension
        counts = Counter(self._trigrams(text))

        for token, count in counts.items():
            idx = hash(token) % self.dimension
            vec[idx] += float(count)

        norm = math.sqrt(sum(v * v for v in vec))
        if norm == 0:
            return vec
        return [v / norm for v in vec]

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [self._vectorize(text) for text in texts]
