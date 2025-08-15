# MLOps Workshop - Participant Guide

## 🎯 Overview
This guide will walk you through building a complete MLOps pipeline for OCR (Optical Character Recognition) and RAG (Retrieval-Augmented Generation) using Google Cloud Platform. You'll learn about containerization, CI/CD, model serving, and monitoring.

## 📋 Prerequisites
Please complete the `PREREQUISITES.md` guide before starting this workshop.

### **2. Get Repository Access**
```bash
# Clone the workshop repository (you'll get the URL from the organizer)
git clone <WORKSHOP_REPOSITORY_URL>
cd Mlops-Trainig-OCR

# Verify you have the workshop files
ls -la
# You should see: PARTICIPANT_GUIDE.md, PREREQUISITES.md, app/, rag-service/, etc.
```

### **3. Download Workshop Materials**
- Download your service account key file (`.keys/ocr-sa-<yourname>.json`) from the organizer
- Place it in the `.keys/` directory (create if it doesn't exist)
- Verify sample images are in the `sample/` directory

## 🚀 Step 1: Environment Setup

### 1.1 Set Your Team Variables
**What this does:** Sets up your unique team identifier and project details for all subsequent commands.

```bash
# Set your team identifier (organizer will provide this)
export SUFFIX="p1"  # Change to your team: team1, team2, team3, team4
export PROJECT_ID="mlops-rag"  # Organizer will provide
export REGION="us-central1"

echo "Team: $SUFFIX"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
```

**Explanation:** These environment variables ensure all your resources (services, buckets, repositories) have unique names to avoid conflicts with other participants.

### 1.2 Authenticate with Service Account
**What this does:** Authenticates your local environment with your team's service account, giving you access to GCP resources.

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

```bash
# Configure Docker to authenticate with Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
```

**Explanation:** This command updates your Docker configuration to automatically authenticate with Google's Artifact Registry when pushing or pulling images.

## 🏗️ Step 2: Build and Deploy All Services

### 2.1 Create Artifact Registry Repository
**What this does:** Creates a private Docker image repository where your team's Docker images will be stored.

```bash
# Config project
gcloud config set project $PROJECT_ID

# Create repository for your team's Docker images
gcloud artifacts repositories create ocr-repo-$SUFFIX \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker repository for team $SUFFIX"
```

**Explanation:** Artifact Registry is Google's managed Docker registry. Each team gets their own repository to store Docker images securely.

### 2.2 Build and Deploy RAG Service
**What this does:** Creates and deploys the RAG (Retrieval-Augmented Generation) service that provides AI-powered document Q&A capabilities.

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

``` bash
RAG_URL=$(gcloud run services describe rag-service-$SUFFIX --region=$REGION --format='value(status.url)')
curl $RAG_URL/health
```

**Explanation:** The RAG service combines document storage with AI language models to answer questions about your documents. It needs more resources (`--memory=2Gi --cpu=2`) because it runs AI models. The `--service-account` parameter ensures the service uses your team's service account with the proper permissions.

### 2.3 Build and Deploy Tesseract OCR Service
**What this does:** Creates and deploys the Tesseract OCR service for free, local text extraction from images.

```bash
# Build Tesseract OCR service
docker build --platform=linux/amd64 -t ocr-service-$SUFFIX .

# Tag for Artifact Registry
docker tag ocr-service-$SUFFIX us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/ocr-service-$SUFFIX:v1

# Push image
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/ocr-service-$SUFFIX:v1

# Get RAG service URL for integration
RAG_URL=$(gcloud run services describe rag-service-$SUFFIX --region=$REGION --format='value(status.url)')

# Deploy to Cloud Run with RAG integration
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
```
``` bash
OCR_URL=$(gcloud run services describe ocr-service-$SUFFIX --region=$REGION --format='value(status.url)')
curl $OCR_URL/health

curl -X POST  -F "file=@$PWD/sample/Sample-handwritten-text-input-for-OCR.png" "$OCR_URL/ocr"  
```

**Explanation:** Tesseract OCR provides free text extraction from images. It's integrated with the RAG service so extracted text can be automatically indexed for AI-powered Q&A. The `--service-account` parameter ensures consistent permissions across all services.

### 2.4 Build and Deploy Cloud Vision OCR Service
**What this does:** Creates and deploys the Cloud Vision OCR service for high-accuracy, professional text extraction.

```bash
# Build Cloud Vision OCR service
cd ocr-cloud-vision
docker build --platform=linux/amd64 -t vision-ocr-service-$SUFFIX .

# Tag for Artifact Registry
docker tag vision-ocr-service-$SUFFIX us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/vision-ocr-service-$SUFFIX:v1

# Push image
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ocr-repo-$SUFFIX/vision-ocr-service-$SUFFIX:v1

# Deploy to Cloud Run with RAG integration
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
``` bash
VISION_URL=$(gcloud run services describe vision-ocr-service-$SUFFIX --region=$REGION --format='value(status.url)')
curl $VISION_URL/health

curl -X POST  -F "file=@$PWD/sample/Sample-handwritten-text-input-for-OCR.png" "$VISION_URL/ocr"  
```

**Explanation:** Cloud Vision API provides much higher accuracy for OCR, especially for handwritten text, making it suitable for production use cases. It's also integrated with the RAG service. The `--service-account` parameter ensures consistent permissions across all services.

## 🧪 Step 3: Test All Services

### 3.1 Get Service URLs
**What this does:** Retrieves the public URLs where all your services are accessible.

```bash
# Get all service URLs
RAG_URL=$(gcloud run services describe rag-service-$SUFFIX --region=$REGION --format='value(status.url)')
OCR_URL=$(gcloud run services describe ocr-service-$SUFFIX --region=$REGION --format='value(status.url)')
VISION_URL=$(gcloud run services describe vision-ocr-service-$SUFFIX --region=$REGION --format='value(status.url)')

echo "RAG Service URL: $RAG_URL"
echo "Tesseract OCR Service URL: $OCR_URL"
echo "Cloud Vision OCR Service URL: $VISION_URL"
```

**Explanation:** Cloud Run generates unique URLs for each service. These commands extract those URLs for testing.

### 3.2 Test Health Endpoints
**What this does:** Verifies that all your services are running and responding to requests.

```bash
# Test if all services are healthy
echo "Testing RAG service health..."
curl $RAG_URL/health

echo "Testing Tesseract OCR service health..."
curl $OCR_URL/health

echo "Testing Cloud Vision OCR service health..."
curl $VISION_URL/health
```

**Explanation:** The `/health` endpoint is a standard way to check if a service is operational. Successful responses mean your services are ready to process requests.

### 3.3 Test OCR Services with Sample Image
**What this does:** Tests the actual OCR functionality by uploading an image and extracting text from both OCR services.

```bash
# Test OCR with a sample image (if available)
if [ -f "Sample-handwritten-text-input-for-OCR.png" ]; then
  echo "Testing Tesseract OCR..."
  curl -X POST "$OCR_URL/ocr" \
    -F "file=@$PWD/sample/Sample-handwritten-text-input-for-OCR.png" \
    -F "lang=en" | jq '.'
  
  echo "Testing Cloud Vision OCR..."
  curl -X POST "$VISION_URL/ocr" \
    -F "file=@$PWD/sample/Sample-handwritten-text-input-for-OCR.png" \
    -F "lang=en" | jq '.'
else
  echo "Sample image not found. You can test with any image file."
fi
```

**Explanation:** This sends an image file to both OCR services and returns the extracted text. The `-F` flag creates a form upload, which is how the services expect to receive image files.

### 3.4 Test Complete OCR + RAG Pipeline
**What this does:** Tests the complete pipeline where OCR-extracted text is automatically indexed and can be queried with AI.

```bash
# Test complete pipeline with Tesseract OCR
echo "Testing Tesseract OCR + RAG pipeline..."
curl -X POST "$OCR_URL/ocr-and-index" \
  -F "file=@$PWD/sample/Sample-handwritten-text-input-for-OCR.png" \
  -F "enable_rag=true" | jq '.'

# Test complete pipeline with Cloud Vision OCR
echo "Testing Cloud Vision OCR + RAG pipeline..."
curl -X POST "$VISION_URL/ocr-and-index" \
  -F "file=@$PWD/sample/Sample-handwritten-text-input-for-OCR.png" \
  -F "enable_rag=true" | jq '.'

# Test RAG query
echo "Testing RAG query..."
curl -X POST "$RAG_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?", "top_k": 3}' | jq '.'
```

**Explanation:** This tests the complete workflow:
1. OCR service extracts text from image
2. Text is automatically sent to RAG service for indexing
3. RAG service can answer questions about the indexed content

## 🔄 Step 4: Set Up CI/CD Pipeline

### 4.1 Create Cloud Build Configuration
**What this does:** Creates a configuration file that defines how to automatically build and deploy all your services when code changes.

```bash
# First, get your RAG service URL to hardcode it
RAG_URL=$(gcloud run services describe rag-service-$SUFFIX --region=$REGION --format='value(status.url)')
echo "Your RAG service URL: $RAG_URL"
replace the rag_service_url with above i the below cloud build file

