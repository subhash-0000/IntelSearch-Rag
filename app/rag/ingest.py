from __future__ import annotations

from pathlib import Path


def _infer_domain(path: Path) -> str:
    parts = [p.lower() for p in path.parts]
    for candidate in ("hr", "engineering", "security", "policy", "product"):
        if candidate in parts:
            return candidate
    return "general"


def load_documents(raw_dir: Path) -> list[dict]:
    if not raw_dir.exists():
        return []

    documents: list[dict] = []
    for file_path in sorted(raw_dir.rglob("*")):
        if file_path.suffix.lower() not in {".txt", ".md"}:
            continue

        text = file_path.read_text(encoding="utf-8")
        if not text.strip():
            continue

        rel = file_path.relative_to(raw_dir)
        doc_id = str(rel.with_suffix("")).replace("\\", "/")
        title = file_path.stem.replace("_", " ").replace("-", " ").title()
        documents.append(
            {
                "id": doc_id,
                "source": str(rel).replace("\\", "/"),
                "title": title,
                "domain": _infer_domain(rel),
                "text": text,
            }
        )
    return documents
