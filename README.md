# MLOps Workshop - OCR + RAG Pipeline

## 🎯 Overview
This workshop teaches participants how to build a complete MLOps pipeline for OCR (Optical Character Recognition) and RAG (Retrieval-Augmented Generation) using Google Cloud Platform.

## 🚀 Quick Start

### For Participants
1. Complete **[PREREQUISITES.md](PREREQUISITES.md)** for environment setup
2. Follow **[PARTICIPANT_GUIDE.md](PARTICIPANT_GUIDE.md)** for main workshop
3. Optional: Try **[PARTICIPANT_BONUS_GUIDE.md](PARTICIPANT_BONUS_GUIDE.md)** for advanced features

## 🏗️ What You'll Build

### Basic Workshop (PARTICIPANT_GUIDE.md)
- ✅ **OCR Service** - Extract text from images using Tesseract
- ✅ **CI/CD Pipeline** - Automated deployment with Cloud Build
- ✅ **Model Serving** - Deploy to Cloud Run
- ✅ **Data Versioning** - Cloud Storage with object versioning
- ✅ **Web Interface** - Streamlit frontend
- ✅ **Basic Monitoring** - Cloud Logging

### Advanced Features (PARTICIPANT_BONUS_GUIDE.md)
- 🧠 **Vertex AI Model Registry** - Production model versioning
- 📊 **Advanced Metrics** - Custom performance tracking
- 🔍 **Cloud Monitoring Dashboard** - Real-time visualization
- 🚨 **Alert Policies** - Automated error detection
- 🔧 **Cloud Vision API** - Professional OCR capabilities
- 🤖 **RAG Pipeline** - AI-powered document Q&A with Gemini 2.5 Flash

## 📁 Project Structure

```
Mlops-Trainig-OCR/
├── app/                          # Tesseract OCR service
├── rag-service/                  # RAG service with advanced features
├── ocr-cloud-vision/            # Cloud Vision OCR service
├── streamlit-frontend/          # Web interface
├── tests/                       # Unit tests
├── sample/                      # Sample images for testing
├── misc/                        # Organizer and auxiliary files
├── .keys/                       # Service account keys (created by organizer)
├── ORGANIZER_GUIDE.md           # Organizer setup guide
├── PARTICIPANT_GUIDE.md         # Main participant guide
├── PARTICIPANT_BONUS_GUIDE.md   # Advanced features guide
├── PREREQUISITES.md             # Pre-workshop setup
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Main service Dockerfile
└── .gitignore                   # Git ignore file
```

## 🎯 Learning Objectives

### MLOps Fundamentals
- **Containerization** - Docker images and deployment
- **CI/CD** - Automated build and deployment pipelines
- **Model Serving** - Production model deployment
- **Monitoring** - Application and model monitoring
- **Data Management** - Versioning and storage

### Advanced MLOps
- **Model Registry** - Production model versioning
- **Advanced Monitoring** - Custom metrics and dashboards
- **Alerting** - Automated error detection
- **AI Integration** - RAG with large language models
- **Professional OCR** - Cloud Vision API

## 🔗 Useful Links

- **Google Cloud Console**: https://console.cloud.google.com/
- **Cloud Run**: https://console.cloud.google.com/run
- **Cloud Build**: https://console.cloud.google.com/cloud-build
- **Vertex AI**: https://console.cloud.google.com/vertex-ai
- **Cloud Monitoring**: https://console.cloud.google.com/monitoring