# Create cloudbuild.yaml for automated deployment
cat > cloudbuild.yaml << EOF
steps:
  # Build RAG service
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '--platform=linux/amd64', '-t', 'us-central1-docker.pkg.dev/\$PROJECT_ID/ocr-repo-$SUFFIX/rag-service-$SUFFIX:v\$SHORT_SHA', './rag-service']
  
  # Build Tesseract OCR service
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '--platform=linux/amd64', '-t', 'us-central1-docker.pkg.dev/\$PROJECT_ID/ocr-repo-$SUFFIX/ocr-service-$SUFFIX:v\$SHORT_SHA', '.']
  
  # Build Cloud Vision OCR service
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '--platform=linux/amd64', '-t', 'us-central1-docker.pkg.dev/\$PROJECT_ID/ocr-repo-$SUFFIX/vision-ocr-service-$SUFFIX:v\$SHORT_SHA', './ocr-cloud-vision']
  
  # Push all images
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/\$PROJECT_ID/ocr-repo-$SUFFIX/rag-service-$SUFFIX:v\$SHORT_SHA']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/\$PROJECT_ID/ocr-repo-$SUFFIX/ocr-service-$SUFFIX:v\$SHORT_SHA']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/\$PROJECT_ID/ocr-repo-$SUFFIX/vision-ocr-service-$SUFFIX:v\$SHORT_SHA']
  
  # Deploy RAG service first
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'rag-service-$SUFFIX'
      - '--image=us-central1-docker.pkg.dev/\$PROJECT_ID/ocr-repo-$SUFFIX/rag-service-$SUFFIX:v\$SHORT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--port=8080'
      - '--memory=2Gi'
      - '--cpu=2'
      - '--max-instances=10'
      - '--service-account=ocr-sa-$SUFFIX@$PROJECT_ID.iam.gserviceaccount.com'
      - '--set-env-vars=GOOGLE_CLOUD_PROJECT=\$PROJECT_ID,REGION=us-central1,SUFFIX=$SUFFIX'
  
  # Deploy OCR services with hardcoded RAG URL
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'ocr-service-$SUFFIX'
      - '--image=us-central1-docker.pkg.dev/\$PROJECT_ID/ocr-repo-$SUFFIX/ocr-service-$SUFFIX:v\$SHORT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--port=8080'
      - '--memory=1Gi'
      - '--cpu=1'
      - '--max-instances=10'
      - '--service-account=ocr-sa-$SUFFIX@$PROJECT_ID.iam.gserviceaccount.com'
      - '--set-env-vars=RAG_SERVICE_URL=https://rag-service-team1-f2melavagq-uc.a.run.app'
  
  # Deploy Cloud Vision OCR service
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'vision-ocr-service-$SUFFIX'
      - '--image=us-central1-docker.pkg.dev/\$PROJECT_ID/ocr-repo-$SUFFIX/vision-ocr-service-$SUFFIX:v\$SHORT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--port=8080'
      - '--memory=1Gi'
      - '--cpu=1'
      - '--max-instances=10'
      - '--service-account=ocr-sa-$SUFFIX@$PROJECT_ID.iam.gserviceaccount.com'
      - '--set-env-vars=RAG_SERVICE_URL=https://rag-service-team1-f2melavagq-uc.a.run.app'

