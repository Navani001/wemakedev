import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Hugging Face Configuration
HF_CACHE_DIR = os.environ.get('HF_CACHE_DIR', './hf_cache')
HF_TOKEN = os.environ.get('HF_TOKEN')

# Pinecone Configuration
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.environ.get('PINECONE_INDEX_NAME', 'document-collection')
PINECONE_DIMENSION = int(os.environ.get('PINECONE_DIMENSION', '384'))
EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')

# Cerebras API Configuration
CEREBRAS_API_KEY = os.environ.get('CEREBRAS_API_KEY')