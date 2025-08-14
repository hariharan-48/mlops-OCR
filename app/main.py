from fastapi import FastAPI, UploadFile, File, Form
from app.ocr import run_ocr
from app.processor import chunk_text, extract_metadata
import httpx
import os
from typing import Optional

app = FastAPI(title="OCR Demo Service", version="0.1.0")

# RAG service URL (will be set by environment variable or constructed)
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "")

@app.get("/health")
def health():
    return {"status": "ok", "service": "ocr"}

@app.post("/ocr")
async def ocr(file: UploadFile = File(...), lang: str = "eng"):
    file_bytes = await file.read()
    result = run_ocr(file_bytes, lang=lang, filename=file.filename)
    return {
        "filename": file.filename,
        "text": result["text"],
        "file_type": result["file_type"],
        "pages": result["pages"],
        "confidence": result["confidence"],
        "word_count": result["word_count"],
        "language": result["language"],
        "ocr_engine": "tesseract"
    }

@app.post("/ocr-and-index")
async def ocr_and_index(
    file: UploadFile = File(...), 
    lang: str = "eng",
    enable_rag: bool = Form(False)
):
    """OCR + optional RAG indexing"""
    file_bytes = await file.read()
    ocr_result = run_ocr(file_bytes, lang=lang, filename=file.filename)
    text = ocr_result["text"]
    
    result = {
        "filename": file.filename,
        "text": text,
        "file_type": ocr_result["file_type"],
        "pages": ocr_result["pages"],
        "confidence": ocr_result["confidence"],
        "word_count": ocr_result["word_count"],
        "language": ocr_result["language"],
        "ocr_engine": "tesseract",
        "indexed": False
    }
    
    # If RAG is enabled, try to index the document
    if enable_rag:
        # Try to get RAG service URL
        rag_url = RAG_SERVICE_URL
        if not rag_url:
            # Try to construct from environment variables
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            region = os.getenv("REGION", "us-central1")
            suffix = os.getenv("SUFFIX", "demo")
            if project_id:
                rag_url = f"https://rag-service-{suffix}-{project_id}.{region}.run.app"
        
        if rag_url:
            try:
                # Process document for RAG
                chunks = chunk_text(text)
                metadata = extract_metadata(text, file.filename)
                
                # Prepare chunks for RAG service
                rag_chunks = []
                for i, chunk in enumerate(chunks):
                    rag_chunks.append({
                        "text": chunk["text"],
                        "source": f"{file.filename}_chunk_{i}",
                        "metadata": {**metadata, "chunk_id": i, "start": chunk["start"], "end": chunk["end"]}
                    })
                
                # Send to RAG service
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{rag_url}/add-documents",
                        json=rag_chunks,
                        timeout=30.0
                    )
                    if response.status_code == 200:
                        result["indexed"] = True
                        result["chunks_added"] = len(rag_chunks)
                        result["rag_url"] = rag_url
                    else:
                        result["rag_error"] = f"Failed to index: {response.status_code} - {response.text}"
                        
            except Exception as e:
                result["rag_error"] = f"RAG indexing failed: {str(e)}"
                result["rag_url_attempted"] = rag_url
        else:
            result["rag_error"] = "RAG service URL not configured. Set RAG_SERVICE_URL environment variable."
    
    return result

