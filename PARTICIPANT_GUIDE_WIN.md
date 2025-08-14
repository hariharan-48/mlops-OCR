# MLOps Workshop - Participant Guide (Windows)

## 🎯 Overview
This guide will walk you through building a complete MLOps pipeline for OCR (Optical Character Recognition) and RAG (Retrieval-Augmented Generation) using Google Cloud Platform. You'll learn about containerization, CI/CD, model serving, and monitoring.

**🖥️ Windows-Specific Notes:**
- Use **Command Prompt** or **PowerShell** (recommended)
- Use **Git Bash** for Linux-like commands
- Use **Windows paths** with backslashes or forward slashes
- **Docker Desktop** must be running

## 📋 Prerequisites
Please complete the `PREREQUISITES.md` guide before starting this workshop.

**Windows Prerequisites:**
- ✅ Python 3.11 installed from python.org
- ✅ Git installed from git-scm.com
- ✅ Docker Desktop installed and running
- ✅ Google Cloud SDK installed from cloud.google.com
- ✅ Command Prompt or PowerShell ready

## 🚀 Step 1: Environment Setup

### 1.1 Set Your Team Variables
**What this does:** Sets up your unique team identifier and project details for all subsequent commands.

**Command Prompt:**
```cmd
REM Set your team identifier (organizer will provide this)
set SUFFIX=p1
set PROJECT_ID=mlops-rag
set REGION=us-central1

echo Team: %SUFFIX%
echo Project: %PROJECT_ID%
echo Region: %REGION%
```

**PowerShell:**
```powershell
# Set your team identifier (organizer will provide this)
$env:SUFFIX = "p1"
$env:PROJECT_ID = "mlops-rag"
$env:REGION = "us-central1"

Write-Host "Team: $env:SUFFIX"
Write-Host "Project: $env:PROJECT_ID"
Write-Host "Region: $env:REGION"
```

**Git Bash:**
```bash
# Set your team identifier (organizer will provide this)
export SUFFIX="p1"
export PROJECT_ID="mlops-rag"
export REGION="us-central1"

echo "Team: $SUFFIX"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
```

**Explanation:** These environment variables ensure all your resources (services, buckets, repositories) have unique names to avoid conflicts with other participants. Choose the shell you're most comfortable with.

### 1.2 Authenticate with Service Account
**What this does:** Authenticates your local environment with your team's service account, giving you access to GCP resources.

**Command Prompt:**
```cmd
REM Activate your team's service account
gcloud auth activate-service-account ocr-sa-%SUFFIX%@%PROJECT_ID%.iam.gserviceaccount.com --key-file=.keys\ocr-sa-%SUFFIX%.json

REM Verify authentication
gcloud auth list
```

**PowerShell:**
```powershell
# Activate your team's service account
gcloud auth activate-service-account ocr-sa-$env:SUFFIX@$env:PROJECT_ID.iam.gserviceaccount.com --key-file=".keys\ocr-sa-$env:SUFFIX.json"

# Verify authentication
gcloud auth list
```

**Git Bash:**
```bash
# Activate your team's service account
gcloud auth activate-service-account ocr-sa-$SUFFIX@$PROJECT_ID.iam.gserviceaccount.com \
  --key-file=.keys/ocr-sa-$SUFFIX.json

# Verify authentication
gcloud auth list
```

**Explanation:** The service account provides secure, limited access to GCP resources. The key file contains credentials that allow you to deploy and manage resources without needing full project access.

### 1.3 Configure Docker for Artifact Registry
**What this does:** Configures Docker to authenticate with Google's Artifact Registry, allowing you to push and pull Docker images.

```cmd
REM Configure Docker to authenticate with Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
```

**Explanation:** This command updates your Docker configuration to automatically authenticate with Google's Artifact Registry when pushing or pulling images.

## 🏗️ Step 2: Build and Deploy All Services

### 2.1 Create Artifact Registry Repository
**What this does:** Creates a private Docker image repository where your team's Docker images will be stored.

**Command Prompt:**
```cmd
REM Create repository for your team's Docker images
gcloud artifacts repositories create ocr-repo-%SUFFIX% --repository-format=docker --location=%REGION% --description="Docker repository for team %SUFFIX%"
```

