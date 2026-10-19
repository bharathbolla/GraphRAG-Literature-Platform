from fastapi import APIRouter
from .routes_corpus import router as corpus_router
from .routes_chat import router as chat_router
from .routes_ner import router as ner_router
from .routes_pico import router as pico_router
from .routes_graph import router as graph_router

api_router = APIRouter(prefix="/api")
api_router.include_router(corpus_router, tags=["Corpus & Ingestion"])
api_router.include_router(chat_router, tags=["Clinical Multi-Doc Chat"])
api_router.include_router(ner_router, tags=["Biomedical NER"])
api_router.include_router(pico_router, tags=["Structured PICO Grid"])
api_router.include_router(graph_router, tags=["Knowledge Graph"])

__all__ = ["api_router"]
