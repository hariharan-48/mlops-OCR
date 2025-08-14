import streamlit as st
import requests
import json
import os
import subprocess
import ssl
import urllib3
from typing import Dict, List, Any
import time

# Disable SSL warnings and certificate verification for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Page configuration
st.set_page_config(
    page_title="OCR + RAG Document Q&A",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .service-status {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-ok {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .response-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .upload-section {
        background-color: #e3f2fd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def get_service_urls() -> Dict[str, str]:
    """Get service URLs dynamically using gcloud"""
    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        region = os.getenv("REGION", "us-central1")
        suffix = os.getenv("SUFFIX", "demo")
        
        if project_id:
            # Fetch URLs using gcloud
            ocr_url = subprocess.check_output([
                "gcloud", "run", "services", "describe", 
                f"vision-ocr-service-{suffix}", 
                "--region", region, 
                "--format", "value(status.url)"
            ], text=True).strip()
            
            rag_url = subprocess.check_output([
                "gcloud", "run", "services", "describe", 
                f"rag-service-{suffix}", 
                "--region", region, 
                "--format", "value(status.url)"
            ], text=True).strip()
            
            return {
                "ocr": ocr_url,
                "rag": rag_url
            }
        else:
            return {
                "ocr": os.getenv("OCR_SERVICE_URL", ""),
                "rag": os.getenv("RAG_SERVICE_URL", "")
            }
    except Exception as e:
        st.error(f"Error fetching service URLs: {str(e)}")
        return {
            "ocr": os.getenv("OCR_SERVICE_URL", ""),
            "rag": os.getenv("RAG_SERVICE_URL", "")
        }

def check_service_health(url: str, service_name: str) -> Dict[str, Any]:
    """Check if a service is healthy with SSL verification disabled"""
    try:
        # Disable SSL verification for development
        response = requests.get(f"{url}/health", timeout=10, verify=False)
        if response.status_code == 200:
            return {"status": "ok", "data": response.json()}
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def upload_and_process_image(file, enable_rag: bool = True) -> Dict[str, Any]:
    """Upload image and process with OCR + RAG"""
    urls = get_service_urls()
    ocr_url = urls["ocr"]
    
    if not ocr_url:
        return {"error": "OCR service URL not configured"}
    
    try:
        files = {"file": file}
        data = {"lang": "en", "enable_rag": enable_rag}
        
        # Disable SSL verification for development
        response = requests.post(
            f"{ocr_url}/ocr-and-index",
            files=files,
            data=data,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"OCR service error: {response.status_code} - {response.text}"}
            
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}

def query_rag(question: str, top_k: int = 3) -> Dict[str, Any]:
    """Query the RAG service"""
    urls = get_service_urls()
    rag_url = urls["rag"]
    
    if not rag_url:
        return {"error": "RAG service URL not configured"}
    
    try:
        payload = {
            "query": question,
            "top_k": top_k
        }
        
        # Disable SSL verification for development
        response = requests.post(
            f"{rag_url}/query",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"RAG service error: {response.status_code} - {response.text}"}
            
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}

def get_indexed_documents() -> Dict[str, Any]:
    """Get list of indexed documents"""
    urls = get_service_urls()
    rag_url = urls["rag"]
    
    if not rag_url:
        return {"error": "RAG service URL not configured"}
    
    try:
        # Disable SSL verification for development
        response = requests.get(f"{rag_url}/documents", timeout=10, verify=False)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to get documents: {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Failed to get documents: {str(e)}"}

# Main application
def main():
    st.markdown('<h1 class="main-header">📄 OCR + RAG Document Q&A System</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Service URLs
        st.subheader("Service URLs")
        urls = get_service_urls()
        
        ocr_url = st.text_input("OCR Service URL", value=urls["ocr"], key="ocr_url")
        rag_url = st.text_input("RAG Service URL", value=urls["rag"], key="rag_url")
        
        # Service health check
        st.subheader("Service Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ocr_health = check_service_health(ocr_url, "OCR")
            if ocr_health["status"] == "ok":
                st.markdown('<div class="service-status status-ok">✅ OCR Service</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="service-status status-error">❌ OCR Service</div>', unsafe_allow_html=True)
                st.caption(f"Error: {ocr_health['message']}")
        
        with col2:
            rag_health = check_service_health(rag_url, "RAG")
            if rag_health["status"] == "ok":
                st.markdown('<div class="service-status status-ok">✅ RAG Service</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="service-status status-error">❌ RAG Service</div>', unsafe_allow_html=True)
                st.caption(f"Error: {rag_health['message']}")
        
        # Indexed documents
        st.subheader("📚 Indexed Documents")
        documents = get_indexed_documents()
        
        if "error" not in documents:
            st.write(f"**Total Documents:** {documents.get('count', 0)}")
            
            if documents.get('documents'):
                for doc in documents['documents'][:5]:  # Show first 5
                    st.write(f"• {doc['source']}")
                if len(documents['documents']) > 5:
                    st.write(f"... and {len(documents['documents']) - 5} more")
        else:
            st.error(f"Error: {documents['error']}")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Images")
        
        with st.container():
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'],
                help="Upload an image containing text to extract and index"
            )
            
            enable_rag = st.checkbox("Enable RAG indexing", value=True, help="Index the extracted text for Q&A")
            
            if uploaded_file is not None:
                st.write(f"**File:** {uploaded_file.name}")
                st.write(f"**Size:** {uploaded_file.size} bytes")
                
                # Show file type information
                file_ext = uploaded_file.name.lower().split('.')[-1] if '.' in uploaded_file.name else 'unknown'
                st.info("🖼️ Image file detected")
                
                if st.button("🚀 Process Document", type="primary"):
                    with st.spinner("Processing document..."):
                        result = upload_and_process_image(uploaded_file, enable_rag)
                        
                        if "error" not in result:
                            st.success("✅ Document processed successfully!")
                            
                            # Display OCR results
                            st.subheader("📝 Extracted Text")
                            st.text_area("OCR Result", result.get("text", ""), height=150)
                            
                            # Display metadata
                            st.subheader("📊 Processing Details")
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("Confidence", f"{result.get('confidence', 0):.2f}")
                                st.metric("Word Count", result.get("word_count", 0))
                            with col_b:
                                st.metric("Language", result.get("detected_language", "Unknown"))
                                st.metric("Chunks Added", result.get("chunks_added", 0))
                            
                            # RAG status
                            if result.get("indexed"):
                                st.success("✅ Document indexed for Q&A")
                            elif "rag_error" in result:
                                st.error(f"❌ RAG indexing failed: {result['rag_error']}")
                            
                            # Add to session state
                            st.session_state.uploaded_files.append({
                                "filename": uploaded_file.name,
                                "result": result
                            })
                        else:
                            st.error(f"❌ Processing failed: {result['error']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.header("❓ Ask Questions")
        
        # Question input
        question = st.text_input(
            "Ask a question about your documents:",
            placeholder="What is this document about?",
            help="Ask questions about the documents you've uploaded"
        )
        
        top_k = st.slider("Number of relevant chunks", min_value=1, max_value=10, value=3)
        
        if st.button("🔍 Search", type="primary") and question:
            with st.spinner("Searching for answers..."):
                result = query_rag(question, top_k)
                
                if "error" not in result:
                    st.markdown('<div class="response-box">', unsafe_allow_html=True)
                    st.subheader("🤖 AI Response")
                    st.write(result.get("answer", "No answer generated"))
                    
                    # Display sources
                    if result.get("sources"):
                        st.subheader("📚 Sources")
                        for i, source in enumerate(result["sources"], 1):
                            st.write(f"{i}. **{source['source']}**")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": result.get("answer", ""),
                        "sources": result.get("sources", []),
                        "timestamp": time.strftime("%H:%M:%S")
                    })
                else:
                    st.error(f"❌ Query failed: {result['error']}")
        
        # Chat history
        if st.session_state.chat_history:
            st.subheader("💬 Chat History")
            
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:]), 1):  # Show last 5
                with st.expander(f"Q{i}: {chat['question'][:50]}... ({chat['timestamp']})"):
                    st.write(f"**Question:** {chat['question']}")
                    st.write(f"**Answer:** {chat['answer']}")
                    if chat['sources']:
                        st.write("**Sources:**")
                        for source in chat['sources']:
                            st.write(f"• {source['source']}")
            
            if st.button("🗑️ Clear History"):
                st.session_state.chat_history = []
                st.rerun()

if __name__ == "__main__":
    main() 