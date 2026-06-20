# OpsIntel RAG Console

A portfolio-grade Retrieval-Augmented Generation (RAG) project built with Python + Flask.

This app solves a practical problem: helping teams query scattered internal policy and operations docs with grounded answers, ranked evidence, and feedback logging.

## Why this is showcase-worthy

- Hybrid retrieval pipeline: dense vector search (FAISS) + sparse BM25 scoring.
- Reranking stage for better evidence precision.
- Grounded responses with source citations and confidence-like scores.
- Domain filtering (engineering, security, HR, policy).
- Re-index endpoint for document refresh.
- Feedback capture endpoint for continuous quality loops.
- Retrieval evaluation script with Recall@K and MRR.
- Modern non-boilerplate UI designed for demos.

## Architecture

1. Ingestion:
   - Reads `.md` and `.txt` files from `data/raw`.
   - Infers metadata such as title, source, and domain.
   - Splits documents into overlapping chunks.

2. Indexing:
   - Creates embeddings using `all-MiniLM-L6-v2`.
   - Stores vectors in FAISS (`data/index/faiss.index`).
   - Stores chunk metadata in JSON (`data/index/chunks.json`).

3. Retrieval:
   - Dense retrieval from FAISS.
   - Sparse retrieval via BM25.
   - Weighted score fusion.

4. Rerank + Answer:
   - Lightweight reranker boosts lexical overlap confidence.
   - Generator composes deterministic grounded answer.
   - Returns citations, domains, snippets, and request ID.

5. Learning loop:
   - User ratings logged to `feedback/feedback.jsonl`.

## Project structure

- `app/` Flask app, routes, and RAG modules
- `data/raw/` sample source docs
- `data/index/` generated vector index
- `scripts/build_index.py` manual reindex command
- `scripts/evaluate.py` retrieval metrics command
- `tests/` baseline tests

## Quickstart

1. Create virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure environment:

```powershell
Copy-Item .env.example .env
```

3. Build index:

```powershell
python scripts/build_index.py
```

4. Run app:

```powershell
python run.py
```

5. Open:

- http://127.0.0.1:5000

## API endpoints

- `POST /api/ask`
  - body: `{"query": "...", "domain": "engineering", "min_score": 0.0}`
- `POST /api/ingest`
- `POST /api/feedback`
  - body: `{"request_id":"...", "rating": 5, "note":"helpful"}`
- `GET /api/health`

## Demo ideas for interviews

- Ask an incident escalation question and show grounded citations.
- Toggle domain filters and compare retrieval behavior.
- Edit a raw policy file, hit re-index, and show updated answers.
- Show feedback data accumulation and discuss active-learning roadmap.

## Suggested roadmap improvements

- Add cross-encoder reranker (e.g., `bge-reranker-base`).
- Add optional LLM generation provider (OpenAI/Ollama) with switchable adapters.
- Add ingestion for PDFs and Confluence exports.
- Add authentication and multi-tenant doc spaces.
- Add tracing dashboard (latency, hit-rate, citation coverage).
