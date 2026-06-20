from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.rag.evaluator import EvalCase, evaluate_retrieval
from app.rag.pipeline import RAGPipeline


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        pipeline = RAGPipeline.from_config(app.config)

        if not pipeline.store.exists():
            pipeline.rebuild_index()

        cases = [
            EvalCase(
                query="Who gets paged first for severe incidents?",
                expected_source_contains="engineering/incident_response",
            ),
            EvalCase(
                query="What is the offboarding timeline for account disablement?",
                expected_source_contains="security/access_control",
            ),
            EvalCase(
                query="How long can employees work from another country?",
                expected_source_contains="policy/remote_work",
            ),
        ]

        metrics = evaluate_retrieval(pipeline.retriever, cases, top_k=5)
        print(f"Retrieval evaluation: {metrics}")
