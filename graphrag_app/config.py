import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "GraphRAG Literature Platform"
    APP_VERSION: str = "2.0.0"
    PORT: int = int(os.environ.get("PORT", 8080))
    HOST: str = "0.0.0.0"
    DEBUG: bool = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
    
    # NLP & Ontology Settings
    BENCHMARK_DRUG_CLASS: str = "SGLT2 inhibitors"
    DEFAULT_RETRIEVAL_K: int = 6
    NLI_ENTAILMENT_THRESHOLD: float = 0.85
    
    # Cloud Deployment Settings
    GCP_PROJECT: str = os.environ.get("GCP_PROJECT", "")
    GCP_REGION: str = os.environ.get("GCP_REGION", "us-central1")

settings = Settings()