**PowerShell:**
```powershell
# Create repository for your team's Docker images
gcloud artifacts repositories create ocr-repo-$env:SUFFIX --repository-format=docker --location=$env:REGION --description="Docker repository for team $env:SUFFIX"
```

**Git Bash:**
```bash
# Create repository for your team's Docker images
gcloud artifacts repositories create ocr-repo-$SUFFIX \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker repository for team $SUFFIX"
```

**Explanation:** Artifact Registry is Google's managed Docker registry. Each team gets their own repository to store Docker images securely.

### 2.2 Build and Deploy RAG Service
**What this does:** Creates and deploys the RAG (Retrieval-Augmented Generation) service that provides AI-powered document Q&A capabilities.

**Command Prompt:**
```cmd
REM Build RAG service
cd rag-service
docker build --platform=linux/amd64 -t rag-service-%SUFFIX% .

REM Tag for Artifact Registry
docker tag rag-service-%SUFFIX% us-central1-docker.pkg.dev/%PROJECT_ID%/ocr-repo-%SUFFIX%/rag-service-%SUFFIX%:v1

REM Push image
docker push us-central1-docker.pkg.dev/%PROJECT_ID%/ocr-repo-%SUFFIX%/rag-service-%SUFFIX%:v1

REM Deploy to Cloud Run
gcloud run deploy rag-service-%SUFFIX% --image=us-central1-docker.pkg.dev/%PROJECT_ID%/ocr-repo-%SUFFIX%/rag-service-%SUFFIX%:v1 --platform=managed --region=%REGION% --allow-unauthenticated --port=8080 --memory=2Gi --cpu=2 --max-instances=10 --service-account=ocr-sa-%SUFFIX%@%PROJECT_ID%.iam.gserviceaccount.com --set-env-vars=GOOGLE_CLOUD_PROJECT=%PROJECT_ID%,REGION=%REGION%,SUFFIX=%SUFFIX%

cd ..
```

**PowerShell:**
```powershell
# Build RAG service
cd rag-service
docker build --platform=linux/amd64 -t rag-service-$env:SUFFIX .

# Tag for Artifact Registry
docker tag rag-service-$env:SUFFIX us-central1-docker.pkg.dev/$env:PROJECT_ID/ocr-repo-$env:SUFFIX/rag-service-$env:SUFFIX:v1

# Push image
docker push us-central1-docker.pkg.dev/$env:PROJECT_ID/ocr-repo-$env:SUFFIX/rag-service-$env:SUFFIX:v1

# Deploy to Cloud Run
gcloud run deploy rag-service-$env:SUFFIX --image=us-central1-docker.pkg.dev/$env:PROJECT_ID/ocr-repo-$env:SUFFIX/rag-service-$env:SUFFIX:v1 --platform=managed --region=$env:REGION --allow-unauthenticated --port=8080 --memory=2Gi --cpu=2 --max-instances=10 --service-account=ocr-sa-$env:SUFFIX@$env:PROJECT_ID.iam.gserviceaccount.com --set-env-vars=GOOGLE_CLOUD_PROJECT=$env:PROJECT_ID,REGION=$env:REGION,SUFFIX=$env:SUFFIX

cd ..
```

**Git Bash:**
```bash
# Build RAG service
cd rag-service
docker build --platform=linux/amd64 -t rag-service-$SUFFIX .

# Tag for Artifact Registry
docker tag rag-service-$SUFFIX us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/rag-service-$SUFFIX:v1

# Push image
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/rag-service-$SUFFIX:v1

# Deploy to Cloud Run
gcloud run deploy rag-service-$SUFFIX \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/rag-service-$SUFFIX:v1 \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --port=8080 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=10 \
  --service-account=ocr-sa-$SUFFIX@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars=GOOGLE_CLOUD_PROJECT=$PROJECT_ID,REGION=$REGION,SUFFIX=$SUFFIX

cd ..
```

**Test the deployment:**
```cmd
REM Get RAG service URL and test
for /f "tokens=*" %i in ('gcloud run services describe rag-service-%SUFFIX% --region=%REGION% --format="value(status.url)"') do set RAG_URL=%i
curl %RAG_URL%/health
```

