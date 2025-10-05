# WeMakeDev RAG System 📚🤖

A comprehensive **Retrieval-Augmented Generation (RAG)** system built with FastAPI and Pinecone for intelligent document querying and quiz generation from PDF books.

## 🌟 Features

- **Document Processing**: Automatically process PDF books and create embeddings
- **Intelligent Querying**: Ask questions about your documents and get AI-powered answers
- **Quiz Generation**: Generate quizzes based on document content
- **Multi-Book Support**: Query specific books or search across all documents
- **RESTful API**: Clean FastAPI endpoints for easy integration
- **Vector Search**: Powered by Pinecone for fast and accurate document retrieval
- **AI Integration**: Uses Cerebras Cloud SDK for intelligent responses

## 📁 Project Structure

```
rag/
├── app.py                    # Main FastAPI application
├── document_pinecone.py      # Document processing and embedding
├── query_pinecone.py         # Query processing and AI responses
├── config.py                 # Configuration settings
├── requirements_rag.txt      # Python dependencies
├── .env.example             # Environment variables template
├── .env                     # Your environment variables
├── books/                   # PDF books directory
│   ├── tamilNadu-computerScience.pdf
│   └── tamilNadu-english.pdf
├── DockerFile              # Docker configuration
├── .gitignore              # Git ignore rules
└── README.md               # This documentation
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- **Pinecone Account** (for vector database)
- **Cerebras API Key** (for AI responses)
- **Hugging Face Account** (for embeddings)

### 2. Installation

Clone this repository and navigate to the project directory:

```bash
git clone <repository-url>
cd rag
```

### 3. Set up Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements_rag.txt
```

### 5. Environment Setup

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual API keys:

```bash
# Environment Configuration for RAG System
# REQUIRED: Get these from respective services

# Pinecone Configuration (https://pinecone.io)
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_INDEX_NAME=document-collection
PINECONE_DIMENSION=384
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Hugging Face Configuration (https://huggingface.co)
HF_TOKEN=your-hugging-face-token-here
HF_CACHE_DIR=./hf_cache

# Cerebras API Key (https://cerebras.ai)
CEREBRAS_API_KEY=your-cerebras-api-key-here

# Application Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
PORT=7860
```

### 6. Add Your PDF Books

Place your PDF files in the `books/` directory:

```
books/
├── tamilNadu-computerScience.pdf
├── tamilNadu-english.pdf
└── your-book.pdf  # Add more PDFs here
```

### 7. Process Documents

Run the document processing script to create embeddings:

```bash
python document_pinecone.py
```

### 8. Start the API Server

```bash
python app.py
```

The API will be available at `http://localhost:7860`

## 🔌 API Endpoints

### Core Endpoints

- **GET** `/` - API welcome message and version
- **GET** `/health` - Health check endpoint
- **GET** `/books` - List all available books in the system
- **POST** `/query` - Query documents and get AI responses
- **POST** `/quizz` - Generate quizzes from document content

### 📖 API Usage Examples

#### 1. Health Check
```bash
curl http://localhost:7860/health
```

#### 2. Get Available Books
```bash
curl http://localhost:7860/books
```

#### 3. Query Documents
```bash
curl -X POST http://localhost:7860/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is computer science?",
    "book": "tamilNadu-computerScience.pdf",
    "n_results": 3
  }'
```

#### 4. Generate Quiz
```bash
curl -X POST http://localhost:7860/quizz \
  -H "Content-Type: application/json" \
  -d '{
    "book": "tamilNadu-english.pdf",
    "n_results": 5,
    "question": 10
  }'
```

#### 5. Query with Chat History
```bash
curl -X POST http://localhost:7860/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain more about that topic",
    "message": [
      {"role": "user", "content": "What is programming?"},
      {"role": "assistant", "content": "Programming is..."}
    ],
    "n_results": 3
  }'
```

## ⚙️ Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PINECONE_API_KEY` | Your Pinecone API key | `pc-abc123...` |
| `PINECONE_INDEX_NAME` | Name of your Pinecone index | `document-collection` |
| `CEREBRAS_API_KEY` | Your Cerebras API key for LLM | `csk-abc123...` |
| `HF_TOKEN` | Hugging Face API token | `hf_abc123...` |

### Optional Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `7860` |
| `PINECONE_DIMENSION` | Vector dimension | `384` |

# WeMakeDev — RAG + Voice Agent (current status)

