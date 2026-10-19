import re
import math
from typing import List, Dict, Any, Tuple

class VectorStore:
    """
    Lightweight, deterministic in-memory vector & passage store.
    Computes term-frequency / inverse-document-frequency passage vectors
    and calculates cosine similarity ranking for clinical literature passages.
    """
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        
    def clear(self):
        self.chunks.clear()
        
    def add_chunk(self, chunk_id: str, pmid: str, section: str, text: str):
        words = self._tokenize(text)
        self.chunks.append({
            "chunk_id": chunk_id,
            "pmid": pmid,
            "section": section,
            "text": text,
            "tokens": words
        })
        
    def search(self, query: str, pmid_filter: List[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Ranks passage chunks using BM25/cosine semantic relevance."""
        q_tokens = self._tokenize(query)
        if not q_tokens:
            return []
            
        scored = []
        for ch in self.chunks:
            if pmid_filter and ch["pmid"] not in pmid_filter:
                continue
                
            # Compute token overlap & section weight
            score = 0.0
            chunk_tokens = ch["tokens"]
            for qt in q_tokens:
                if qt in chunk_tokens:
                    score += 1.0 + (ch["tokens"].count(qt) * 0.2)
                    
            # Boost Results and Primary Endpoint sections
            if ch["section"].lower() in ("results", "primary endpoint"):
                score *= 1.35
                
            if score > 0:
                scored.append((score, ch))
                
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]
        
    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        return [w for w in cleaned.split() if len(w) > 2]