**Explanation:** The RAG service combines document storage with AI language models to answer questions about your documents. It needs more resources (`--memory=2Gi --cpu=2`) because it runs AI models. The `--service-account` parameter ensures the service uses your team's service account with the proper permissions.

### 2.3 Build and Deploy Tesseract OCR Service
**What this does:** Creates and deploys the Tesseract OCR service that extracts text from images using open-source OCR technology.

**Command Prompt:**
```cmd
REM Build Tesseract OCR service
cd app
docker build --platform=linux/amd64 -t ocr-service-%SUFFIX% .

REM Tag for Artifact Registry
docker tag ocr-service-%SUFFIX% us-central1-docker.pkg.dev/%PROJECT_ID%/ocr-repo-%SUFFIX%/ocr-service-%SUFFIX%:v1

REM Push image
docker push us-central1-docker.pkg.dev/%PROJECT_ID%/ocr-repo-%SUFFIX%/ocr-service-%SUFFIX%:v1

REM Get RAG service URL first
for /f "tokens=*" %i in ('gcloud run services describe rag-service-%SUFFIX% --region=%REGION% --format="value(status.url)"') do set RAG_URL=%i

REM Deploy to Cloud Run
gcloud run deploy ocr-service-%SUFFIX% --image=us-central1-docker.pkg.dev/%PROJECT_ID%/ocr-repo-%SUFFIX%/ocr-service-%SUFFIX%:v1 --platform=managed --region=%REGION% --allow-unauthenticated --port=8080 --memory=1Gi --cpu=1 --max-instances=10 --service-account=ocr-sa-%SUFFIX%@%PROJECT_ID%.iam.gserviceaccount.com --set-env-vars=RAG_SERVICE_URL=%RAG_URL%

cd ..
```

**PowerShell:**
```powershell
# Build Tesseract OCR service
cd app
docker build --platform=linux/amd64 -t ocr-service-$env:SUFFIX .

# Tag for Artifact Registry
docker tag ocr-service-$env:SUFFIX us-central1-docker.pkg.dev/$env:PROJECT_ID/ocr-repo-$env:SUFFIX/ocr-service-$env:SUFFIX:v1

# Push image
docker push us-central1-docker.pkg.dev/$env:PROJECT_ID/ocr-repo-$env:SUFFIX/ocr-service-$env:SUFFIX:v1

# Get RAG service URL first
$env:RAG_URL = gcloud run services describe rag-service-$env:SUFFIX --region=$env:REGION --format="value(status.url)"

# Deploy to Cloud Run
gcloud run deploy ocr-service-$env:SUFFIX --image=us-central1-docker.pkg.dev/$env:PROJECT_ID/ocr-repo-$env:SUFFIX/ocr-service-$env:SUFFIX:v1 --platform=managed --region=$env:REGION --allow-unauthenticated --port=8080 --memory=1Gi --cpu=1 --max-instances=10 --service-account=ocr-sa-$env:SUFFIX@$env:PROJECT_ID.iam.gserviceaccount.com --set-env-vars=RAG_SERVICE_URL=$env:RAG_URL

cd ..
```

**Git Bash:**
```bash
# Build Tesseract OCR service
cd app
docker build --platform=linux/amd64 -t ocr-service-$SUFFIX .

# Tag for Artifact Registry
docker tag ocr-service-$SUFFIX us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/ocr-service-$SUFFIX:v1

# Push image
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/ocr-service-$SUFFIX:v1

# Get RAG service URL first
RAG_URL=$(gcloud run services describe rag-service-$SUFFIX --region=$REGION --format='value(status.url)')

# Deploy to Cloud Run
gcloud run deploy ocr-service-$SUFFIX \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/ocr-service-$SUFFIX:v1 \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --port=8080 \
  --memory=1Gi \
  --cpu=1 \
  --max-instances=10 \
  --service-account=ocr-sa-$SUFFIX@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars=RAG_SERVICE_URL=$RAG_URL

cd ..
```

**Explanation:** The Tesseract OCR service uses open-source OCR to extract text from images. It's lighter on resources than the RAG service. The `RAG_SERVICE_URL` environment variable connects it to the RAG service for document indexing.

