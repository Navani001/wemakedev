import os
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from huggingface_hub import hf_hub_download, list_repo_files
from config import HF_CACHE_DIR, PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_DIMENSION, EMBEDDING_MODEL, HF_TOKEN

repo_id = "Navanihk/books"
os.makedirs(HF_CACHE_DIR, exist_ok=True)

print("🔧 Initializing Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)

if HF_TOKEN:
    os.environ['HF_TOKEN'] = HF_TOKEN

print(f"🤖 Loading embedding model: {EMBEDDING_MODEL}")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

print(f"📊 Setting up Pinecone index: {PINECONE_INDEX_NAME}")
existing_indexes = pc.list_indexes()
index_names = [idx['name'] for idx in existing_indexes.indexes]

if PINECONE_INDEX_NAME not in index_names:
    print(f"📝 Creating new index '{PINECONE_INDEX_NAME}'")
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=PINECONE_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    time.sleep(10)

index = pc.Index(PINECONE_INDEX_NAME)
print(f"🔗 Connected to Pinecone index")

print("📚 Fetching books from Hugging Face...")
try:
    repo_files = list_repo_files(repo_id=repo_id, token=HF_TOKEN)
    pdf_files = [f for f in repo_files if f.endswith('.pdf')]
except Exception:
    pdf_files = ["tamilNadu-computerScience.pdf"]

downloaded_files = []
for pdf_file in pdf_files:
    try:
        pdf_path = hf_hub_download(repo_id=repo_id, filename=pdf_file, cache_dir=HF_CACHE_DIR, token=HF_TOKEN)
        downloaded_files.append({"filename": pdf_file, "path": pdf_path})
        print(f"✅ Downloaded {pdf_file}")
    except Exception as e:
        print(f"❌ Failed to download {pdf_file}: {e}")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
print("🔄 Processing documents...")

all_vectors = []
batch_size = 100

for file_info in downloaded_files:
    filename = file_info["filename"]
    file_path = file_info["path"]
    
    loader = PyPDFLoader(file_path)
    print(f"📖 Processing {filename}...")

    for page_num, page in enumerate(loader.lazy_load()):
        chunks = text_splitter.split_text(page.page_content)
        
        for chunk_num, chunk in enumerate(chunks):
            chunk_id = f"{filename}_page_{page_num}_chunk_{chunk_num}"
            embedding = embedding_model.encode(chunk).tolist()
            
            metadata = {
                "text": chunk,
                "page_number": page_num,
                "chunk_number": chunk_num,
                "source": file_path,
                "book": filename
            }
            
            vector = {"id": chunk_id, "values": embedding, "metadata": metadata}
            all_vectors.append(vector)

print(f"⬆️ Uploading {len(all_vectors)} vectors...")
for i in range(0, len(all_vectors), batch_size):
    batch = all_vectors[i:i + batch_size]
    index.upsert(vectors=batch)
    print(f"✅ Uploaded batch {i//batch_size + 1}")

final_stats = index.describe_index_stats()
print(f"🎉 Complete! Total vectors: {final_stats.total_vector_count}")

# Test query
query_embedding = embedding_model.encode("what is array").tolist()
results = index.query(vector=query_embedding, top_k=2, include_metadata=True)
print(f"📊 Test query found {len(results.matches)} results")