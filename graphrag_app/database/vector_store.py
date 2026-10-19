import re
import math
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("graphrag.vector_store")

class VectorStore:
    """
    Hybrid Dense & Lexical Vector Store for Clinical Literature Passages.
    Combines dense semantic vector embeddings (Google text-embedding-004 standard, 768d)
    with clinical section outcome boosting (1.35x multiplier on Results / Primary Endpoints).
    Falls back gracefully to term-frequency BM25/cosine overlap when offline.
    """
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []

    def clear(self):
        self.chunks.clear()

    def add_chunk(self, chunk_id: str, pmid: str, section: str, text: str, embedding: Optional[List[float]] = None):
        words = self._tokenize(text)
        self.chunks.append({
            "chunk_id": chunk_id,
            "pmid": pmid,
            "section": section,
            "text": text,
            "tokens": words,
            "embedding": embedding
        })

    def add_chunks(self, chunk_dicts: List[Dict[str, Any]]):
        """Batch adds chunks and computes dense embeddings incrementally if client is active."""
        if not chunk_dicts:
            return

        from agents.llm_client import gemini_client

        chunks_needing_emb = [c for c in chunk_dicts if not c.get("embedding")]
        if chunks_needing_emb and gemini_client.is_available():
            texts = [c["text"] for c in chunks_needing_emb]
            try:
                dense_embeddings = gemini_client.generate_embeddings(texts)
                logger.info(f"VectorStore: Batch embedded {len(dense_embeddings)} new chunks.")
                for idx, c in enumerate(chunks_needing_emb):
                    if idx < len(dense_embeddings):
                        c["embedding"] = dense_embeddings[idx]
            except Exception as e:
                logger.warning(f"VectorStore: Dense embedding failed, using lexical fallback: {e}")

        for c in chunk_dicts:
            self.add_chunk(
                chunk_id=c["chunk_id"],
                pmid=c["pmid"],
                section=c["section"],
                text=c["text"],
                embedding=c.get("embedding")
            )

    def has_dense_embeddings(self) -> bool:
        return any(c.get("embedding") is not None and len(c["embedding"]) > 0 for c in self.chunks)

    def search(self, query: str, pmid_filter: List[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Ranks passage chunks using dense semantic cosine similarity (text-embedding-004)
        with clinical section weighting. Falls back to lexical overlap if offline.
        """
        if not query:
            return []

        # 1. Attempt Dense Semantic Vector Search
        if self.has_dense_embeddings():
            from agents.llm_client import gemini_client
            if gemini_client.is_available():
                q_embs = gemini_client.generate_embeddings([query])
                if q_embs and len(q_embs) > 0 and len(q_embs[0]) > 0:
                    q_vec = q_embs[0]
                    dense_scored = []
                    for ch in self.chunks:
                        if pmid_filter and ch["pmid"] not in pmid_filter:
                            continue
                        if not ch.get("embedding"):
                            continue

                        sim = self._cosine_similarity(q_vec, ch["embedding"])
                        # Boost Results and Primary Endpoint sections
                        if ch["section"].lower() in ("results", "primary endpoint"):
                            sim *= 1.35

                        if sim > 0:
                            dense_scored.append((sim, ch))

                    if dense_scored:
                        dense_scored.sort(key=lambda x: x[0], reverse=True)
                        return [item[1] for item in dense_scored[:top_k]]

        # 2. Lexical / BM25 Overlap Fallback
        q_tokens = self._tokenize(query)
        if not q_tokens:
            return []

        scored = []
        for ch in self.chunks:
            if pmid_filter and ch["pmid"] not in pmid_filter:
                continue

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

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Pure-Python standard cosine similarity."""
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        return [w for w in cleaned.split() if len(w) > 2]
