from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from .chunking import chunk_documents
from .embeddings import EmbeddingService
from .generator import HeuristicGenerator
from .ingest import load_documents
from .reranker import LightweightReranker
from .retriever import HybridRetriever
from .vector_store import VectorStore


class RAGPipeline:
    def __init__(
        self,
        data_dir: Path,
        raw_dir: Path,
        index_dir: Path,
        feedback_dir: Path,
        embedding_model: str,
        chunk_size: int,
        chunk_overlap: int,
        top_k: int,
        rerank_top_k: int,
    ) -> None:
        self.data_dir = data_dir
        self.raw_dir = raw_dir
        self.index_dir = index_dir
        self.feedback_dir = feedback_dir
        self.top_k = top_k
        self.rerank_top_k = rerank_top_k
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.embedder = EmbeddingService(embedding_model)
        self.store = VectorStore(index_dir)
        self.retriever = HybridRetriever(self.embedder, self.store)
        self.reranker = LightweightReranker()
        self.generator = HeuristicGenerator()

        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        if self.store.exists():
            self.retriever.load()

    @classmethod
    def from_config(cls, config: dict) -> "RAGPipeline":
        return cls(
            data_dir=config["DATA_DIR"],
            raw_dir=config["RAW_DATA_DIR"],
            index_dir=config["INDEX_DIR"],
            feedback_dir=config["FEEDBACK_DIR"],
            embedding_model=config["EMBEDDING_MODEL"],
            chunk_size=config["CHUNK_SIZE"],
            chunk_overlap=config["CHUNK_OVERLAP"],
            top_k=config["TOP_K"],
            rerank_top_k=config["RERANK_TOP_K"],
        )

    def rebuild_index(self) -> dict:
        docs = load_documents(self.raw_dir)
        if not docs:
            raise ValueError("No documents found in data/raw.")

        chunks = chunk_documents(docs, chunk_size=self.chunk_size, overlap=self.chunk_overlap)
        vectors = self.embedder.encode([chunk.text for chunk in chunks])
        build_stats = self.store.build(chunks=chunks, vectors=vectors)
        self.retriever.load()

        return {
            "documents": len(docs),
            "chunks": len(chunks),
            **build_stats,
        }

    def answer(self, query: str, domain: str | None = None, min_score: float = 0.0) -> dict:
        if not self.store.exists():
            self.rebuild_index()

        hits = self.retriever.retrieve(query=query, top_k=self.top_k, domain=domain)
        reranked = self.reranker.rerank(query=query, hits=hits, top_k=self.rerank_top_k)
        filtered = [item for item in reranked if item["rerank_score"] >= min_score]

        contexts = [item["chunk"].text for item in filtered]
        answer = self.generator.generate(query=query, contexts=contexts)
        request_id = str(uuid.uuid4())

        citations = [
            {
                "source": item["chunk"].source,
                "title": item["chunk"].title,
                "domain": item["chunk"].domain,
                "score": round(item["rerank_score"], 4),
                "snippet": item["chunk"].text[:220],
            }
            for item in filtered
        ]

        return {
            "request_id": request_id,
            "query": query,
            "answer": answer,
            "citations": citations,
            "used_domain": domain,
            "retrieval_count": len(filtered),
        }

    def save_feedback(self, request_id: str, rating: int, note: str = "") -> dict:
        path = self.feedback_dir / "feedback.jsonl"
        payload = {
            "request_id": request_id,
            "rating": rating,
            "note": note,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=True) + "\n")
        return payload

    def health(self) -> dict:
        return {
            "index_ready": self.store.exists(),
            "raw_docs_dir": str(self.raw_dir),
            "index_dir": str(self.index_dir),
            "top_k": self.top_k,
            "rerank_top_k": self.rerank_top_k,
        }
