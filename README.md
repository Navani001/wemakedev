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
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `HF_CACHE_DIR` | Hugging Face cache directory | `./hf_cache` |

## 🏗️ System Architecture

### Core Components

1. **FastAPI Application** (`app.py`)
   - RESTful API server
   - Async request handling
   - Health monitoring

2. **Document Processing** (`document_pinecone.py`)
   - PDF text extraction
   - Text chunking and preprocessing
   - Vector embedding generation
   - Pinecone index management

3. **Query Engine** (`query_pinecone.py`)
   - Vector similarity search
   - Context retrieval
   - AI-powered response generation
   - Quiz generation logic

4. **Books Directory** (`books/`)
   - Contains all PDF documents
   - Automatically scanned for new files
   - Currently includes:
     - `tamilNadu-computerScience.pdf`
     - `tamilNadu-english.pdf`

### Data Flow

```
PDF Books → Document Processing → Vector Embeddings → Pinecone Database
                                                            ↓
User Query → Vector Search → Context Retrieval → AI Response → JSON Output
```

## 🐳 Docker Deployment

The application includes a `DockerFile` for containerized deployment:

```bash
# Build the Docker image
docker build -t wemakedev-rag .

# Run the container
docker run -p 7860:7860 --env-file .env wemakedev-rag
```

## 🔧 Development

### Adding New Books

1. Place PDF files in the `books/` directory
2. Run the document processing script:
   ```bash
   python document_pinecone.py
   ```
3. The system will automatically process and index new documents

### Project Structure Details

```
📁 rag/
├── 🚀 app.py                    # FastAPI application server
├── 📄 document_pinecone.py      # PDF processing & vectorization
├── 🔍 query_pinecone.py         # Search & AI response logic
├── ⚙️  config.py                # Configuration management
├── 📋 requirements_rag.txt      # Python dependencies
├── 🔐 .env.example             # Environment template
├── 🔐 .env                     # Your secrets (not in git)
├── 📚 books/                   # PDF documents storage
│   ├── 📖 tamilNadu-computerScience.pdf
│   └── 📖 tamilNadu-english.pdf
├── 🐳 DockerFile              # Container configuration
├── 🚫 .gitignore              # Git ignore rules
└── 📖 README.md               # This documentation
```

### Key Features Implementation

- **Vector Similarity Search**: Uses Pinecone for fast document retrieval
- **Contextual AI Responses**: Integrates Cerebras for intelligent answers
- **Multi-document Support**: Query across all books or target specific ones
- **Async Processing**: Non-blocking API responses
- **Scalable Architecture**: Ready for production deployment

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Errors**
   ```
   Error: Invalid API key
   ```
   - Check your `.env` file has correct API keys
   - Ensure no extra spaces in environment variables
   - Verify API keys are active and have proper permissions

2. **Pinecone Connection Issues**
   ```
   Error: Unable to connect to Pinecone
   ```
   - Verify your Pinecone API key and index name
   - Check if your Pinecone index exists and is active
   - Ensure the dimension matches your embedding model (384 for all-MiniLM-L6-v2)

3. **Document Processing Errors**
   ```
   Error: Unable to process PDF
   ```
   - Check if PDF files are not corrupted
   - Ensure PDFs are text-based (not scanned images)
   - Verify sufficient disk space for processing

4. **Port Already in Use**
   ```
   Error: Port 7860 is already in use
   ```
   - Change PORT in your `.env` file
   - Or kill the existing process: `netstat -ano | findstr :7860`

### Environment Variables Checklist

Make sure your `.env` file contains all required variables:

```bash
✅ PINECONE_API_KEY=your-key-here
✅ PINECONE_INDEX_NAME=document-collection  
✅ CEREBRAS_API_KEY=your-key-here
✅ HF_TOKEN=your-token-here
✅ PORT=7860
```

## 📚 Books Directory

The `books/` folder contains all PDF documents that can be queried:

```
books/
├── 📖 tamilNadu-computerScience.pdf    # Tamil Nadu Computer Science curriculum
├── 📖 tamilNadu-english.pdf           # Tamil Nadu English curriculum
└── 📖 [Add your PDFs here]            # Place new books for processing
```

**Note**: After adding new PDFs, run `python document_pinecone.py` to process and index them.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Getting Help

- 📖 **FastAPI Docs**: https://fastapi.tiangolo.com/
- 🔍 **Pinecone Docs**: https://docs.pinecone.io/
- 🤖 **Cerebras Docs**: https://cerebras.ai/
- 🤗 **Hugging Face**: https://huggingface.co/docs
- 🐛 **Issues**: Create an issue in this repository for bugs or feature requests

---

Built with ❤️ by **WeMakeDev** team for intelligent document interaction!