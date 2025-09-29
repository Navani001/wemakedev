# Initialize Chroma client
import chromadb
chroma_client = chromadb.PersistentClient(path="./chroma_db")
import os
from cerebras.cloud.sdk import Cerebras 
# Get existing collection (don't create new one!)
def get_existing_collection():
  try:
      collection = chroma_client.get_collection(name="document_collection")
      print(collection)
      print(f"✅ Connected to existing collection with {collection.count()} documents")
      return collection
  except Exception as e:
      print(f"❌ Collection not found: {e}")
      print("Please run 'python document.py' first to create and populate the collection!")
      exit()
def query_collection(query):
  collection = get_existing_collection()
  results = collection.query(
      query_texts=[query],
      n_results=3,  # Return top 3 most relevant chunks
      include=['documents', 'metadatas', 'distances']
  )
  
  client = Cerebras(
    api_key="csk-tj9fe8htptknv3e6p9cw53cxcdte453m93ecpp42566rhwrj",
  )

  chat_completion = client.chat.completions.create(
    messages=[
    {"role": "user", "content": query,"context": results['documents'][0]},
  ],
    model="llama-4-scout-17b-16e-instruct",
  )
  return chat_completion.choices[0].message