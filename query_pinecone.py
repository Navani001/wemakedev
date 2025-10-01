import os
import subprocess
import sys
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from cerebras.cloud.sdk import Cerebras
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME, EMBEDDING_MODEL, HF_TOKEN, CEREBRAS_API_KEY
import json
pc = None
index = None
embedding_model = None

def initialize_pinecone():
    global pc, index, embedding_model
    
    if pc is None:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        print(f"🔗 Connected to Pinecone index: {PINECONE_INDEX_NAME}")
    
    if embedding_model is None:
        if HF_TOKEN:
            os.environ['HF_TOKEN'] = HF_TOKEN
        embedding_model = SentenceTransformer(EMBEDDING_MODEL)

def get_existing_collection():
    global pc, index, embedding_model
    
    try:
        initialize_pinecone()
        stats = index.describe_index_stats()
        if stats.total_vector_count > 0:
            print(f"✅ Connected to existing index with {stats.total_vector_count} documents")
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ Index not found, running document processing...")
        try:
            result = subprocess.run([sys.executable, "document_pinecone.py"], timeout=600)
            if result.returncode == 0:
                initialize_pinecone()
                return True
        except Exception:
            pass
        return False

def get_available_books():
    global pc, index, embedding_model
    
    if not get_existing_collection():
        return []
    
    try:
        sample_query = embedding_model.encode("book").tolist()
        results = index.query(vector=sample_query, top_k=1000, include_metadata=True)
        
        books = set()
        for match in results.matches:
            if 'book' in match.metadata:
                books.add(match.metadata['book'])
        return list(books)
    except Exception:
        return []

def quizz_collection(book=None, n_results=3,question=10):
    
    global pc, index, embedding_model
    
    if not get_existing_collection():
        raise Exception("No data available in Pinecone index")
    
    query_embedding = embedding_model.encode("topics topic").tolist()
    
    query_params = {"vector": query_embedding, "top_k": n_results, "include_metadata": True}
    if book:
        query_params["filter"] = {"book": book}
        print(f"🔍 Searching in book: {book}")
    
    results = index.query(**query_params)
    print(f"📊 Found {len(results.matches)} relevant chunks")
    
    contexts = [match.metadata['text'] for match in results.matches if 'text' in match.metadata]
    context = "\n\n".join(contexts)
    
    client = Cerebras(api_key=CEREBRAS_API_KEY)
    question_schema = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "topic": {"type": "string"},
                    "answer": {"type": "string"},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                    }
                },
            },
        },
    },
    "additionalProperties": False
}
    system_prompt = """You are a helpful assistant for educational books. give me ${question} quizz questions. you generate a quizz question with 4 options and also provide the correct answer. Always cite which book the information comes from when possible and also don't include based on context liked."""

    user_prompt = f"""
topics from books: {context}
Please provide a helpful quiz question with 4 options and the correct answer based on the topic above, create {question} questions based on the topic and also don't include any personal opinions or information not contained in the context and also don't include based on context liked"""
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model="llama-4-scout-17b-16e-instruct",
        response_format={
        "type": "json_schema", 
        "json_schema": {
            "name": "question_schema",
            "strict": True,
            "schema": question_schema
        }
    }
    )
   

    return {
        "message": json.loads(chat_completion.choices[0].message.content),
        "available_books": get_available_books(),
        "query_book_filter": book
    }
def query_collection(query, message=None, book=None, n_results=3):
    
    global pc, index, embedding_model
    
    if not get_existing_collection():
        raise Exception("No data available in Pinecone index")
    
    query_embedding = embedding_model.encode(query).tolist()
    
    query_params = {"vector": query_embedding, "top_k": n_results, "include_metadata": True}
    if book:
        query_params["filter"] = {"book": book}
        print(f"🔍 Searching in book: {book}")
    
    results = index.query(**query_params)
    print(f"📊 Found {len(results.matches)} relevant chunks")
    
    contexts = [match.metadata['text'] for match in results.matches if 'text' in match.metadata]
    context = "\n\n".join(contexts)
    
    client = Cerebras(api_key=CEREBRAS_API_KEY)

    system_prompt = """You are a helpful assistant for educational books. Use the provided context to answer accurately. Always cite which book the information comes from when possible and also don't include based on context liked."""

    user_prompt = f"""Question: {query}
Context from books: {context}
Please provide a helpful answer based on the context above and also don't include any personal opinions or information not contained in the context and also don't include based on context liked"""
    if(message):
        message=[  {"role": "system", "content": system_prompt}]+message+[{"role": "user", "content": user_prompt}]
    # chat_completion = client.chat.completions.create(
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_prompt}
    #     ],
    #     model="llama-4-scout-17b-16e-instruct",
    # )
    print("messages to send to backend: "+str(message))
    chat_completion = client.chat.completions.create(
        messages=message,
        model="llama-4-scout-17b-16e-instruct",
    )
    
    sources_info = [{
        "id": match.id,
        "book": match.metadata.get('book', 'unknown'),
        "page": match.metadata.get('page_number', 'unknown'),
        "score": match.score
    } for match in results.matches]
    
    return {
        "message": chat_completion.choices[0].message.content,
        "sources": sources_info,
        "available_books": get_available_books(),
        "query_book_filter": book
    }