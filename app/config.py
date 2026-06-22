import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Vector DB
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    COLLECTION_NAME: str = "documind_collection"

    # Chunking
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 200))

    # Retrieval
    MAX_RETRIEVAL_DOCS: int = int(os.getenv("MAX_RETRIEVAL_DOCS", 5))

    # App
    APP_NAME: str = os.getenv("APP_NAME", "DocuMind AI")
    APP_VERSION: str = "1.0.0"

    # Models
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "gemini-embedding-001"

    # API Base
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1/models"


config = Config()
