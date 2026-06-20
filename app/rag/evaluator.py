from __future__ import annotations

from dataclasses import dataclass

from .retriever import HybridRetriever


@dataclass
class EvalCase:
    query: str
    expected_source_contains: str


def evaluate_retrieval(retriever: HybridRetriever, cases: list[EvalCase], top_k: int = 5) -> dict:
    if not cases:
        return {"cases": 0, "recall_at_k": 0.0, "mrr": 0.0}

    hits = 0
    reciprocal_rank_sum = 0.0

    for case in cases:
        results = retriever.retrieve(case.query, top_k=top_k)
        found_rank = None
        for rank, item in enumerate(results, start=1):
            source = item["chunk"].source.lower()
            if case.expected_source_contains.lower() in source:
                found_rank = rank
                break

        if found_rank:
            hits += 1
            reciprocal_rank_sum += 1.0 / found_rank

    total = len(cases)
    return {
        "cases": total,
        "recall_at_k": round(hits / total, 4),
        "mrr": round(reciprocal_rank_sum / total, 4),
    }
