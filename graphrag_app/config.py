import os
from pathlib import Path
from pydantic import BaseModel
from typing import List

# Safely load environment variables from .env if available
try:
    from dotenv import load_dotenv
    # Check local project root .env then home .env
    env_paths = [
        Path(__file__).resolve().parent / ".env",
        Path.home() / ".env"
    ]
    for p in env_paths:
        if p.exists():
            load_dotenv(p)
            break
except ImportError:
    pass

class Settings(BaseModel):
    APP_NAME: str = "GraphRAG Literature Platform"
    APP_VERSION: str = "2.1.0"
    PORT: int = int(os.environ.get("PORT", 8080))
    HOST: str = "0.0.0.0"
    DEBUG: bool = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
    
    # NLP & Ontology Settings
    BENCHMARK_DRUG_CLASS: str = "SGLT2 inhibitors"
    DEFAULT_RETRIEVAL_K: int = 6
    NLI_ENTAILMENT_THRESHOLD: float = 0.85
    
    # Gemini Flash Dynamic Agent Settings
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
    GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
    GEMINI_FALLBACK_MODELS: List[str] = [
        "gemini-3.8-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]
    USE_DYNAMIC_AGENTS: bool = True

    # Vector Embedding Settings (768d standard matching text-embedding-004)
    EMBEDDING_MODEL: str = os.environ.get("EMBEDDING_MODEL", "gemini-embedding-001")
    EMBEDDING_DIMENSIONS: int = int(os.environ.get("EMBEDDING_DIMENSIONS", 768))
    EMBEDDING_FALLBACK_MODELS: List[str] = [
        "gemini-embedding-001",
        "gemini-embedding-2",
        "text-embedding-004"
    ]
    
    # Cloud Deployment Settings
    GCP_PROJECT: str = os.environ.get("GCP_PROJECT", "graphrag-novartis")
    GCP_REGION: str = os.environ.get("GCP_REGION", "us-central1")

settings = Settings()