images:
  - 'us-central1-docker.pkg.dev/\$PROJECT_ID/ocr-repo-$SUFFIX/rag-service-$SUFFIX:v\$SHORT_SHA'
  - 'us-central1-docker.pkg.dev/\$PROJECT_ID/ocr-repo-$SUFFIX/ocr-service-$SUFFIX:v\$SHORT_SHA'
  - 'us-central1-docker.pkg.dev/\$PROJECT_ID/ocr-repo-$SUFFIX/vision-ocr-service-$SUFFIX:v\$SHORT_SHA'
EOF
```

**Explanation:** This YAML file defines a CI/CD pipeline that:
1. **Builds** all three services (RAG, Tesseract OCR, Cloud Vision OCR)
2. **Pushes** all images to Artifact Registry
3. **Deploys** RAG service first
4. **Deploys** both OCR services with the actual RAG URL hardcoded

**Note:** The RAG service URL is fetched using `gcloud run services describe` and then hardcoded into the cloudbuild.yaml file. This ensures the correct URL is used and avoids any Cloud Build substitution issues.

### 4.2 Test Cloud Build Locally
**What this does:** Tests your CI/CD configuration by running the build process manually.

```bash
# Test the build configuration
gcloud builds submit --config=cloudbuild.yaml .
```

**Explanation:** This command triggers the build process defined in your `cloudbuild.yaml` file, testing that your CI/CD pipeline works correctly for all services. The RAG URL is already hardcoded in the file, so no substitutions are needed.

## 📊 Step 5: Data Ingestion and Versioning

### 5.1 Create Cloud Storage Bucket
**What this does:** Creates a storage bucket for your team's data files.

```bash
# Create bucket for your team's data
gsutil mb -l $REGION gs://mlops-workshop-$SUFFIX-$PROJECT_ID
```

**Explanation:** Cloud Storage buckets are like folders in the cloud where you can store files. Each team gets their own bucket to avoid conflicts.

### 5.2 Upload Sample Data
**What this does:** Uploads sample images to your storage bucket for testing and versioning.

```bash
# Upload sample images to your bucket

  gsutil cp $PWD/sample/Sample-handwritten-text-input-for-OCR.png gs://mlops-workshop-$SUFFIX-$PROJECT_ID/


