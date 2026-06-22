from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import config


class DocumentChunker:
    """
    Handles intelligent chunking of documents with multiple strategies.
    """

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata attached to each chunk."""
        raw_chunks = self.splitter.split_text(text)
        chunks = []
        for i, chunk in enumerate(raw_chunks):
            chunk_meta = {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(raw_chunks),
                "chunk_size": len(chunk)
            }
            chunks.append({
                "text": chunk,
                "metadata": chunk_meta
            })
        return chunks

    def chunk_by_paragraph(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Alternative: split by paragraphs for structured documents."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        for i, para in enumerate(paragraphs):
            if len(para) > 50:  # skip tiny fragments
                chunks.append({
                    "text": para,
                    "metadata": {**metadata, "chunk_index": i, "total_chunks": len(paragraphs)}
                })
        return chunks
