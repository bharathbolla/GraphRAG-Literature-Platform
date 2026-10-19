from typing import List
from models.article import Article
from database.benchmark_data import get_benchmark_articles
from database.knowledge_graph import KnowledgeGraphManager
from database.vector_store import VectorStore
from database.history_store import HistoryStore
from agents.ingestion_agent import IngestionAgent
from agents.extraction_guard_agent import ExtractionGuardAgent
from agents.ontology_agent import OntologyAgent
from agents.router_agent import RouterAgent
from agents.synthesis_audit_agent import SynthesisAuditAgent
from agents.prompt_refiner_agent import PromptRefinerAgent

class AppState:
    """Singleton application state holding active corpus, micro-agents, and audit history store."""
    def __init__(self):
        self.articles: List[Article] = []
        self.kg_manager = KnowledgeGraphManager()
        self.vector_store = VectorStore()
        self.history_store = HistoryStore()
        
        # Initialize autonomous micro-agents
        self.ingestion_agent = IngestionAgent()
        self.extraction_guard_agent = ExtractionGuardAgent()
        self.ontology_agent = OntologyAgent()
        self.router_agent = RouterAgent(self.kg_manager, self.vector_store)
        self.prompt_refiner = PromptRefinerAgent()
        self.synthesis_audit_agent = SynthesisAuditAgent()
        
        # Load default benchmark
        self.reset_to_benchmark()

    def reset_to_benchmark(self):
        """Resets the corpus to the verified 7 landmark cardiorenal RCTs."""
        self.articles = get_benchmark_articles()
        self.sync_graph_and_vectors()

    def sync_graph_and_vectors(self):
        """Synchronizes knowledge graph and vector store from active articles."""
        self.kg_manager.rebuild_from_articles(self.articles)
        self.vector_store.clear()
        
        for art in self.articles:
            # Chunk abstract into sections
            sections = art.abstract.split("\n")
            for idx, sec in enumerate(sections):
                sec_name = "Abstract"
                if ":" in sec:
                    sec_name = sec.split(":")[0].strip()
                self.vector_store.add_chunk(
                    chunk_id=f"chk_{art.pmid}_{idx}",
                    pmid=art.pmid,
                    section=sec_name,
                    text=sec
                )

# Global runtime state instance
app_state = AppState()
