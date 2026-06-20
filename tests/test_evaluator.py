from app.rag.evaluator import EvalCase, evaluate_retrieval


class FakeRetriever:
    def retrieve(self, query: str, top_k: int = 5):
        if "incident" in query.lower():
            return [{"chunk": type("Chunk", (), {"source": "engineering/incident_response.md"})()}]
        return [{"chunk": type("Chunk", (), {"source": "other/doc.md"})()}]


def test_evaluate_retrieval_metrics():
    cases = [
        EvalCase(query="incident process", expected_source_contains="incident_response"),
        EvalCase(query="leave details", expected_source_contains="leave_policy"),
    ]

    metrics = evaluate_retrieval(FakeRetriever(), cases, top_k=5)
    assert metrics["cases"] == 2
    assert metrics["recall_at_k"] == 0.5
