import re
from typing import List, Dict

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
    """
    Simple text chunking for RAG demo.
    In production, use more sophisticated chunking strategies.
    """
    # Clean and normalize text
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) <= chunk_size:
        return [{"text": text, "start": 0, "end": len(text)}]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundaries
        if end < len(text):
            # Look for sentence endings
            for i in range(end, max(start + chunk_size - 100, start), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "start": start,
                "end": end
            })
        
        # Move start position with overlap
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

def extract_metadata(text: str, source: str) -> Dict:
    """
    Extract basic metadata from document.
    In production, use more sophisticated extraction.
    """
    return {
        "source": source,
        "length": len(text),
        "word_count": len(text.split()),
        "has_numbers": bool(re.search(r'\d', text)),
        "has_dates": bool(re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text))
    } 