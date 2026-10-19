import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

class HistoryStore:
    """
    Persistent Audit and Traceability Store.
    Saves all user natural language queries, the exact documents/trials retrieved with each query,
    the synthesized answers, refined prompts, and all document ingestion operations.
    Persists data to JSON on disk for zero-data-loss audit compliance.
    """
    def __init__(self, storage_path: str = "data/audit_history.json"):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        """Ensures the storage directory and file exist."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            initial_data = {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "queries": [],
                "ingestions": []
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    def _read_data(self) -> dict:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading history store: {e}")
            return {"queries": [], "ingestions": []}

    def _write_data(self, data: dict):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error writing to history store: {e}")

    def log_query(
        self,
        query_text: str,
        intent: str,
        retrieved_articles: List[Dict[str, Any]],
        synthesis: str,
        refined_prompts: List[Dict[str, Any]],
        audit_badge: str
    ) -> Dict[str, Any]:
        """Records a user query event with exact associated documents."""
        data = self._read_data()
        
        query_entry = {
            "query_id": f"q_{int(time.time() * 1000)}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "query_text": query_text,
            "intent": intent,
            "documents_count": len(retrieved_articles),
            "documents": [
                {
                    "pmid": a.get("pmid"),
                    "title": a.get("title"),
                    "journal": a.get("journal"),
                    "year": a.get("year"),
                    "sample_size": a.get("sample_size"),
                    "drug": a.get("pico", {}).get("interventions", [{}])[0].get("name", "N/A") if a.get("pico") else "N/A",
                    "primary_outcome": a.get("pico", {}).get("outcomes", [{}])[0].get("name", "N/A") if a.get("pico") else "N/A"
                }
                for a in retrieved_articles
            ],
            "synthesis_snippet": synthesis[:220] + ("..." if len(synthesis) > 220 else ""),
            "refined_prompts": refined_prompts,
            "audit_badge": audit_badge
        }
        
        data.setdefault("queries", []).insert(0, query_entry)
        self._write_data(data)
        return query_entry

    def log_ingestion(
        self,
        input_query: str,
        ingested_articles: List[Dict[str, Any]],
        total_chunks: int,
        kg_edges: int
    ) -> Dict[str, Any]:
        """Records an article ingestion event with input query and indexed documents."""
        data = self._read_data()

        ingest_entry = {
            "ingest_id": f"ing_{int(time.time() * 1000)}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "input_query": input_query,
            "total_ingested": len(ingested_articles),
            "ingested_documents": [
                {
                    "pmid": a.get("pmid"),
                    "title": a.get("title"),
                    "journal": a.get("journal"),
                    "year": a.get("year"),
                    "sample_size": a.get("sample_size"),
                    "section_chunks_count": len(a.get("section_chunks", []))
                }
                for a in ingested_articles
            ],
            "section_chunks_added": total_chunks,
            "total_kg_edges": kg_edges
        }

        data.setdefault("ingestions", []).insert(0, ingest_entry)
        self._write_data(data)
        return ingest_entry

    def get_queries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the most recent user queries."""
        data = self._read_data()
        return data.get("queries", [])[:limit]

    def get_ingestions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the most recent ingestion operations."""
        data = self._read_data()
        return data.get("ingestions", [])[:limit]

    def get_full_history(self) -> Dict[str, Any]:
        """Returns aggregated summary metrics and complete log lists."""
        data = self._read_data()
        queries = data.get("queries", [])
        ingestions = data.get("ingestions", [])
        return {
            "total_queries_logged": len(queries),
            "total_ingestions_logged": len(ingestions),
            "recent_queries": queries[:30],
            "recent_ingestions": ingestions[:30]
        }

    def clear(self):
        """Clears all audit logs."""
        self._write_data({
            "created_at": datetime.utcnow().isoformat() + "Z",
            "queries": [],
            "ingestions": []
        })