### 2.4 Build and Deploy Cloud Vision OCR Service
**What this does:** Creates and deploys the Cloud Vision OCR service that uses Google's AI-powered OCR for higher accuracy.

**Command Prompt:**
```cmd
REM Build Cloud Vision OCR service
cd ocr-cloud-vision
docker build --platform=linux/amd64 -t vision-ocr-service-%SUFFIX% .

REM Tag for Artifact Registry
docker tag vision-ocr-service-%SUFFIX% us-central1-docker.pkg.dev/%PROJECT_ID%/ocr-repo-%SUFFIX%/vision-ocr-service-%SUFFIX%:v1

REM Push image
docker push us-central1-docker.pkg.dev/%PROJECT_ID%/ocr-repo-%SUFFIX%/vision-ocr-service-%SUFFIX%:v1

REM Deploy to Cloud Run
gcloud run deploy vision-ocr-service-%SUFFIX% --image=us-central1-docker.pkg.dev/%PROJECT_ID%/ocr-repo-%SUFFIX%/vision-ocr-service-%SUFFIX%:v1 --platform=managed --region=%REGION% --allow-unauthenticated --port=8080 --memory=1Gi --cpu=1 --max-instances=10 --service-account=ocr-sa-%SUFFIX%@%PROJECT_ID%.iam.gserviceaccount.com --set-env-vars=RAG_SERVICE_URL=%RAG_URL%

cd ..
```

**PowerShell:**
```powershell
# Build Cloud Vision OCR service
cd ocr-cloud-vision
docker build --platform=linux/amd64 -t vision-ocr-service-$env:SUFFIX .

# Tag for Artifact Registry
docker tag vision-ocr-service-$env:SUFFIX us-central1-docker.pkg.dev/$env:PROJECT_ID/ocr-repo-$env:SUFFIX/vision-ocr-service-$env:SUFFIX:v1

# Push image
docker push us-central1-docker.pkg.dev/$env:PROJECT_ID/ocr-repo-$env:SUFFIX/vision-ocr-service-$env:SUFFIX:v1

# Deploy to Cloud Run
gcloud run deploy vision-ocr-service-$env:SUFFIX --image=us-central1-docker.pkg.dev/$env:PROJECT_ID/ocr-repo-$env:SUFFIX/vision-ocr-service-$env:SUFFIX:v1 --platform=managed --region=$env:REGION --allow-unauthenticated --port=8080 --memory=1Gi --cpu=1 --max-instances=10 --service-account=ocr-sa-$env:SUFFIX@$env:PROJECT_ID.iam.gserviceaccount.com --set-env-vars=RAG_SERVICE_URL=$env:RAG_URL

cd ..
```

**Git Bash:**
```bash
# Build Cloud Vision OCR service
cd ocr-cloud-vision
docker build --platform=linux/amd64 -t vision-ocr-service-$SUFFIX .

# Tag for Artifact Registry
docker tag vision-ocr-service-$SUFFIX us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/vision-ocr-service-$SUFFIX:v1

# Push image
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/vision-ocr-service-$SUFFIX:v1

# Deploy to Cloud Run
gcloud run deploy vision-ocr-service-$SUFFIX \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/vision-ocr-service-$SUFFIX:v1 \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --port=8080 \
  --memory=1Gi \
  --cpu=1 \
  --max-instances=10 \
  --service-account=ocr-sa-$SUFFIX@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars=RAG_SERVICE_URL=$RAG_URL

cd ..
```

**Explanation:** The Cloud Vision OCR service uses Google's AI-powered OCR for higher accuracy than Tesseract. It requires the same permissions and connects to the RAG service for document indexing.

## 🧪 Step 3: Test Your Services

### 3.1 Test All Services
**What this does:** Verifies that all your services are running and responding correctly.

