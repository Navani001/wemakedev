from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import json

# Initialize Chroma client with persistent storage
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Recreate the collection
try:
    chroma_client.delete_collection(name="document_collection")
except:
    pass

collection = chroma_client.create_collection(name="document_collection")

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Size of each chunk
    chunk_overlap=200,      # Overlap between chunks
    length_function=len,    # Function to measure length
    separators=["\n\n", "\n", " ", ""]  # Separators to split on
)

# Load and process PDF
loader = PyPDFLoader('./book.pdf')
pages = []

print("Loading and splitting PDF documents...")

# Process each page and split into chunks
all_chunks = []
chunk_metadata = []
chunk_ids = []

for page_num, page in enumerate(loader.lazy_load()):
    pages.append(page)
    
    # Split the page content into chunks
    chunks = text_splitter.split_text(page.page_content)
    
    for chunk_num, chunk in enumerate(chunks):
        # Create unique ID for each chunk
        chunk_id = f"page_{page_num}_chunk_{chunk_num}"
        
        # Store chunk and metadata
        all_chunks.append(chunk)
        chunk_ids.append(chunk_id)
        
        # Enhanced metadata including original page info
        metadata = {
            "page_number": page_num,
            "chunk_number": chunk_num,
            "source": page.metadata.get('source', 'unknown'),
            "total_pages": len(pages) if hasattr(loader, '__len__') else 'unknown'
        }
        chunk_metadata.append(metadata)

print(f"Created {len(all_chunks)} chunks from {len(pages)} pages")

# Add all chunks to ChromaDB collection
if all_chunks:
    collection.add(
        ids=chunk_ids,
        documents=all_chunks,
        metadatas=chunk_metadata
    )
    
    print("Documents successfully embedded in ChromaDB!")
   
    
    
else:
    print("No content found to embed!")

    print(f"\n" + "="*50)
    print("First page metadata:")
    print(f"{pages[0].metadata}")
    print(f"\nFirst page content preview:")
    print(f"{pages[0].page_content[:300]}{'...' if len(pages[0].page_content) > 300 else ''}")