This repository contains a Retrieval-Augmented Generation (RAG) system plus an experimental voice/agent integration. The project combines document processing, vector search (Pinecone), embeddings (SentenceTransformers / Hugging Face), and LLM-driven responses via Cerebras Cloud. A FastAPI service exposes query and quiz endpoints. There's also a LiveKit-based voice agent implementation that uses Deepgram for STT/TTS and OpenAI/Cerebras models for conversational responses.

This README has been updated to reflect the actual code and tooling in the repository as of now.

## What this project currently includes

- FastAPI application exposing endpoints in `app.py` (/, /health, /books, /query, /quizz)
- Document processing and embedding upload: `document_pinecone.py` (downloads PDFs from a HF repo fallback and uploads embeddings to Pinecone)
- Query & quiz logic: `query_pinecone.py` (queries Pinecone and calls Cerebras chat completions)
- Voice/agent code: `agent.py` (LiveKit agent + tools, Deepgram STT/TTS, utility functions)
- Configuration: `config.py` (loads environment variables)
- Example books folder: `books/` (small set of sample PDFs or placeholders)
- Dockerfile for container builds

## Main libraries & services used

- FastAPI (API server)
- Uvicorn (ASGI server)
- Pinecone (vector database)
- sentence-transformers (embeddings, e.g. all-MiniLM-L6-v2)
- langchain_community (PDF loader used in processing script)
- huggingface_hub (optional download of PDFs)
- Cerebras Cloud SDK (LLM/chat completions)
- LiveKit, Deepgram, and related plugins (voice agent)
- python-dotenv (load .env values)

Check `requirements_rag.txt` for the full pinned dependencies list.

## Quick run (local development)

1) Create and activate a virtual environment (PowerShell on Windows):

```powershell
python -m venv .venv; .venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install -r requirements_rag.txt
```

3) Create a `.env` file (you can copy values from `.env.example` if present) and set at least:

- PINECONE_API_KEY — Pinecone API key
- PINECONE_INDEX_NAME — name for index (default: document-collection)
- HF_TOKEN — (optional) Hugging Face token if downloading PDFs from a repo
- CEREBRAS_API_KEY — API key for Cerebras chat completions
- PORT — port to run the FastAPI app (default 7860)

Example minimal `.env`:

```text
PINECONE_API_KEY=pc-xxxx
PINECONE_INDEX_NAME=document-collection
CEREBRAS_API_KEY=csk-xxxx
HF_TOKEN=hf_xxx
PORT=7860
```

4) Prepare or add PDFs:

- Put PDFs into `books/` or ensure `document_pinecone.py` can download them from the configured Hugging Face repo.

5) Build index (creates embeddings and uploads to Pinecone):

```powershell
python document_pinecone.py
```

6) Start the API server:

```powershell
python app.py
```

API base: http://localhost:7860

Endpoints:

- GET / — welcome
- GET /health — status
- GET /books — list available indexed books
- POST /query — body: {"query": "...", "book": "optional.pdf", "n_results": 3, "message": [...]} — returns an LLM answer plus sources
- POST /quizz — body: {"book": "optional.pdf", "n_results": 3, "question": 10} — returns generated quiz JSON

## Voice agent (notes)

- `agent.py` contains an experimental LiveKit-based voice agent that:
   - uses `sentence-transformers` to embed user queries and Pinecone to search the knowledge base
   - provides helper function tools (get_weather, get_time)
   - configures a session with Deepgram STT/TTS and a Cerebras/OpenAI LLM
- This component is not required to run the REST API but demonstrates how to wire a conversation-capable agent to the same knowledge base.

## Known limitations & TODOs

- Some components assume external services (Pinecone, Cerebras, Deepgram). Without valid API keys they will not function.
- `document_pinecone.py` may attempt to download PDFs from a Hugging Face repo — ensure `HF_TOKEN` is set if the repo is private.
- Error handling is basic in places (scripts often print and exit); consider adding better retries and logging.

If you want, I can:

- run a small verification (read environment and list available books) locally in this workspace
- add a `.env.example` file with recommended variables
- add a small smoke test script that calls `/health` and `/books`

---

Requirements coverage:

- README updated to describe current project files and status — Done
- Listed main libraries and external services used — Done
- Quick local run steps and endpoints — Done

If you'd like a more detailed README (examples for request/response JSON, contribution guide, or Docker instructions), tell me which sections to expand and I'll update the file.