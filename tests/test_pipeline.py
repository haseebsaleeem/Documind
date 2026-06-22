import pytest
from app.rag.chunker import DocumentChunker
from app.rag.pipeline import DocumentPipeline


def test_chunker_basic():
    chunker = DocumentChunker()
    text = "This is sentence one. " * 100
    chunks = chunker.chunk_text(text, {"source": "test.pdf"})
    assert len(chunks) > 0
    assert all("text" in c for c in chunks)
    assert all("metadata" in c for c in chunks)


def test_chunker_metadata():
    chunker = DocumentChunker()
    chunks = chunker.chunk_text(
        "Some text " * 50, {"source": "doc.pdf", "page_count": 3})
    for chunk in chunks:
        assert chunk["metadata"]["source"] == "doc.pdf"
        assert "chunk_index" in chunk["metadata"]


def test_chunker_paragraph():
    chunker = DocumentChunker()
    text = "This is the first paragraph with enough content to pass the filter.\n\nThis is the second paragraph with enough content to pass the filter.\n\nThis is the third paragraph with enough content to pass the filter."
    chunks = chunker.chunk_by_paragraph(text, {"source": "test.pdf"})
    assert len(chunks) > 0


def test_pipeline_stats():
    pipeline = DocumentPipeline()
    stats = pipeline.get_collection_stats()
    assert "total_chunks" in stats
    assert isinstance(stats["total_chunks"], int)


def test_pipeline_list_documents():
    pipeline = DocumentPipeline()
    docs = pipeline.list_documents()
    assert isinstance(docs, list)