**Command Prompt:**
```cmd
REM Test RAG service
for /f "tokens=*" %i in ('gcloud run services describe rag-service-%SUFFIX% --region=%REGION% --format="value(status.url)"') do set RAG_URL=%i
echo RAG Service: %RAG_URL%
curl %RAG_URL%/health

REM Test Tesseract OCR service
for /f "tokens=*" %i in ('gcloud run services describe ocr-service-%SUFFIX% --region=%REGION% --format="value(status.url)"') do set OCR_URL=%i
echo Tesseract OCR Service: %OCR_URL%
curl %OCR_URL%/health

REM Test Cloud Vision OCR service
for /f "tokens=*" %i in ('gcloud run services describe vision-ocr-service-%SUFFIX% --region=%REGION% --format="value(status.url)"') do set VISION_URL=%i
echo Cloud Vision OCR Service: %VISION_URL%
curl %VISION_URL%/health
```

**PowerShell:**
```powershell
# Test RAG service
$env:RAG_URL = gcloud run services describe rag-service-$env:SUFFIX --region=$env:REGION --format="value(status.url)"
Write-Host "RAG Service: $env:RAG_URL"
curl $env:RAG_URL/health

# Test Tesseract OCR service
$env:OCR_URL = gcloud run services describe ocr-service-$env:SUFFIX --region=$env:REGION --format="value(status.url)"
Write-Host "Tesseract OCR Service: $env:OCR_URL"
curl $env:OCR_URL/health

# Test Cloud Vision OCR service
$env:VISION_URL = gcloud run services describe vision-ocr-service-$env:SUFFIX --region=$env:REGION --format="value(status.url)"
Write-Host "Cloud Vision OCR Service: $env:VISION_URL"
curl $env:VISION_URL/health
```

**Git Bash:**
```bash
# Test RAG service
RAG_URL=$(gcloud run services describe rag-service-$SUFFIX --region=$REGION --format='value(status.url)')
echo "RAG Service: $RAG_URL"
curl $RAG_URL/health

# Test Tesseract OCR service
OCR_URL=$(gcloud run services describe ocr-service-$SUFFIX --region=$REGION --format='value(status.url)')
echo "Tesseract OCR Service: $OCR_URL"
curl $OCR_URL/health

# Test Cloud Vision OCR service
VISION_URL=$(gcloud run services describe vision-ocr-service-$SUFFIX --region=$REGION --format='value(status.url)')
echo "Cloud Vision OCR Service: $VISION_URL"
curl $VISION_URL/health
```

### 3.2 Test OCR + RAG Pipeline
**What this does:** Tests the complete pipeline by uploading an image, extracting text, and asking questions about it.

**Command Prompt:**
```cmd
REM Test Tesseract OCR + RAG
curl -X POST "%OCR_URL%/ocr-and-index" -F "file=@sample\Sample-handwritten-text-input-for-OCR.png" -F "enable_rag=true"

REM Test Cloud Vision OCR + RAG
curl -X POST "%VISION_URL%/ocr-and-index" -F "file=@sample\Sample-handwritten-text-input-for-OCR.png" -F "enable_rag=true"

REM Ask a question about the document
curl -X POST "%RAG_URL%/query" -H "Content-Type: application/json" -d "{\"query\": \"What is this document about?\", \"top_k\": 3}"
```

**PowerShell:**
```powershell
# Test Tesseract OCR + RAG
curl -X POST "$env:OCR_URL/ocr-and-index" -F "file=@sample\Sample-handwritten-text-input-for-OCR.png" -F "enable_rag=true"

# Test Cloud Vision OCR + RAG
curl -X POST "$env:VISION_URL/ocr-and-index" -F "file=@sample\Sample-handwritten-text-input-for-OCR.png" -F "enable_rag=true"

# Ask a question about the document
curl -X POST "$env:RAG_URL/query" -H "Content-Type: application/json" -d '{"query": "What is this document about?", "top_k": 3}'
```

**Git Bash:**
```bash
# Test Tesseract OCR + RAG
curl -X POST "$OCR_URL/ocr-and-index" \
  -F "file=@sample/Sample-handwritten-text-input-for-OCR.png" \
  -F "enable_rag=true"

# Test Cloud Vision OCR + RAG
curl -X POST "$VISION_URL/ocr-and-index" \
  -F "file=@sample/Sample-handwritten-text-input-for-OCR.png" \
  -F "enable_rag=true"

# Ask a question about the document
curl -X POST "$RAG_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?", "top_k": 3}'
```

