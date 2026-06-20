from __future__ import annotations

import math
from collections import Counter, defaultdict

from .chunking import Chunk
from .embeddings import EmbeddingService
from .vector_store import VectorStore


class BM25Okapi:
    def __init__(self, corpus: list[list[str]], k1: float = 1.5, b: float = 0.75) -> None:
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.doc_freq: dict[str, int] = defaultdict(int)
        self.doc_lens = [len(doc) for doc in corpus]
        self.avg_doc_len = (sum(self.doc_lens) / len(self.doc_lens)) if self.doc_lens else 1.0
        self.term_freqs: list[Counter] = []

        for doc in corpus:
            freqs = Counter(doc)
            self.term_freqs.append(freqs)
            for token in freqs:
                self.doc_freq[token] += 1

        self.corpus_size = len(corpus)

    def _idf(self, token: str) -> float:
        n = self.doc_freq.get(token, 0)
        return math.log(1 + ((self.corpus_size - n + 0.5) / (n + 0.5))) if self.corpus_size else 0.0

    def get_scores(self, query_tokens: list[str]) -> list[float]:
        scores: list[float] = []
        for i, doc in enumerate(self.corpus):
            score = 0.0
            doc_len = len(doc)
            tf = self.term_freqs[i]
            norm = self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
            for token in query_tokens:
                f = tf.get(token, 0)
                if f == 0:
                    continue
                idf = self._idf(token)
                score += idf * ((f * (self.k1 + 1)) / (f + norm))
            scores.append(score)
        return scores


class HybridRetriever:
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.bm25: BM25Okapi | None = None
        self.tokenized_corpus: list[list[str]] = []
        self.chunk_idx_by_id: dict[str, int] = {}

    def load(self) -> None:
        self.vector_store.load()
        self.tokenized_corpus = [chunk.text.lower().split() for chunk in self.vector_store.chunks]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        self.chunk_idx_by_id = {chunk.chunk_id: i for i, chunk in enumerate(self.vector_store.chunks)}

    def retrieve(self, query: str, top_k: int = 8, domain: str | None = None) -> list[dict]:
        if self.bm25 is None:
            self.load()

        query_vec = self.embedding_service.encode([query])[0]
        dense_hits = self.vector_store.search(query_vec, top_k=top_k * 3)

        tokens = query.lower().split()
        sparse_scores = self.bm25.get_scores(tokens)

        merged: list[dict] = []
        for chunk, dense_score in dense_hits:
            if domain and chunk.domain != domain:
                continue

            sparse_idx = self.chunk_idx_by_id.get(chunk.chunk_id)
            if sparse_idx is None:
                continue

            sparse_score = float(sparse_scores[sparse_idx])
            # Weighted hybrid score with min-max compressed BM25 contribution.
            hybrid_score = (0.65 * dense_score) + (0.35 * (sparse_score / (sparse_score + 1.0)))
            merged.append(
                {
                    "chunk": chunk,
                    "score": hybrid_score,
                    "dense_score": dense_score,
                    "sparse_score": sparse_score,
                }
            )

        merged.sort(key=lambda item: item["score"], reverse=True)
        return merged[:top_k]
