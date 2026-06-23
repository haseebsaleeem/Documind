import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str, default: str = "") -> str:
    """
    Reads from Streamlit secrets first (cloud),
    then falls back to environment variables (local).
    """
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


class Config:
    # API
    GEMINI_API_KEY: str = get_secret("GEMINI_API_KEY")

    # Vector DB
    CHROMA_PERSIST_DIR: str = get_secret("CHROMA_PERSIST_DIR", "./chroma_db")
    COLLECTION_NAME: str = "documind_collection"

    # Chunking
    CHUNK_SIZE: int = int(get_secret("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(get_secret("CHUNK_OVERLAP", "200"))

    # Retrieval
    MAX_RETRIEVAL_DOCS: int = int(get_secret("MAX_RETRIEVAL_DOCS", "5"))

    # App
    APP_NAME: str = get_secret("APP_NAME", "DocuMind AI")
    APP_VERSION: str = "1.0.0"

    # Models
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "gemini-embedding-001"

    # API Base
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1/models"


config = Config()
