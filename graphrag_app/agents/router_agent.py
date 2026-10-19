from typing import List, Set, Tuple
from models.chat import QueryIntent
from models.article import Article
from database.knowledge_graph import KnowledgeGraphManager
from database.vector_store import VectorStore

class RouterAgent:
    """
    Agent 4: Hybrid Router & Pathfinding Agent.
    Inspects user clinical queries, classifies query intent,
    and orchestrates multi-path retrieval across the knowledge graph
    and dense passage vector store.
    """
    def __init__(self, kg_manager: KnowledgeGraphManager, vector_store: VectorStore):
        self.kg_manager = kg_manager
        self.vector_store = vector_store

    def classify_intent(self, query: str) -> QueryIntent:
        """Determines the optimal execution pathway from query linguistic signatures."""
        q = query.lower()
        if any(k in q for k in ["how many", "count", "percentage of rct", "sample size range"]):
            return QueryIntent.AGGREGATION
        elif any(k in q for k in ["themes", "landscape", "trend", "thematic", "consensus"]):
            return QueryIntent.GLOBAL_THEMATIC
        elif any(k in q for k in ["compare", "which trials", "across studies", "sglt2", "trials", "progression", "ckd"]):
            return QueryIntent.GRAPH_ENTITY
        else:
            return QueryIntent.VECTOR_FACT

    def route_and_retrieve(self, query: str, active_articles: List[Article]) -> Tuple[QueryIntent, Set[str], List[dict]]:
        """
        Executes hybrid retrieval:
        1. Classifies intent.
        2. Executes graph traversal if entity-centric.
        3. Retrieves ranked passages from the vector store.
        """
        intent = self.classify_intent(query)
        q = query.lower()

        matched_pmids: Set[str] = set()

        if intent == QueryIntent.GRAPH_ENTITY:
            # Check for CKD or Kidney query
            is_ckd = any(k in q for k in ["kidney", "ckd", "renal", "egfr", "progression"])
            is_hf = any(k in q for k in ["heart failure", "hf", "hfr-ef", "cv death", "mortality"])

            for art in active_articles:
                pico = art.pico
                if not pico:
                    continue
                pop_desc = pico.population.description.lower() if pico.population else ""
                cond_name = pico.population.condition.lower() if pico.population else ""

                if is_ckd and ("kidney" in cond_name or "ckd" in cond_name or "nephropathy" in pop_desc):
                    matched_pmids.add(art.pmid)
                elif is_hf and ("heart failure" in cond_name or "ejection fraction" in pop_desc):
                    matched_pmids.add(art.pmid)

            # Fallback if specific condition not recognized
            if not matched_pmids:
                matched_pmids = {a.pmid for a in active_articles}

        elif intent == QueryIntent.AGGREGATION or intent == QueryIntent.GLOBAL_THEMATIC:
            matched_pmids = {a.pmid for a in active_articles}
        else:
            # Single fact lookup: vector search across all chunks
            chunks = self.vector_store.search(query, top_k=5)
            matched_pmids = {ch["pmid"] for ch in chunks}
            if not matched_pmids:
                matched_pmids = {a.pmid for a in active_articles[:3]}

        # Rank passages specifically for matched trials
        ranked_chunks = self.vector_store.search(query, pmid_filter=list(matched_pmids), top_k=6)

        return intent, matched_pmids, ranked_chunks
