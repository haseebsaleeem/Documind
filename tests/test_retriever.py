from app.rag.retriever import RAGRetriever


def test_retriever_init():
    """Should initialize without errors."""
    retriever = RAGRetriever()
    assert retriever is not None


def test_retriever_empty_collection():
    """Should return empty list when no documents loaded."""
    retriever = RAGRetriever()
    if retriever.collection.count() == 0:
        results = retriever.retrieve("test query")
        assert isinstance(results, list)
        assert len(results) == 0


def test_retriever_answer_no_docs():
    """Should return graceful message when no documents loaded."""
    retriever = RAGRetriever()
    if retriever.collection.count() == 0:
        result = retriever.answer("What is this document about?")
        assert "answer" in result
        assert "sources" in result
        assert isinstance(result["sources"], list)
        assert "confidence" in result
