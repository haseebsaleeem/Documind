from typing import List
import requests
from app.config import config


class EmbeddingGenerator:
    """
    Generates embeddings using Google Gemini REST API directly.
    No SDK — pure HTTP requests.
    """

    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.model = config.EMBEDDING_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1/models"

    def _call_api(self, text: str, task_type: str) -> List[float]:
        url = f"{self.base_url}/{self.model}:embedContent?key={self.api_key}"
        payload = {
            "model": f"models/{self.model}",
            "content": {
                "parts": [{"text": text}]
            },
            "taskType": task_type
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["embedding"]["values"]
        except Exception as e:
            print(f"[EmbeddingGenerator] API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[EmbeddingGenerator] Response: {e.response.text}")
            return []

    def embed_text(self, text: str) -> List[float]:
        return self._call_api(text, "RETRIEVAL_DOCUMENT")

    def embed_query(self, query: str) -> List[float]:
        return self._call_api(query, "RETRIEVAL_QUERY")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]
