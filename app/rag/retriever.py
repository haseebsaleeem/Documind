from typing import List, Dict, Any
import requests
import chromadb

from app.config import config
from app.rag.embeddings import EmbeddingGenerator


class RAGRetriever:
    def __init__(self, collection=None):
        self.api_key = config.GEMINI_API_KEY
        self.embedder = EmbeddingGenerator()
        self.base_url = "https://generativelanguage.googleapis.com/v1/models"

        if collection is not None:
            self.collection = collection
        else:
            chroma = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
            self.collection = chroma.get_or_create_collection(
                name=config.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )

    def _generate(self, prompt: str) -> str:
        url = f"{self.base_url}/{config.GEMINI_MODEL}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
        }
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[RAGRetriever] LLM error: {e}")
            return f"Error generating response: {str(e)}"

    def retrieve(self, query: str, n_results: int = None) -> List[Dict[str, Any]]:
        n_results = n_results or config.MAX_RETRIEVAL_DOCS

        if self.collection.count() == 0:
            return []

        query_embedding = self.embedder.embed_query(query)
        if not query_embedding:
            return []

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []
        for i in range(len(results["documents"][0])):
            distance = results["distances"][0][i]
            similarity = 1 - distance
            retrieved.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "similarity": round(similarity, 4),
                "source": results["metadatas"][0][i].get("source", "Unknown")
            })

        return retrieved

    def answer(self, query: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        contexts = self.retrieve(query)

        if not contexts:
            return {
                "answer": "I don't have any documents to search through yet. Please upload some documents first.",
                "sources": [],
                "confidence": "low",
                "contexts_used": 0
            }

        context_text = ""
        sources_used = []
        for i, ctx in enumerate(contexts):
            context_text += f"\n[Source {i+1}: {ctx['source']}]\n{ctx['text']}\n"
            if ctx["source"] not in sources_used:
                sources_used.append(ctx["source"])

        history_text = ""
        if chat_history:
            for msg in chat_history[-4:]:
                history_text += f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}\n"

        prompt = f"""You are DocuMind AI, an expert document intelligence assistant.
Answer questions accurately based ONLY on the provided document context.

## Conversation History:
{history_text if history_text else "No prior conversation."}

## Retrieved Document Context:
{context_text}

## User Question:
{query}

## Instructions:
- Answer based strictly on the context above.
- Be specific and cite which source your answer comes from.
- If the context doesn't contain enough information, say so clearly.
- End your response with a "📌 Sources:" section listing the documents referenced.

## Answer:"""

        answer_text = self._generate(prompt)

        avg_sim = sum(c["similarity"] for c in contexts) / len(contexts)
        confidence = "high" if avg_sim > 0.7 else "medium" if avg_sim > 0.4 else "low"

        return {
            "answer": answer_text,
            "sources": sources_used,
            "contexts": contexts,
            "confidence": confidence,
            "avg_similarity": round(avg_sim, 4),
            "contexts_used": len(contexts)
        }
