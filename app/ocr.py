from typing import Optional, Dict, Any
import io
from PIL import Image
import pytesseract
import os


def run_ocr(file_bytes: bytes, lang: str = "eng", filename: str = "") -> Dict[str, Any]:
    """Run OCR on provided file bytes and return extracted text.

    Args:
        file_bytes: Raw bytes of an image file (PNG/JPEG/etc.).
        lang: Tesseract language code; default is English ("eng").
        filename: Original filename to determine file type.

    Returns:
        Dict containing extracted text and metadata.
    """
    try:
        # Determine file type from filename
        file_ext = os.path.splitext(filename.lower())[1] if filename else ""
        
        if file_ext == '.pdf':
            raise Exception("PDF processing is not supported. Please use images only.")
        else:
            return _process_image(file_bytes, lang)
            
    except Exception as e:
        raise Exception(f"OCR processing failed: {str(e)}")


def _process_image(image_bytes: bytes, lang: str = "eng") -> Dict[str, Any]:
    """Process image files (PNG, JPEG, etc.)"""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    text = pytesseract.image_to_string(image, lang=lang)
    
    return {
        "text": text.strip(),
        "file_type": "image",
        "pages": 1,
        "confidence": 0.8,  # Tesseract doesn't provide confidence scores
        "word_count": len(text.split()),
        "language": lang
    }




