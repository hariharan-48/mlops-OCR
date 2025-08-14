#!/usr/bin/env python3
"""
Test script to verify environment variables for Streamlit app
"""
import os
import subprocess

def test_environment():
    print("🔍 Testing Streamlit Environment Variables")
    print("=" * 50)
    
    # Check required environment variables
    required_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "REGION", 
        "SUFFIX",
        "OCR_SERVICE_URL",
        "VISION_OCR_URL",
        "RAG_SERVICE_URL"
    ]
    
    print("📋 Environment Variables:")
    for var in required_vars:
        value = os.getenv(var, "")
        status = "✅" if value else "❌"
        print(f"  {status} {var}: {value}")
    
    print("\n🔧 Testing gcloud authentication:")
    try:
        # Test gcloud auth
        result = subprocess.run(["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print(f"  ✅ Authenticated as: {result.stdout.strip()}")
        else:
            print("  ❌ Not authenticated. Run: gcloud auth activate-service-account --key-file=.keys/ocr-sa-$SUFFIX.json")
    except Exception as e:
        print(f"  ❌ gcloud error: {e}")
    
    print("\n🌐 Testing service URLs:")
    try:
        # Test if services are accessible
        for service, url_var in [("OCR", "OCR_SERVICE_URL"), ("Vision OCR", "VISION_OCR_URL"), ("RAG", "RAG_SERVICE_URL")]:
            url = os.getenv(url_var, "")
            if url:
                print(f"  📍 {service}: {url}")
            else:
                print(f"  ❌ {service}: URL not set")
    except Exception as e:
        print(f"  ❌ Error testing URLs: {e}")
    
    print("\n💡 Next steps:")
    print("  1. If any variables are missing, run the setup commands again")
    print("  2. If not authenticated, run: gcloud auth activate-service-account --key-file=.keys/ocr-sa-$SUFFIX.json")
    print("  3. If services are not accessible, check if they're deployed and running")
    print("  4. Run: streamlit run app.py --server.port=8501 --server.address=0.0.0.0")

if __name__ == "__main__":
    test_environment() 