## 🌐 Step 4: Deploy Streamlit Frontend

### 4.1 Option A: Run Streamlit Locally (Recommended)
**What this does:** Runs the Streamlit web interface locally on your Windows machine for easy testing and development.

**Command Prompt:**
```cmd
REM Create virtual environment for Streamlit
cd streamlit-frontend
python -m venv .streamlit

REM Activate virtual environment
.streamlit\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Set environment variables
set OCR_SERVICE_URL=%OCR_URL%
set VISION_OCR_URL=%VISION_URL%
set RAG_SERVICE_URL=%RAG_URL%
set GOOGLE_CLOUD_PROJECT=%PROJECT_ID%
set REGION=%REGION%
set SUFFIX=%SUFFIX%

REM Run Streamlit
streamlit run app.py
```

**PowerShell:**
```powershell
# Create virtual environment for Streamlit
cd streamlit-frontend
python -m venv .streamlit

# Activate virtual environment
.\.streamlit\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set environment variables
$env:OCR_SERVICE_URL = $env:OCR_URL
$env:VISION_OCR_URL = $env:VISION_URL
$env:RAG_SERVICE_URL = $env:RAG_URL
$env:GOOGLE_CLOUD_PROJECT = $env:PROJECT_ID
$env:REGION = $env:REGION
$env:SUFFIX = $env:SUFFIX

# Run Streamlit
streamlit run app.py
```

**Git Bash:**
```bash
# Create virtual environment for Streamlit
cd streamlit-frontend
python3 -m venv .streamlit

# Activate virtual environment
source .streamlit/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OCR_SERVICE_URL=$OCR_URL
export VISION_OCR_URL=$VISION_URL
export RAG_SERVICE_URL=$RAG_URL
export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
export REGION=$REGION
export SUFFIX=$SUFFIX

# Run Streamlit
streamlit run app.py
```

**Explanation:** This creates a local web interface that connects to your deployed services. Streamlit will open in your browser at `http://localhost:8501`. This is the easiest way to test the complete system.

### 4.2 Option B: Deploy Streamlit to Cloud Run
**What this does:** Deploys the Streamlit frontend to Cloud Run for a web-accessible interface.

**Command Prompt:**
```cmd
REM Build Streamlit service
cd streamlit-frontend
docker build --platform=linux/amd64 -t streamlit-frontend-%SUFFIX% .

REM Tag for Artifact Registry
docker tag streamlit-frontend-%SUFFIX% us-central1-docker.pkg.dev/%PROJECT_ID%/ocr-repo-%SUFFIX%/streamlit-frontend-%SUFFIX%:v1

REM Push image
docker push us-central1-docker.pkg.dev/%PROJECT_ID%/ocr-repo-%SUFFIX%/streamlit-frontend-%SUFFIX%:v1

REM Deploy to Cloud Run
gcloud run deploy streamlit-frontend-%SUFFIX% --image=us-central1-docker.pkg.dev/%PROJECT_ID%/ocr-repo-%SUFFIX%/streamlit-frontend-%SUFFIX%:v1 --platform=managed --region=%REGION% --allow-unauthenticated --port=8501 --memory=1Gi --cpu=1 --max-instances=10 --service-account=ocr-sa-%SUFFIX%@%PROJECT_ID%.iam.gserviceaccount.com --set-env-vars=OCR_SERVICE_URL=%OCR_URL%,VISION_OCR_URL=%VISION_URL%,RAG_SERVICE_URL=%RAG_URL%,GOOGLE_CLOUD_PROJECT=%PROJECT_ID%,REGION=%REGION%,SUFFIX=%SUFFIX%

cd ..
```

