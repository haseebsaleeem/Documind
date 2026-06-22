 # DocuMind AI

AI-Powered Document Intelligence and Decision Assistant built with Google Gemini, ChromaDB, and Streamlit.

## Features

- PDF ingestion with intelligent chunking
- RAG-based semantic search with source citations
- AI Agent for multi-step reasoning
- Automated CSV analytics with visualizations
- Built-in evaluation suite with LLM-as-judge scoring
- Docker deployment ready

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Google Gemini 2.5 Flash |
| Embeddings | gemini-embedding-001 (3072 dim) |
| Vector DB | ChromaDB |
| UI | Streamlit |
| PDF Parsing | pdfplumber + PyPDF2 |
| Analytics | Pandas + Plotly |

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/documind.git
cd documind
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
```

Gemini API key:

### 3. Run

```bash
python -m streamlit run app/main.py
```

Open http://localhost:8501

### 4. Docker

```bash
docker-compose up --build
```

## Project Structure
documind/

├── app/

│   ├── main.py              # Streamlit entry point

│   ├── config.py            # Configuration

│   ├── agent.py             # AI Agent

│   ├── styles.py            # UI styles

│   ├── rag/

│   │   ├── pipeline.py      # Document ingestion

│   │   ├── embeddings.py    # Embedding generation

│   │   ├── retriever.py     # Semantic search + RAG

│   │   └── chunker.py       # Text chunking

│   ├── analytics/

│   │   └── data_analyzer.py # CSV analytics

│   ├── evaluation/

│   │   └── evaluator.py     # RAG evaluation

│   └── ui/

│       ├── chat_ui.py       # Chat interface

│       ├── analytics_ui.py  # Analytics interface

│       └── sidebar.py       # Sidebar

├── tests/                   # Unit tests

├── docs/                    # Architecture docs

├── sample_docs/             # Sample PDFs

├── requirements.txt

├── Dockerfile

└── docker-compose.yml

## Architecture

### Document Ingestion Flow

PDF Upload → Text Extraction → Cleaning → Chunking → Embedding → ChromaDB

### Query Flow

User Query → Query Embedding → Similarity Search → Context Assembly → Gemini → Cited Answer

### Agent Flow

Query → Intent Planning → Action Routing → Execution → Synthesis


## Evaluation Metrics

- Retrieval similarity score (cosine)
- LLM-as-judge quality scoring (1-5 scale)
- Response latency measurement
- Confidence classification (high/medium/low)

## Running Tests

```bash
python -m pytest tests/ -v
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| GEMINI_API_KEY | Google Gemini API key | required |
| CHROMA_PERSIST_DIR | ChromaDB storage path | ./chroma_db |
| CHUNK_SIZE | Text chunk size | 1000 |
| CHUNK_OVERLAP | Chunk overlap | 200 |
| MAX_RETRIEVAL_DOCS | Top-k retrieval | 5 |

## Limitations

- Free tier API rate limits apply
- PDF only ingestion
- Single user design

## Future Improvements

- User authentication
- Persistent chat history
- DOCX and HTML support
- Hybrid BM25 + semantic search
- Cloud deployment


