from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import vertexai
from vertexai.generative_models import GenerativeModel
import os
from model_registry import model_registry, register_rag_model
from metrics import metrics, METRIC_QUERIES_TOTAL, METRIC_QUERIES_SUCCESS, METRIC_QUERIES_ERROR, METRIC_QUERY_DURATION, METRIC_DOCUMENTS_INDEXED, METRIC_DOCUMENTS_TOTAL

app = FastAPI(title="RAG Query Service", version="0.1.0")

# Initialize Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("REGION", "us-central1")
vertexai.init(project=project_id, location=location)

# Register model in registry
register_rag_model()

# Simple in-memory storage for demo (replace with Vector Search in production)
document_store = {}

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

class DocumentChunk(BaseModel):
    text: str
    source: str
    metadata: dict

@app.get("/health")
def health():
    return {"status": "ok", "service": "rag-query"}

@app.post("/add-documents")
async def add_documents(chunks: List[DocumentChunk]):
    """Add document chunks to the store (simplified for demo)"""
    for i, chunk in enumerate(chunks):
        doc_id = f"doc_{len(document_store) + i}"
        document_store[doc_id] = {
            "text": chunk.text,
            "source": chunk.source,
            "metadata": chunk.metadata
        }
    
    # Track metrics
    metrics.increment_counter(METRIC_DOCUMENTS_INDEXED, len(chunks))
    metrics.increment_counter(METRIC_DOCUMENTS_TOTAL, len(chunks))
    
    return {"status": "added", "count": len(chunks)}

@app.post("/query")
async def query_rag(request: QueryRequest):
    """Simple RAG query using text similarity and LLM"""
    # Start timing
    metrics.start_timer(METRIC_QUERY_DURATION)
    metrics.increment_counter(METRIC_QUERIES_TOTAL)
    
    if not document_store:
        metrics.increment_counter(METRIC_QUERIES_ERROR)
        metrics.end_timer(METRIC_QUERY_DURATION)
        raise HTTPException(status_code=400, detail="No documents indexed")
    
    # Simple keyword matching (replace with proper vector search)
    relevant_docs = []
    query_lower = request.query.lower()
    
    for doc_id, doc in document_store.items():
        if any(word in doc["text"].lower() for word in query_lower.split()):
            relevant_docs.append({
                "id": doc_id,
                "text": doc["text"],
                "source": doc["source"],
                "score": 0.8  # Simplified scoring
            })
    
    # Sort by score and take top_k
    relevant_docs.sort(key=lambda x: x["score"], reverse=True)
    relevant_docs = relevant_docs[:request.top_k]
    
    if not relevant_docs:
        return {
            "answer": "I couldn't find relevant information in the documents.",
            "sources": [],
            "query": request.query
        }
    
    # Create context from relevant documents
    context = "\n\n".join([doc["text"] for doc in relevant_docs])
    
    # Generate response using Vertex AI Gemini 2.5 Flash
    try:
        model = GenerativeModel("gemini-2.5-flash")
        prompt = f"""Based on the following context, answer the question. If the context doesn't contain enough information, say so.

Context:
{context}

Question: {request.query}

Answer:"""
        
        response = model.generate_content(prompt)
        
        # Track success and timing
        metrics.increment_counter(METRIC_QUERIES_SUCCESS)
        metrics.end_timer(METRIC_QUERY_DURATION)
        
        return {
            "answer": response.text,
            "sources": [{"id": doc["id"], "source": doc["source"]} for doc in relevant_docs],
            "query": request.query,
            "context_used": len(relevant_docs)
        }
    except Exception as e:
        # Track error and timing
        metrics.increment_counter(METRIC_QUERIES_ERROR)
        metrics.end_timer(METRIC_QUERY_DURATION)
        
        return {
            "answer": f"Error generating response: {str(e)}",
            "sources": [{"id": doc["id"], "source": doc["source"]} for doc in relevant_docs],
            "query": request.query
        }

@app.get("/documents")
async def list_documents():
    """List all indexed documents (for debugging)"""
    return {
        "count": len(document_store),
        "documents": [
            {"id": doc_id, "source": doc["source"], "text_preview": doc["text"][:100] + "..."}
            for doc_id, doc in document_store.items()
        ]
    }

@app.get("/models")
async def list_models():
    """List all registered models"""
    return {
        "models": model_registry.list_models(),
        "total_models": len(model_registry.list_models())
    }

@app.get("/models/{model_name}")
async def get_model_versions(model_name: str):
    """Get all versions of a specific model"""
    versions = model_registry.get_model_versions(model_name)
    return {
        "model_name": model_name,
        "versions": versions,
        "total_versions": len(versions)
    }

@app.get("/models/{model_name}/latest")
async def get_latest_model(model_name: str):
    """Get the latest version of a model"""
    latest = model_registry.get_latest_model(model_name)
    if not latest:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    return latest

@app.get("/metrics")
async def get_metrics():
    """Get all metrics"""
    return metrics.get_all_metrics()

@app.get("/metrics/summary")
async def get_metrics_summary():
    """Get a summary of key metrics"""
    return {
        "total_queries": metrics.get_counter(METRIC_QUERIES_TOTAL),
        "successful_queries": metrics.get_counter(METRIC_QUERIES_SUCCESS),
        "failed_queries": metrics.get_counter(METRIC_QUERIES_ERROR),
        "success_rate": f"{(metrics.get_counter(METRIC_QUERIES_SUCCESS) / max(metrics.get_counter(METRIC_QUERIES_TOTAL), 1)) * 100:.1f}%",
        "avg_query_time": f"{metrics.get_timing_stats(METRIC_QUERY_DURATION)['avg'] * 1000:.1f}ms",
        "total_documents": metrics.get_counter(METRIC_DOCUMENTS_TOTAL),
        "indexed_documents": metrics.get_counter(METRIC_DOCUMENTS_INDEXED)
    } 