**PowerShell:**
```powershell
# Build Streamlit service
cd streamlit-frontend
docker build --platform=linux/amd64 -t streamlit-frontend-$env:SUFFIX .

# Tag for Artifact Registry
docker tag streamlit-frontend-$env:SUFFIX us-central1-docker.pkg.dev/$env:PROJECT_ID/ocr-repo-$env:SUFFIX/streamlit-frontend-$env:SUFFIX:v1

# Push image
docker push us-central1-docker.pkg.dev/$env:PROJECT_ID/ocr-repo-$env:SUFFIX/streamlit-frontend-$env:SUFFIX:v1

# Deploy to Cloud Run
gcloud run deploy streamlit-frontend-$env:SUFFIX --image=us-central1-docker.pkg.dev/$env:PROJECT_ID/ocr-repo-$env:SUFFIX/streamlit-frontend-$env:SUFFIX:v1 --platform=managed --region=$env:REGION --allow-unauthenticated --port=8501 --memory=1Gi --cpu=1 --max-instances=10 --service-account=ocr-sa-$env:SUFFIX@$env:PROJECT_ID.iam.gserviceaccount.com --set-env-vars=OCR_SERVICE_URL=$env:OCR_URL,VISION_OCR_URL=$env:VISION_URL,RAG_SERVICE_URL=$env:RAG_URL,GOOGLE_CLOUD_PROJECT=$env:PROJECT_ID,REGION=$env:REGION,SUFFIX=$env:SUFFIX

cd ..
```

**Git Bash:**
```bash
# Build Streamlit service
cd streamlit-frontend
docker build --platform=linux/amd64 -t streamlit-frontend-$SUFFIX .

# Tag for Artifact Registry
docker tag streamlit-frontend-$SUFFIX us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/streamlit-frontend-$SUFFIX:v1

# Push image
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/streamlit-frontend-$SUFFIX:v1

# Deploy to Cloud Run
gcloud run deploy streamlit-frontend-$SUFFIX \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/streamlit-frontend-$SUFFIX:v1 \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --port=8501 \
  --memory=1Gi \
  --cpu=1 \
  --max-instances=10 \
  --service-account=ocr-sa-$SUFFIX@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars=OCR_SERVICE_URL=$OCR_URL,VISION_OCR_URL=$VISION_URL,RAG_SERVICE_URL=$RAG_URL,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,REGION=$REGION,SUFFIX=$SUFFIX

cd ..
```

### 4.3 Test Streamlit Frontend
**What this does:** Verifies that the Streamlit frontend is working and can connect to your services.

**Command Prompt:**
```cmd
REM Get Streamlit URL (if deployed to Cloud Run)
for /f "tokens=*" %i in ('gcloud run services describe streamlit-frontend-%SUFFIX% --region=%REGION% --format="value(status.url)"') do set STREAMLIT_URL=%i

REM Open in browser
start %STREAMLIT_URL%
```

**PowerShell:**
```powershell
# Get Streamlit URL (if deployed to Cloud Run)
$env:STREAMLIT_URL = gcloud run services describe streamlit-frontend-$env:SUFFIX --region=$env:REGION --format="value(status.url)"

# Open in browser
Start-Process $env:STREAMLIT_URL
```

**Git Bash:**
```bash
# Get Streamlit URL (if deployed to Cloud Run)
STREAMLIT_URL=$(gcloud run services describe streamlit-frontend-$SUFFIX --region=$REGION --format='value(status.url)')

# Open in browser
start $STREAMLIT_URL
```

**Manual Testing:**
1. **Local Streamlit**: Open `http://localhost:8501` in your browser
2. **Cloud Run Streamlit**: Open the URL provided by the deployment
3. **Upload an image** from the `sample/` directory
4. **Process the document** and verify text extraction
5. **Ask questions** about the document using the RAG interface

## 🎉 Congratulations!

You've successfully built a complete MLOps pipeline with:

### ✅ **Services Deployed:**
- **RAG Service** - AI-powered document Q&A
- **Tesseract OCR Service** - Open-source text extraction
- **Cloud Vision OCR Service** - Google AI text extraction
- **Streamlit Frontend** - Web interface (local or Cloud Run)

### 🔗 **Console Links:**
- **Cloud Run**: https://console.cloud.google.com/run?project=$PROJECT_ID
- **Artifact Registry**: https://console.cloud.google.com/artifacts?project=$PROJECT_ID
- **Cloud Storage**: https://console.cloud.google.com/storage/browser?project=$PROJECT_ID

