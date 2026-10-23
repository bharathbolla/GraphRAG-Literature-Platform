import re
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
    Features dynamic open-domain entity pathfinding across any clinical condition or drug.
    """
    def __init__(self, kg_manager: KnowledgeGraphManager, vector_store: VectorStore):
        self.kg_manager = kg_manager
        self.vector_store = vector_store

    def classify_intent(self, query: str) -> QueryIntent:
        """Determines the optimal execution pathway from query linguistic signatures."""
        q = query.lower()
        if any(k in q for k in ["how many", "count", "percentage of rct", "sample size range", "total patient"]):
            return QueryIntent.AGGREGATION
        elif any(k in q for k in ["themes", "landscape", "trend", "thematic", "consensus", "community"]):
            return QueryIntent.GLOBAL_THEMATIC
        elif any(k in q for k in ["compare", "which trials", "across studies", "sglt2", "trials", "progression", "ckd", "versus", "vs", "hazard ratio", "efficacy", "endpoint"]):
            return QueryIntent.GRAPH_ENTITY
        else:
            return QueryIntent.VECTOR_FACT

    def route_and_retrieve(self, query: str, active_articles: List[Article]) -> Tuple[QueryIntent, Set[str], List[dict]]:
        """
        Executes hybrid retrieval:
        1. Classifies intent.
        2. Executes dynamic open-domain graph traversal if entity-centric.
        3. Retrieves ranked passages from the vector store.
        """
        intent = self.classify_intent(query)
        q = query.lower()

        matched_pmids: Set[str] = set()

        if intent == QueryIntent.GRAPH_ENTITY:
            # Dynamic open-domain entity pathfinding
            q_tokens = set(re.findall(r'\b[a-z0-9\-]{3,}\b', q))

            for art in active_articles:
                art_matched = False
                pico = art.pico
                if not pico:
                    continue

                # 1. Condition & Population match
                if pico.population:
                    cond_str = (pico.population.condition or "").lower()
                    pop_desc = (pico.population.description or "").lower()
                    cond_tokens = set(re.findall(r'\b[a-z0-9\-]{3,}\b', cond_str))
                    desc_tokens = set(re.findall(r'\b[a-z0-9\-]{3,}\b', pop_desc))
                    if (q_tokens & cond_tokens) or (len(q_tokens & desc_tokens) >= 2):
                        art_matched = True

                # 2. Intervention / Drug match
                for inter in pico.interventions:
                    drug_str = (inter.name or "").lower()
                    drug_tokens = set(re.findall(r'\b[a-z0-9\-]{3,}\b', drug_str))
                    if q_tokens & drug_tokens:
                        art_matched = True
                        break

                # 3. Clinical Outcome match
                for out in pico.outcomes:
                    out_tokens = set(re.findall(r'\b[a-z0-9\-]{3,}\b', (out.name or "").lower()))
                    if len(q_tokens & out_tokens) >= 2:
                        art_matched = True
                        break

                # 4. Title tokens match
                title_tokens = set(re.findall(r'\b[a-z0-9\-]{3,}\b', art.title.lower()))
                if len(q_tokens & title_tokens) >= 2:
                    art_matched = True

                if art_matched:
                    matched_pmids.add(art.pmid)

            # Fallback if no specific subset matched
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