# List uploaded files
gsutil ls gs://mlops-workshop-$SUFFIX-$PROJECT_ID/
```

**Explanation:** This uploads your sample images to the cloud storage bucket. The `gsutil ls` command shows you what files are stored in your bucket.

### 5.3 Enable Object Versioning
**What this does:** Enables versioning on your storage bucket, allowing you to track changes to your data files.

```bash
# Enable versioning for data tracking
gsutil versioning set on gs://mlops-workshop-$SUFFIX-$PROJECT_ID
```

**Explanation:** With versioning enabled, every time you upload a file with the same name, the old version is preserved. This is crucial for data lineage and reproducibility in MLOps.

## 🔍 Step 6: Basic Monitoring

### 6.1 Check Service Logs
**What this does:** Views recent logs from all your services to monitor their behavior and troubleshoot issues.

```bash
# Method 1: View logs through Cloud Console (Recommended)
echo "View logs in Cloud Console:"
echo "https://console.cloud.google.com/logs?project=$PROJECT_ID"

# Method 2: Try basic log viewing (may not work with service accounts)
echo "Attempting to view logs via CLI..."
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=rag-service-$SUFFIX" \
  --limit=5 \
  --format="value(timestamp,textPayload)" || echo "CLI log viewing not available - use Cloud Console instead"

# Method 3: Check service status and recent activity
echo "Checking service status and recent activity..."
gcloud run services describe rag-service-$SUFFIX --region=$REGION --format="value(status.conditions[0].status,status.conditions[0].message)"
gcloud run services describe ocr-service-$SUFFIX --region=$REGION --format="value(status.conditions[0].status,status.conditions[0].message)"
gcloud run services describe vision-ocr-service-$SUFFIX --region=$REGION --format="value(status.conditions[0].status,status.conditions[0].message)"
```

**Explanation:** Due to Cloud Logging permission restrictions with service accounts, the recommended approach is to view logs through the Cloud Console. The CLI method may not work, but you can still check service status and health.

### 6.2 Monitor Service Metrics
**What this does:** Checks the current status and health of all your deployed services.

```bash
# Check service status for all services
echo "RAG service status:"
gcloud run services describe rag-service-$SUFFIX --region=$REGION --format="value(status.conditions[0].status)"

echo "Tesseract OCR service status:"
gcloud run services describe ocr-service-$SUFFIX --region=$REGION --format="value(status.conditions[0].status)"

echo "Cloud Vision OCR service status:"
gcloud run services describe vision-ocr-service-$SUFFIX --region=$REGION --format="value(status.conditions[0].status)"
```

**Explanation:** This command shows whether your services are healthy and ready to handle requests.

## 🌐 Step 7: Deploy Streamlit Frontend

### Option A: Run Streamlit Locally (Recommended)
**What this does:** Runs the Streamlit app locally on your machine, which is simpler and faster for development and testing.

```bash
# Navigate to Streamlit frontend directory
cd ..
cd streamlit-frontend

