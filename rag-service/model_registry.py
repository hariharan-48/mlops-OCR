"""
Real Google Cloud Vertex AI Model Registry for Workshop Demo
Uses actual Vertex AI Model Registry for production-grade model versioning
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

try:
    from google.cloud import aiplatform
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    print("⚠️  google-cloud-aiplatform not available, using fallback")

class VertexAIModelRegistry:
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("REGION", "us-central1")
        self.suffix = os.getenv("SUFFIX", "demo")
        
        # Initialize Vertex AI if available
        if VERTEX_AI_AVAILABLE and self.project_id:
            try:
                aiplatform.init(project=self.project_id, location=self.location)
                print(f"✅ Vertex AI initialized for project: {self.project_id}")
            except Exception as e:
                print(f"⚠️  Vertex AI initialization failed: {str(e)}")
    
    def register_model(self, model_name: str, version: str, metadata: Dict) -> str:
        """Register a new model in Vertex AI Model Registry"""
        if not VERTEX_AI_AVAILABLE:
            print("⚠️  Vertex AI not available, using fallback registration")
            return f"{model_name}_{version}"
        
        try:
            # Create model in Vertex AI Model Registry
            model = aiplatform.Model.upload(
                display_name=model_name,
                description=metadata.get("description", "RAG service model"),
                serving_container_image_uri=metadata.get("serving_container_image_uri"),
                serving_container_predict_route=metadata.get("serving_container_predict_route", "/query"),
                serving_container_health_route=metadata.get("serving_container_health_route", "/health"),
                serving_container_ports=metadata.get("serving_container_ports", [8080]),
                labels={
                    "version": version,
                    "model_type": metadata.get("model_type", "rag"),
                    "workshop": "mlops-ocr",
                    "llm_model": metadata.get("llm_model", "gemini-2.5-flash"),
                    "embedding_model": metadata.get("embedding_model", "text-embedding-gecko"),
                    "accuracy": str(metadata.get("performance_metrics", {}).get("accuracy", 0.85)),
                    "response_time": metadata.get("performance_metrics", {}).get("response_time", "2.3s")
                }
            )
            
            print(f"✅ Model registered in Vertex AI Model Registry: {model.resource_name}")
            return model.resource_name
            
        except Exception as e:
            print(f"❌ Error registering model in Vertex AI: {str(e)}")
            print("   This might be due to:")
            print("   - Missing Vertex AI API permissions")
            print("   - API not enabled")
            print("   - Service account limitations")
            return f"{model_name}_{version}"
    
    def list_models(self) -> List[Dict]:
        """List all models in Vertex AI Model Registry"""
        if not VERTEX_AI_AVAILABLE:
            print("⚠️  Vertex AI not available, returning empty list")
            return []
        
        try:
            models = aiplatform.Model.list()
            models_list = []
            
            for model in models:
                models_list.append({
                    "name": model.display_name,
                    "resource_name": model.resource_name,
                    "create_time": model.create_time.isoformat(),
                    "labels": model.labels
                })
            
            print(f"📋 Found {len(models_list)} models in Vertex AI Model Registry")
            return models_list
            
        except Exception as e:
            print(f"❌ Error listing models from Vertex AI: {str(e)}")
            return []
    
    def get_model_versions(self, model_name: str) -> List[Dict]:
        """Get all versions of a specific model"""
        if not VERTEX_AI_AVAILABLE:
            print("⚠️  Vertex AI not available, returning empty list")
            return []
        
        try:
            models = aiplatform.Model.list(filter=f'display_name="{model_name}"')
            versions = []
            
            for model in models:
                versions.append({
                    "model_name": model.display_name,
                    "version": model.labels.get("version", "v1.0"),
                    "resource_name": model.resource_name,
                    "create_time": model.create_time.isoformat(),
                    "labels": model.labels,
                    "description": model.description
                })
            
            print(f"📋 Found {len(versions)} versions for model '{model_name}' in Vertex AI Model Registry")
            return versions
            
        except Exception as e:
            print(f"❌ Error getting model versions from Vertex AI: {str(e)}")
            return []
    
    def get_latest_model(self, model_name: str) -> Optional[Dict]:
        """Get the latest version of a model"""
        if not VERTEX_AI_AVAILABLE:
            print("⚠️  Vertex AI not available, returning None")
            return None
        
        try:
            models = aiplatform.Model.list(filter=f'display_name="{model_name}"')
            if models:
                # Get the most recently created model
                latest_model = max(models, key=lambda x: x.create_time)
                result = {
                    "model_name": latest_model.display_name,
                    "version": latest_model.labels.get("version", "v1.0"),
                    "resource_name": latest_model.resource_name,
                    "create_time": latest_model.create_time.isoformat(),
                    "labels": latest_model.labels,
                    "description": latest_model.description
                }
                print(f"📋 Retrieved latest model '{model_name}' from Vertex AI Model Registry")
                return result
            return None
            
        except Exception as e:
            print(f"❌ Error getting latest model from Vertex AI: {str(e)}")
            return None
    
    def deploy_model(self, model_name: str, endpoint_name: str = None) -> str:
        """Deploy a model to an endpoint"""
        if not VERTEX_AI_AVAILABLE:
            print("⚠️  Vertex AI not available, cannot deploy model")
            return None
        
        try:
            models = aiplatform.Model.list(filter=f'display_name="{model_name}"')
            if not models:
                raise Exception(f"Model {model_name} not found in Vertex AI Model Registry")
            
            latest_model = max(models, key=lambda x: x.create_time)
            
            if not endpoint_name:
                endpoint_name = f"{model_name}-endpoint"
            
            # Create endpoint
            endpoint = aiplatform.Endpoint.create(
                display_name=endpoint_name,
                project=self.project_id,
                location=self.location
            )
            
            # Deploy model to endpoint
            endpoint.deploy(
                model=latest_model,
                deployed_model_display_name=f"{model_name}-deployed",
                machine_type="n1-standard-2",
                min_replica_count=1,
                max_replica_count=3
            )
            
            print(f"🚀 Model '{model_name}' deployed to Vertex AI Endpoint: {endpoint.resource_name}")
            return endpoint.resource_name
            
        except Exception as e:
            print(f"❌ Error deploying model to Vertex AI: {str(e)}")
            return None

# Global registry instance
model_registry = VertexAIModelRegistry()

# Register our RAG model
def register_rag_model():
    """Register the RAG model in Vertex AI Model Registry"""
    metadata = {
        "model_type": "rag",
        "llm_model": "gemini-2.5-flash",
        "embedding_model": "text-embedding-gecko",
        "description": "RAG service for document Q&A with Gemini 2.5 Flash",
        "serving_container_image_uri": f"us-central1-docker.pkg.dev/{os.getenv('GOOGLE_CLOUD_PROJECT')}/ocr-repo-{os.getenv('SUFFIX')}/rag-service-{os.getenv('SUFFIX')}:v3",
        "serving_container_predict_route": "/query",
        "serving_container_health_route": "/health",
        "performance_metrics": {
            "accuracy": 0.85,
            "response_time": "2.3s"
        }
    }
    
    return model_registry.register_model(
        model_name=f"rag-service-{os.getenv('SUFFIX', 'demo')}",
        version="v1.0",
        metadata=metadata
    ) 