from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template, request

from .rag.pipeline import RAGPipeline


main_bp = Blueprint("main", __name__)


def _pipeline() -> RAGPipeline:
    if "rag_pipeline" not in current_app.config:
        current_app.config["rag_pipeline"] = RAGPipeline.from_config(current_app.config)
    return current_app.config["rag_pipeline"]


@main_bp.get("/")
def home():
    return render_template("index.html")


@main_bp.post("/api/ask")
def ask_question():
    payload = request.get_json(silent=True) or {}
    query = (payload.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Query is required."}), 400

    domain = (payload.get("domain") or "").strip() or current_app.config.get("DEFAULT_DOMAIN")
    min_score = float(payload.get("min_score", 0.0))

    result = _pipeline().answer(query=query, domain=domain, min_score=min_score)
    return jsonify(result)


@main_bp.post("/api/ingest")
def ingest():
    try:
        stats = _pipeline().rebuild_index()
        return jsonify({"status": "ok", "stats": stats})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@main_bp.post("/api/feedback")
def save_feedback():
    payload = request.get_json(silent=True) or {}
    request_id = (payload.get("request_id") or "").strip()
    rating = int(payload.get("rating", 0))
    note = (payload.get("note") or "").strip()

    if not request_id or rating not in {1, 2, 3, 4, 5}:
        return jsonify({"error": "request_id and rating (1-5) are required."}), 400

    saved = _pipeline().save_feedback(request_id=request_id, rating=rating, note=note)
    return jsonify({"status": "ok", "saved": saved})


@main_bp.get("/api/health")
def health():
    info = _pipeline().health()
    return jsonify(info)
