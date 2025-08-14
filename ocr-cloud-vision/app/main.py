from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.vision_ocr import run_vision_ocr, extract_text_only
from app.processor import chunk_text, extract_metadata
import httpx
import os
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cloud Vision OCR Demo Service", version="0.1.0")

# Environment variables
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")
REGION = os.getenv("REGION", "us-central1")
SUFFIX = os.getenv("SUFFIX", "demo")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "cloud-vision-ocr",
        "project": PROJECT_ID,
        "region": REGION,
        "suffix": SUFFIX
    }

@app.post("/ocr")
async def ocr_endpoint(
    file: UploadFile = File(...),
    lang: str = Form("en")
):
    """
    Extract text from uploaded image using Google Cloud Vision API
    """
    try:
        # Validate file type - handle None content_type
        if file.content_type is None:
            # Try to infer content type from filename
            filename = file.filename.lower() if file.filename else ""
            if not any(ext in filename for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.pdf']):
                raise HTTPException(status_code=400, detail="File must be an image and pdf (PNG, JPG, JPEG, GIF, BMP, TIFF, PDF)")
        elif not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image or pdf")
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Run OCR
        result = run_vision_ocr(image_bytes, lang, file.filename)
        
        return {
            "filename": file.filename,
            "text": result["text"],
            "confidence": result["confidence"],
            "word_count": result["word_count"],
            "language": result["language"],
            "detected_language": result["detected_language"],
            "file_type": result["file_type"],
            "pages": result["pages"],
            "ocr_engine": "google-cloud-vision"
        }
        
    except Exception as e:
        logger.error(f"OCR error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

@app.post("/ocr-and-index")
async def ocr_and_index(
    file: UploadFile = File(...),
    lang: str = Form("en"),
    enable_rag: bool = Form(False)
):
    """
    Extract text and optionally index it in RAG service
    """
    try:
        # Validate file type - handle None content_type
        if file.content_type is None:
            # Try to infer content type from filename
            filename = file.filename.lower() if file.filename else ""
            if not any(ext in filename for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.pdf']):
                raise HTTPException(status_code=400, detail="File must be an image (PNG, JPG, JPEG, GIF, BMP, TIFF, PDF)")
        elif not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image or pdf")
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Run OCR
        ocr_result = run_vision_ocr(image_bytes, lang, file.filename)
        text = ocr_result["text"]
        
        result = {
            "filename": file.filename,
            "text": text,
            "confidence": ocr_result["confidence"],
            "file_type": ocr_result["file_type"],
            "pages": ocr_result["pages"],
            "word_count": ocr_result["word_count"],
            "language": ocr_result["language"],
            "detected_language": ocr_result["detected_language"],
            "ocr_engine": "google-cloud-vision",
            "indexed": False,
            "chunks_added": 0
        }
        
        # RAG indexing if enabled
        if enable_rag and text.strip():
            rag_url = RAG_SERVICE_URL
            if not rag_url:
                # Construct RAG service URL if not provided
                if PROJECT_ID:
                    # Use the correct Cloud Run URL format
                    rag_url = f"https://rag-service-{SUFFIX}-{PROJECT_ID}.{REGION}.run.app"
                    # Note: The actual URL will be different due to revision ID, but this should work for basic connectivity
            
            if rag_url:
                try:
                    # Process text for RAG
                    chunks = chunk_text(text)
                    metadata = extract_metadata(text, file.filename)
                    
                    # Prepare chunks for RAG service
                    rag_chunks = []
                    for i, chunk in enumerate(chunks):
                        rag_chunks.append({
                            "id": f"{file.filename}_chunk_{i}",
                            "text": chunk,
                            "source": file.filename,  # Add source field at root level
                            "metadata": {
                                **metadata,
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                                "confidence": ocr_result["confidence"],
                                "ocr_engine": "google-cloud-vision"
                            }
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
                            result["rag_error"] = f"RAG service returned {response.status_code}: {response.text}"
                            
                except Exception as e:
                    logger.error(f"RAG indexing error: {str(e)}")
                    result["rag_error"] = f"RAG indexing failed: {str(e)}"
            else:
                result["rag_error"] = "RAG service URL not configured."
        
        return result
        
    except Exception as e:
        logger.error(f"OCR and index error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/info")
async def service_info():
    """Get service information and configuration"""
    return {
        "service": "cloud-vision-ocr",
        "version": "0.1.0",
        "ocr_engine": "google-cloud-vision",
        "rag_enabled": bool(RAG_SERVICE_URL),
        "rag_service_url": RAG_SERVICE_URL,
        "project_id": PROJECT_ID,
        "region": REGION,
        "suffix": SUFFIX
    } 