# Create and activate virtual environment
python3 -m venv .streamlit
source .streamlit/bin/activate  # On Windows: .streamlit\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables for your services
export OCR_SERVICE_URL=$(gcloud run services describe ocr-service-$SUFFIX --region=$REGION --format='value(status.url)')
export VISION_OCR_URL=$(gcloud run services describe vision-ocr-service-$SUFFIX --region=$REGION --format='value(status.url)')
export RAG_SERVICE_URL=$(gcloud run services describe rag-service-$SUFFIX --region=$REGION --format='value(status.url)')

# Set additional environment variables for Streamlit app
export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
export REGION=$REGION
export SUFFIX=$SUFFIX

echo "OCR Service URL: $OCR_SERVICE_URL"
echo "Vision OCR Service URL: $VISION_OCR_URL"
echo "RAG Service URL: $RAG_SERVICE_URL"
echo "Note: Streamlit app uses Cloud Vision OCR service by default"

# Test environment setup
echo "Testing environment setup..."
python test_env.py

# Run Streamlit locally
streamlit run app.py --server.port=8501 --server.address=0.0.0.0

# To stop Streamlit: Press Ctrl+C
# To deactivate virtual environment: deactivate

cd ..
```

**Explanation:** This runs Streamlit locally on your machine at `http://localhost:8501`. The virtual environment (`.streamlit`) keeps the dependencies isolated from your system Python. It's much faster to start and debug, and you don't need to worry about Docker builds or Cloud Run deployments for the frontend.

**Troubleshooting:** If you see "RAG service URL not configured" error, make sure:
1. All environment variables are set correctly
2. Your services are running and accessible
3. You're authenticated with the correct service account: `gcloud auth activate-service-account --key-file=.keys/ocr-sa-$SUFFIX.json`

<!-- ### Option B: Deploy Streamlit to Cloud Run
**What this does:** Deploys the Streamlit app to Cloud Run for a web-accessible interface.

```bash
# Build Streamlit frontend
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
  --service-account=ocr-sa-$SUFFIX@$PROJECT_ID.iam.gserviceaccount.com

# Get the Streamlit URL
STREAMLIT_URL=$(gcloud run services describe streamlit-frontend-$SUFFIX --region=$REGION --format='value(status.url)')
echo "Streamlit URL: $STREAMLIT_URL"
echo "Open this URL in your browser to access the OCR + RAG application!"

cd ..
```

**Explanation:** This deploys your Streamlit application to Cloud Run, making it accessible via a web browser. The `--port=8501` is the default Streamlit port. The `--service-account` parameter ensures consistent permissions across all services. -->

<!-- ## 🎯 Step 8: Test Complete Pipeline

### 8.1 Test End-to-End Workflow
**What this does:** Tests all components of your MLOps pipeline to ensure everything works together.

```bash
# Test the complete pipeline
echo "Testing complete OCR + RAG pipeline..."

# 1. Test all services
echo "1. Testing all services..."
echo "   - RAG Service:"
curl -s "$RAG_URL/health" | jq '.'

echo "   - Tesseract OCR Service:"
curl -s "$OCR_URL/health" | jq '.'

echo "   - Cloud Vision OCR Service:"
curl -s "$VISION_URL/health" | jq '.'

# 2. Test Streamlit frontend
echo "2. Testing Streamlit frontend..."
if [ -n "$STREAMLIT_URL" ]; then
  echo "   - Cloud Run Streamlit:"
  curl -s "$STREAMLIT_URL" | head -5
else
  echo "   - Local Streamlit: Check http://localhost:8501 in your browser"
fi

# 3. Test data storage
echo "3. Testing data storage..."
gsutil ls gs://mlops-workshop-$SUFFIX-$PROJECT_ID/

echo "✅ Pipeline test completed!"
``` -->

**Explanation:** This comprehensive test verifies that:
1. All services are responding to requests
2. Your Streamlit frontend is accessible
3. Your data storage is working properly

### 8.2 Manual Testing
**What this does:** Provides instructions for manually testing your application through the web interface.

1. **Open Streamlit URL** in your browser:
   - **Local Streamlit**: Open `http://localhost:8501`
   - **Cloud Run Streamlit**: Open the URL from `$STREAMLIT_URL`
