import os
import re
import hashlib
from typing import List, Dict, Any, Optional

import pdfplumber
import PyPDF2
import chromadb

from app.config import config
from app.rag.chunker import DocumentChunker
from app.rag.embeddings import EmbeddingGenerator


class DocumentPipeline:
    """
    End-to-end document ingestion pipeline:
    PDF -> Extract -> Clean -> Chunk -> Embed -> Store in ChromaDB
    """

    def __init__(self, collection=None):
        self.chunker = DocumentChunker()
        self.embedder = EmbeddingGenerator()

        if collection is not None:
            self.collection = collection
        else:
            self.client = chromadb.PersistentClient(
                path=config.CHROMA_PERSIST_DIR)
            self.collection = self.client.get_or_create_collection(
                name=config.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )

    def ingest_pdf(self, file_path: str, source_name: Optional[str] = None) -> Dict[str, Any]:
        """Full pipeline: PDF file -> ChromaDB. Returns ingestion report."""
        source_name = source_name or os.path.basename(file_path)

        raw_text, page_count = self._extract_pdf(file_path)
        if not raw_text.strip():
            return {"success": False, "error": "Could not extract text from PDF."}

        cleaned = self._clean_text(raw_text)

        metadata = {
            "source": source_name,
            "file_path": file_path,
            "page_count": page_count,
            "doc_id": self._file_hash(file_path)
        }
        chunks = self.chunker.chunk_text(cleaned, metadata)
        stored = self._store_chunks(chunks)

        return {
            "success": True,
            "source": source_name,
            "pages": page_count,
            "chunks_created": len(chunks),
            "chunks_stored": stored,
            "preview": cleaned[:300] + "..."
        }

    def ingest_text(self, text: str, source_name: str) -> Dict[str, Any]:
        """Ingest raw text directly."""
        cleaned = self._clean_text(text)
        metadata = {
            "source": source_name,
            "doc_id": hashlib.md5(text.encode()).hexdigest()
        }
        chunks = self.chunker.chunk_text(cleaned, metadata)
        stored = self._store_chunks(chunks)
        return {
            "success": True,
            "source": source_name,
            "chunks_created": len(chunks),
            "chunks_stored": stored
        }

    def get_collection_stats(self) -> Dict[str, Any]:
        """Return stats about what's stored in the vector DB."""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": config.COLLECTION_NAME,
            "persist_dir": config.CHROMA_PERSIST_DIR
        }

    def list_documents(self) -> List[str]:
        """Return list of unique source documents in the DB."""
        if self.collection.count() == 0:
            return []
        results = self.collection.get(include=["metadatas"])
        sources = list({m["source"]
                       for m in results["metadatas"] if "source" in m})
        return sorted(sources)

    def delete_document(self, source_name: str) -> int:
        """Delete all chunks belonging to a document."""
        results = self.collection.get(
            where={"source": source_name},
            include=["metadatas"]
        )
        ids = results.get("ids", [])
        if ids:
            self.collection.delete(ids=ids)
        return len(ids)

    def _extract_pdf(self, file_path: str):
        """Try pdfplumber first, fall back to PyPDF2."""
        text = ""
        page_count = 0

        try:
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception:
            pass

        if not text.strip():
            try:
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    page_count = len(reader.pages)
                    for page in reader.pages:
                        text += page.extract_text() or ""
            except Exception as e:
                print(f"[Pipeline] PDF extraction error: {e}")

        return text, page_count

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'[^\x20-\x7E\n]', ' ', text)
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        return text.strip()

    def _store_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Embed chunks and store in ChromaDB."""
        stored = 0
        for chunk in chunks:
            text = chunk["text"]
            meta = chunk["metadata"]

            uid = hashlib.md5(
                f"{meta.get('source', '')}-{meta.get('chunk_index', 0)}-{text[:50]}".encode(
                )
            ).hexdigest()

            embedding = self.embedder.embed_text(text)
            if not embedding:
                print(f"[Pipeline] Skipping chunk — empty embedding")
                continue

            clean_meta = {k: str(v) for k, v in meta.items()}

            try:
                self.collection.upsert(
                    ids=[uid],
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[clean_meta]
                )
                stored += 1
            except Exception as e:
                print(f"[Pipeline] Store error: {e}")

        return stored

    def _file_hash(self, path: str) -> str:
        h = hashlib.md5()
        with open(path, "rb") as f:
            h.update(f.read())
        return h.hexdigest()
