from typing import Optional, Dict, Any
import io
from PIL import Image
from google.cloud import vision
import base64
import os

def run_vision_ocr(file_bytes: bytes, lang: str = "en", filename: str = "") -> Dict[str, Any]:
    """
    Extract text from image using Google Cloud Vision API
    
    Args:
        file_bytes: File data as bytes (image only)
        lang: Language hint (e.g., 'en', 'es', 'fr')
        filename: Original filename to determine file type
    
    Returns:
        Dict containing extracted text and confidence scores
    """
    try:
        # Determine file type from filename
        file_ext = os.path.splitext(filename.lower())[1] if filename else ""
        
        if file_ext == '.pdf':
            raise Exception("Cloud Vision API does not support PDF processing. Please use images only.")
        else:
            return _process_image_vision(file_bytes, lang)
            
    except Exception as e:
        raise Exception(f"Vision OCR failed: {str(e)}")


def _process_image_vision(image_bytes: bytes, lang: str = "en") -> Dict[str, Any]:
    """Process image files using Cloud Vision API"""
    try:
        # Initialize Vision client
        client = vision.ImageAnnotatorClient()
        
        # Create image object
        image = vision.Image(content=image_bytes)
        
        # Perform text detection
        response = client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(f"Vision API Error: {response.error.message}")
        
        # Extract text and confidence
        texts = response.text_annotations
        if not texts:
            return {
                "text": "",
                "confidence": 0.0,
                "word_count": 0,
                "language": lang,
                "detected_language": lang,
                "file_type": "image",
                "pages": 1
            }
        
        # Get full text (first annotation contains all text)
        full_text = texts[0].description.strip()
        
        # Calculate average confidence from individual words
        word_confidences = []
        for text in texts[1:]:  # Skip first (full text) annotation
            if hasattr(text, 'confidence') and text.confidence:
                word_confidences.append(text.confidence)
        
        avg_confidence = sum(word_confidences) / len(word_confidences) if word_confidences else 0.0
        
        # Count words
        word_count = len(full_text.split())
        
        # Try to get detected language from full text annotation
        detected_language = lang
        if hasattr(response, 'full_text_annotation') and response.full_text_annotation:
            if response.full_text_annotation.pages:
                page = response.full_text_annotation.pages[0]
                if hasattr(page, 'property') and page.property:
                    if hasattr(page.property, 'detected_languages') and page.property.detected_languages:
                        detected_language = page.property.detected_languages[0].language_code
        
        return {
            "text": full_text,
            "confidence": round(avg_confidence, 3),
            "word_count": word_count,
            "language": lang,
            "detected_language": detected_language,
            "file_type": "image",
            "pages": 1
        }
        
    except Exception as e:
        raise Exception(f"Image Vision OCR failed: {str(e)}")





def extract_text_only(file_bytes: bytes, lang: str = "en", filename: str = "") -> str:
    """
    Simple function to extract just the text (for backward compatibility)
    
    Args:
        file_bytes: File data as bytes
        lang: Language hint
        filename: Original filename
    
    Returns:
        Extracted text as string
    """
    result = run_vision_ocr(file_bytes, lang, filename)
    return result["text"] 