### 🎯 **What You've Learned:**
1. **Containerization** - Docker images and deployment
2. **Cloud Services** - Cloud Run, Artifact Registry, Cloud Storage
3. **Service Integration** - Connecting multiple services
4. **API Development** - RESTful APIs with FastAPI
5. **Web Frontend** - Streamlit for user interface
6. **MLOps Pipeline** - End-to-end document processing

## 🧹 Cleanup (Optional)

### Clean Up Resources
**What this does:** Removes all resources created during the workshop to avoid ongoing charges.

**Command Prompt:**
```cmd
REM Delete Cloud Run services
gcloud run services delete rag-service-%SUFFIX% --region=%REGION% --quiet
gcloud run services delete ocr-service-%SUFFIX% --region=%REGION% --quiet
gcloud run services delete vision-ocr-service-%SUFFIX% --region=%REGION% --quiet
gcloud run services delete streamlit-frontend-%SUFFIX% --region=%REGION% --quiet

REM Delete Artifact Registry repository
gcloud artifacts repositories delete ocr-repo-%SUFFIX% --location=%REGION% --quiet

REM Delete service account
gcloud iam service-accounts delete ocr-sa-%SUFFIX%@%PROJECT_ID%.iam.gserviceaccount.com --quiet

REM Clean up local virtual environment
if exist streamlit-frontend\.streamlit rmdir /s /q streamlit-frontend\.streamlit
```

**PowerShell:**
```powershell
# Delete Cloud Run services
gcloud run services delete rag-service-$env:SUFFIX --region=$env:REGION --quiet
gcloud run services delete ocr-service-$env:SUFFIX --region=$env:REGION --quiet
gcloud run services delete vision-ocr-service-$env:SUFFIX --region=$env:REGION --quiet
gcloud run services delete streamlit-frontend-$env:SUFFIX --region=$env:REGION --quiet

# Delete Artifact Registry repository
gcloud artifacts repositories delete ocr-repo-$env:SUFFIX --location=$env:REGION --quiet

# Delete service account
gcloud iam service-accounts delete ocr-sa-$env:SUFFIX@$env:PROJECT_ID.iam.gserviceaccount.com --quiet

# Clean up local virtual environment
if (Test-Path "streamlit-frontend\.streamlit") { Remove-Item -Recurse -Force "streamlit-frontend\.streamlit" }
```

**Git Bash:**
```bash
# Delete Cloud Run services
gcloud run services delete rag-service-$SUFFIX --region=$REGION --quiet
gcloud run services delete ocr-service-$SUFFIX --region=$REGION --quiet
gcloud run services delete vision-ocr-service-$SUFFIX --region=$REGION --quiet
gcloud run services delete streamlit-frontend-$SUFFIX --region=$REGION --quiet

# Delete Artifact Registry repository
gcloud artifacts repositories delete ocr-repo-$SUFFIX --location=$REGION --quiet

# Delete service account
gcloud iam service-accounts delete ocr-sa-$SUFFIX@$PROJECT_ID.iam.gserviceaccount.com --quiet

# Clean up local virtual environment
if [ -d "streamlit-frontend/.streamlit" ]; then
  rm -rf streamlit-frontend/.streamlit
fi
```

## 🚨 Windows-Specific Troubleshooting

### **Docker Desktop Issues**
```cmd
REM If Docker Desktop won't start
REM 1. Check Windows Features - enable WSL2
REM 2. Run: wsl --install
REM 3. Restart computer
REM 4. Start Docker Desktop again
```

### **Python Virtual Environment Issues**
```cmd
REM If virtual environment activation fails
REM Try running Command Prompt as Administrator
REM Or use PowerShell with:
.\.streamlit\Scripts\Activate.ps1
```

### **Path Issues**
```cmd
REM If commands not found, check PATH
echo %PATH%

REM Add Python to PATH if needed
REM Usually: C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\
REM And: C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts\
```

### **Permission Issues**
```powershell
# If you get execution policy errors in PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Git Bash Alternative**
If Command Prompt or PowerShell give you trouble:
1. **Install Git Bash** with Git installation
2. **Use Git Bash** for all commands
3. **Commands work the same** as Linux/macOS

---

**🎉 You've successfully built a production-ready MLOps pipeline on Windows! 🚀** 