import re
from typing import List, Dict, Any
from datetime import datetime

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for RAG processing
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk (characters)
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If this isn't the last chunk, try to break at a sentence boundary
        if end < len(text):
            # Look for sentence endings within the last 100 characters of the chunk
            search_start = max(start, end - 100)
            sentence_end = text.rfind('.', search_start, end)
            if sentence_end > start:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position, accounting for overlap
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

def extract_metadata(text: str, filename: str) -> Dict[str, Any]:
    """
    Extract metadata from text and filename
    
    Args:
        text: Extracted text
        filename: Original filename
    
    Returns:
        Dictionary of metadata
    """
    metadata = {
        "source": filename,
        "extraction_date": datetime.now().isoformat(),
        "text_length": len(text),
        "word_count": len(text.split()) if text else 0,
        "file_type": filename.split('.')[-1].lower() if '.' in filename else "unknown"
    }
    
    # Try to extract document type from content
    text_lower = text.lower()
    if any(word in text_lower for word in ['invoice', 'bill', 'receipt']):
        metadata["document_type"] = "invoice"
    elif any(word in text_lower for word in ['contract', 'agreement', 'terms']):
        metadata["document_type"] = "contract"
    elif any(word in text_lower for word in ['report', 'analysis', 'summary']):
        metadata["document_type"] = "report"
    elif any(word in text_lower for word in ['letter', 'email', 'correspondence']):
        metadata["document_type"] = "correspondence"
    else:
        metadata["document_type"] = "general"
    
    # Extract language hints
    if re.search(r'[а-яё]', text, re.IGNORECASE):
        metadata["language_hint"] = "russian"
    elif re.search(r'[ñáéíóúü]', text, re.IGNORECASE):
        metadata["language_hint"] = "spanish"
    elif re.search(r'[àâäéèêëïîôöùûüÿç]', text, re.IGNORECASE):
        metadata["language_hint"] = "french"
    else:
        metadata["language_hint"] = "english"
    
    return metadata 