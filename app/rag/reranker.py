from __future__ import annotations

import math


def _cosine_like_overlap(q_tokens: set[str], doc_tokens: set[str]) -> float:
    if not q_tokens or not doc_tokens:
        return 0.0
    overlap = len(q_tokens.intersection(doc_tokens))
    denom = math.sqrt(len(q_tokens) * len(doc_tokens))
    return overlap / denom if denom else 0.0


class LightweightReranker:
    """Fast lexical-semantic reranker without external heavy model dependencies."""

    def rerank(self, query: str, hits: list[dict], top_k: int) -> list[dict]:
        q_tokens = set(query.lower().split())

        for hit in hits:
            d_tokens = set(hit["chunk"].text.lower().split())
            overlap = _cosine_like_overlap(q_tokens, d_tokens)
            hit["rerank_score"] = (0.75 * hit["score"]) + (0.25 * overlap)

        hits.sort(key=lambda item: item["rerank_score"], reverse=True)
        return hits[:top_k]
