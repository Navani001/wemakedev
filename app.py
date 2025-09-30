
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from typing import Optional, Any
import requests
import uvicorn
import logging
import time
from query import query_collection
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Pydantic models for request/response validation
class PDFRequest(BaseModel):
   query:str
   book:str
    
class PDFResponse(BaseModel):
    message: str
    username: str
    status: str

app = FastAPI(title="wemakedev", version="1.0.0")


@app.get('/')
def index():
    """Home page"""
    return {
        'message': 'Welcome to Flask API',
        'version': '1.0.0',
        'status': 'running'
    }

@app.get('/api/health')
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy'}

@app.post('/pdf')
def pdf(request: PDFRequest):
    """Handle PDF processing requests"""
    try:
        # Return structured response
        return {
            "message": "PDF request processed successfully",
            "result": query_collection(request.query,request.book)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
# Run the app if the script is executed directly
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))  # Hugging Face Spaces uses port 7860
    uvicorn.run(app, host="0.0.0.0", port=port)
