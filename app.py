
import os
import asyncio
import time
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from query import query_collection, get_available_books, quizz_collection
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFRequest(BaseModel):
    query: str
    book: Optional[str] = None
    message: list[dict] = []
    n_results: Optional[int] = 3
class QuizzRequest(BaseModel):
    book: Optional[str] = None
    n_results: Optional[int] = 3
    question: Optional[str] = 10

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting wemakedev API...")
    yield
    logger.info("🛑 Shutting down API...")

app = FastAPI(
    title="WeMakeDev RAG API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get('/')
async def index():
    return {'message': 'WeMakeDev RAG API', 'version': '1.0.0'}

@app.get('/health')
async def health_check():
    return {'status': 'healthy'}

@app.get('/books')
async def get_books():
    try:
        loop = asyncio.get_event_loop()
        books = await loop.run_in_executor(None, get_available_books)
        return {"books": books, "count": len(books)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post('/quizz')
async def quizz_documents(request: QuizzRequest):
    try:
        logger.info(f"Processing quizz: ...")
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            quizz_collection,
            request.book,
            request.n_results,
            request.question
        )
        return result
    except Exception as e:
        logger.error(f"Quizz error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/query')
async def query_documents(request: PDFRequest):
    try:
        logger.info(f"Processing query: {request.query[:50]}...")
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            query_collection,
            request.query,
            request.message,
            request.book,
            request.n_results
        )
        return result
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
