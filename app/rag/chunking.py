from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(slots=True)
class Chunk:
    chunk_id: str
    text: str
    source: str
    title: str
    domain: str


def split_text(text: str, chunk_size: int = 700, overlap: int = 120) -> list[str]:
    cleaned = " ".join(text.split())
    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunks.append(cleaned[start:end])
        if end >= len(cleaned):
            break
        start = max(0, end - overlap)
    return chunks


def chunk_documents(documents: Iterable[dict], chunk_size: int, overlap: int) -> list[Chunk]:
    output: list[Chunk] = []

    for doc in documents:
        text_chunks = split_text(doc["text"], chunk_size=chunk_size, overlap=overlap)
        for idx, text in enumerate(text_chunks):
            output.append(
                Chunk(
                    chunk_id=f"{doc['id']}::chunk-{idx}",
                    text=text,
                    source=doc["source"],
                    title=doc.get("title", doc["id"]),
                    domain=doc.get("domain", "general"),
                )
            )
    return output
