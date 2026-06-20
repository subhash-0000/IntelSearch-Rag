from app.rag.chunking import chunk_documents, split_text


def test_split_text_generates_overlap_chunks():
    text = "A" * 200
    chunks = split_text(text, chunk_size=80, overlap=20)
    assert len(chunks) >= 3
    assert all(len(c) <= 80 for c in chunks)


def test_chunk_documents_metadata_propagation():
    docs = [
        {
            "id": "policy/remote",
            "source": "policy/remote.md",
            "title": "Remote",
            "domain": "policy",
            "text": "word " * 300,
        }
    ]

    chunks = chunk_documents(docs, chunk_size=120, overlap=30)
    assert len(chunks) > 1
    assert chunks[0].source == "policy/remote.md"
    assert chunks[0].domain == "policy"