2. **Upload an image** with text
3. **Choose OCR service** (Tesseract or Cloud Vision)
4. **View OCR results** and extracted text
5. **Ask questions** about the document using RAG
6. **Compare results** between Tesseract and Cloud Vision

**Explanation:** Manual testing through the web interface helps you understand the user experience and verify that all services are working correctly with real images.

## 📈 Step 9: Monitor and Optimize

### 9.1 Check Service Performance
**What this does:** Monitors the performance and health of all your deployed services.

```bash
# Monitor service metrics for all services
echo "RAG service performance:"
gcloud run services describe rag-service-$SUFFIX --region=$REGION \
  --format="value(status.conditions[0].status,status.conditions[0].message)"

echo "Tesseract OCR service performance:"
gcloud run services describe ocr-service-$SUFFIX --region=$REGION \
  --format="value(status.conditions[0].status,status.conditions[0].message)"

echo "Cloud Vision OCR service performance:"
gcloud run services describe vision-ocr-service-$SUFFIX --region=$REGION \
  --format="value(status.conditions[0].status,status.conditions[0].message)"
```

**Explanation:** This shows you the current status of your services and any error messages if there are issues.

### 9.2 View Application Logs
**What this does:** Views detailed logs to understand how your applications are performing and identify any issues.

```bash
# View recent application logs for all services
echo "Recent logs from all services:"
gcloud logging read "resource.type=cloud_run_revision AND (resource.labels.service_name=rag-service-$SUFFIX OR resource.labels.service_name=ocr-service-$SUFFIX OR resource.labels.service_name=vision-ocr-service-$SUFFIX)" \
  --limit=10
```

**Explanation:** Logs provide detailed information about requests, errors, and performance that help you optimize your applications.

## 🧹 Step 10: Cleanup (Optional)

### 10.1 Clean Up Resources
**What this does:** Removes all resources created during the workshop to avoid ongoing charges.

```bash
# Delete Cloud Run services
gcloud run services delete rag-service-$SUFFIX --region=$REGION --quiet
gcloud run services delete ocr-service-$SUFFIX --region=$REGION --quiet
gcloud run services delete vision-ocr-service-$SUFFIX --region=$REGION --quiet

# Only delete Streamlit if you deployed it to Cloud Run
if gcloud run services describe streamlit-frontend-$SUFFIX --region=$REGION --quiet 2>/dev/null; then
  gcloud run services delete streamlit-frontend-$SUFFIX --region=$REGION --quiet
fi

# Delete Artifact Registry repository
gcloud artifacts repositories delete ocr-repo-$SUFFIX --location=$REGION --quiet

# Delete Cloud Storage bucket
gsutil -m rm -r gs://mlops-workshop-$SUFFIX-$PROJECT_ID/

# Clean up local virtual environment (if using local Streamlit)
if [ -d "streamlit-frontend/.streamlit" ]; then
  echo "Removing local Streamlit virtual environment..."
  rm -rf streamlit-frontend/.streamlit
fi
```

**Explanation:** These commands remove all the resources you created during the workshop. Use `--quiet` to skip confirmation prompts.

## 🎉 Congratulations!

You've successfully built a complete MLOps pipeline with:
- ✅ **RAG Service** - AI-powered document Q&A
- ✅ **Tesseract OCR Service** - Free text extraction
- ✅ **Cloud Vision OCR Service** - Professional text extraction
- ✅ **CI/CD Pipeline** - Automated deployment for all services
- ✅ **Model Serving** - All services deployed to Cloud Run
- ✅ **Streamlit Frontend** - Web interface (local or Cloud Run)
- ✅ **Data Versioning** - Cloud Storage with object versioning
- ✅ **Web Interface** - Streamlit frontend for all services
- ✅ **Basic Monitoring** - Cloud Logging for all services

## 🔗 Useful Links

- **Cloud Console**: https://console.cloud.google.com/
- **Cloud Run**: https://console.cloud.google.com/run
- **Cloud Build**: https://console.cloud.google.com/cloud-build
- **Cloud Storage**: https://console.cloud.google.com/storage
- **Cloud Logging**: https://console.cloud.google.com/logs

## 📚 Next Steps

Ready for advanced features? Check out `PARTICIPANT_BONUS_GUIDE.md` for:
- Vertex AI Model Registry
- Advanced monitoring and alerting
- Custom metrics and dashboards
- Production-ready MLOps features

---
