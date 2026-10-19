# GraphRAG Platform for Research Literature: Chat, NER and PICO

Design document for an application that retrieves research articles for a search query, builds a knowledge graph over them, and serves three applications: multi-document chat (QA + summarization), named entity recognition (NER) browsing, and PICO evidence extraction.

---

## 1. Problem statement

Users run a literature search (e.g. PubMed query). The system collects the matching articles and lets users:

1. **Chat** – ask questions whose answers require reading and combining many papers, with citations.
2. **NER** – browse diseases, drugs, genes, outcomes, etc. mentioned across the corpus and jump to the papers.
3. **PICO** – see a structured grid of Population, Intervention, Comparator and Outcome for each study, and filter/compare.

## 2. Decision: GraphRAG (hybrid) over traditional RAG

### 2.1 Key insight

NER and PICO are not separate apps built *on top of* the graph. They are the **extraction layer that builds the graph**. One extraction pass produces structured data that powers all three applications.

```
Articles ─► NER + PICO extraction ─► Normalization (MeSH/UMLS) ─► Knowledge Graph + Vectors
                                                                       │
                                        ┌──────────────┬───────────────┼───────────────┐
                                        ▼              ▼               ▼
                                     Chat/QA      NER Explorer     PICO Grid
```

### 2.2 Why traditional (vector-only) RAG is insufficient here

| Limitation | Effect on literature QA |
|---|---|
| Top-k retrieval | If 40 papers are relevant and k = 8, most evidence is ignored silently |
| Similarity ≠ relevance | Passing mentions in Discussion rank as high as Results |
| No entity identity | "T2DM", "type 2 diabetes mellitus", "NIDDM" are not unified |
| No cross-document relations | Can't tell that two papers studied the same drug/population/outcome |
| No aggregation | "How many RCTs…" or "compare effect sizes" is unreliable |
| Global questions | "Main themes of this corpus?" has no single answering chunk |

### 2.3 What GraphRAG provides

- **Completeness**: retrieve *every* study linked to a concept, not a similarity sample.
- **Normalization**: synonyms resolve to one concept ID.
- **Multi-hop**: Drug → DrugClass → Outcome → Population.
- **Aggregation**: graph queries for counts, groupings, comparisons.
- **Global summaries**: community detection + community summaries for corpus-level questions.
- **Provenance**: each edge stores source article ID and sentence → sentence-level citations.
- **Reuse**: the same graph serves chat, NER and PICO.

### 2.4 Comparison

| Capability | Traditional RAG | GraphRAG (hybrid) |
|---|---|---|
| Single-fact lookup | Good, cheap | Good (vector path) |
| Multi-paper synthesis | Limited | Strong |
| Synonym handling | Fuzzy | Concept IDs |
| Counting / aggregation | Unreliable | Native |
| Multi-hop | Weak | Strong |
| Corpus themes | Poor | Community summaries |
| NER/PICO output | Separate pipeline | Same data |
| Indexing cost | Low | High |
| Build complexity | Low | Medium–High |
| Incremental updates | Easy | Needs re-linking / summary refresh |

### 2.5 When to stay with vector RAG

- Small per-search corpora (a few papers)
- Mostly single-paper questions
- Throwaway searches where indexing cost dominates
- Early prototype

**Recommendation:** build a vector RAG baseline first, then add the graph. Keep both: graph for filtering and structure, vectors for passage ranking.

---

## 3. Architecture

### 3.1 Components

| Layer | Purpose | Suggested tools |
|---|---|---|
| Ingestion | Search + fetch metadata, abstracts, OA full text | PubMed E-utilities, PMC OA subset, Europe PMC |
| Parsing | PDF/XML → sections, tables | PMC XML (preferred), GROBID for PDFs |
| Chunking | Section-aware chunks (300–600 tokens) | Custom, keep section labels |
| NER | Biomedical entities | scispaCy, PubTator annotations, or an LLM |
| PICO extraction | Spans + structured fields | LLM with JSON schema; EBM-NLP-trained models as alternative |
| Normalization | Map to concept IDs | UMLS / MeSH, scispaCy entity linker, RxNorm for drugs |
| Relation extraction | Study–reports–Outcome with effects | LLM, constrained schema |
| Graph store | Nodes/edges + properties | Neo4j (built-in vector index) or Postgres + pgvector |
| Vector store | Chunk embeddings | Neo4j vector index / pgvector / Qdrant |
| Community layer | Clusters + summaries for global questions | Leiden clustering; Microsoft GraphRAG or LightRAG patterns |
| Orchestration | Retrieval + generation | LangGraph / LlamaIndex / plain Python |
| LLM | PICO parsing, synthesis | Any capable LLM |
| UI | Chat, entity explorer, PICO grid | React / Streamlit |

### 3.2 Graph schema

**Nodes**

| Label | Key properties |
|---|---|
| `Article` | pmid, doi, title, year, journal, study_design |
| `Chunk` | id, section, text, embedding |
| `Population` | description, condition_cui, age_range, n |
| `Intervention` | name, concept_cui, dose, duration |
| `Comparator` | name, concept_cui |
| `Outcome` | name, concept_cui, timepoint |
| `Condition` | name, cui (MeSH/UMLS) |
| `Drug` | name, rxnorm_id, cui |
| `DrugClass` | name, cui |
| `Gene` / `Protein` | symbol, id |
| `Community` | level, summary |

**Edges**

```
(Article)-[:HAS_CHUNK]->(Chunk)
(Article)-[:ENROLLS]->(Population)
(Article)-[:STUDIES]->(Intervention)
(Article)-[:COMPARES_TO]->(Comparator)
(Article)-[:REPORTS {effect, unit, ci_low, ci_high, p_value, direction, source_sentence}]->(Outcome)
(Population)-[:HAS_CONDITION]->(Condition)
(Intervention)-[:IS_DRUG]->(Drug)
(Drug)-[:IS_A]->(DrugClass)
(Chunk)-[:MENTIONS]->(Condition|Drug|Gene|Outcome)
(Entity)-[:IN_COMMUNITY]->(Community)
```

Every extracted edge stores `article_id` and `source_sentence` for provenance.

---

## 4. Extraction

### 4.1 PICO extraction prompt (per article)

```text
You extract PICO elements from a biomedical article.
Return ONLY JSON matching this schema. Use null when not reported.
Quote the exact supporting sentence for every field.

{
  "study_design": "RCT | cohort | case-control | cross-sectional | systematic review | other",
  "population": {"description": str, "condition": str, "n": int|null,
                 "age": str|null, "setting": str|null, "evidence": str},
  "interventions": [{"name": str, "dose": str|null, "duration": str|null, "evidence": str}],
  "comparators":   [{"name": str, "evidence": str}],
  "outcomes": [{"name": str, "timepoint": str|null, "effect": str|null,
                "measure": "MD|RR|OR|HR|other|null", "ci": str|null,
                "p_value": str|null, "direction": "benefit|harm|null|unclear",
                "evidence": str}]
}

Article:
<title> ... </title>
<abstract> ... </abstract>
<results> ... </results>
```

### 4.2 Extraction guidelines

- Use specialized biomedical NER for entity mentions (cheaper, consistent); use the LLM for PICO and relations.
- Validate JSON against the schema; reject and retry on failure.
- Require evidence quotes; drop fields whose quote is not found in the source text (hallucination guard).
- Prefer full-text Results and tables for effect sizes; abstracts for quick PICO.

### 4.3 Normalization / entity resolution

1. Link each mention to UMLS CUI / MeSH ID (scispaCy linker or API lookup).
2. Drugs → RxNorm; map to drug class via ATC or MeSH pharmacological action.
3. Merge nodes sharing a concept ID.
4. Keep unlinked mentions as `Unresolved` nodes for manual review.

---

## 5. Retrieval and answering (chat)

### 5.1 Query routing

| Question type | Example | Path |
|---|---|---|
| Local / single fact | "What dose did the EMPA-KIDNEY trial use?" | Vector search |
| Cross-study, entity-centric | "Which SGLT2i trials reported HbA1c in CKD?" | Graph → vectors |
| Aggregation | "How many RCTs studied metformin vs placebo?" | Graph query (Cypher/SQL) |
| Global / thematic | "What are the main research themes?" | Community summaries |

### 5.2 Hybrid pipeline

1. **Parse question to PICO** with the LLM; map terms to concept IDs.
2. **Graph retrieval**: find `Article` nodes matching P/I/C/O; expand via `IS_A` (class → members).
3. **Vector retrieval within the subset**: rank chunks only from matched articles.
4. **Build structured context**: evidence table (article, design, n, intervention, comparator, outcome, effect, CI) + top passages.
5. **Generate**: synthesize, group by intervention/outcome, note conflicts and study quality, cite `[PMID:sentence]`.
6. **Verify**: check each cited claim exists in the cited source.

### 5.3 Example Cypher

```cypher
MATCH (d:DrugClass {name:'SGLT2 inhibitors'})<-[:IS_A]-(drug:Drug)
      <-[:IS_DRUG]-(i:Intervention)<-[:STUDIES]-(a:Article)
MATCH (a)-[:ENROLLS]->(p:Population)-[:HAS_CONDITION]->(c:Condition)
WHERE c.cui IN $ckd_cuis
MATCH (a)-[r:REPORTS]->(o:Outcome) WHERE o.cui = $hba1c_cui
RETURN a.pmid, a.study_design, drug.name, p.n, r.effect, r.ci_low, r.ci_high, r.source_sentence
ORDER BY a.year DESC
```

### 5.4 Answer prompt skeleton

```text
You are an evidence synthesis assistant.
Use ONLY the evidence table and passages provided.
- Group findings by intervention and outcome.
- Report effect sizes with CIs where given.
- Note study design and sample size.
- Flag conflicting results.
- Cite every claim as [PMID].
- If evidence is insufficient, say so.

Question: {question}
Evidence table: {table}
Passages: {passages}
```

---

## 6. NER application

- Entity list per type (Condition, Drug, Gene, Outcome) with paper counts.
- Click entity → articles mentioning it, with highlighted sentences.
- Co-occurrence view: entities most connected to a selected entity.
- Export entities with concept IDs (CSV/JSON).

## 7. PICO application

- Grid: one row per study; columns P, I, C, O, design, n, effect, CI.
- Filters by concept (expands via hierarchy).
- Side-by-side comparison of studies sharing an outcome.
- Export for systematic review tools (CSV).
- Every cell links to its evidence sentence.

---

## 8. Evaluation

| Area | Metric | Method |
|---|---|---|
| NER | Precision / recall / F1 | Hand-label 50–100 abstracts |
| PICO | Field-level accuracy | Compare to annotated sample (EBM-NLP style) |
| Normalization | Linking accuracy | Spot-check concept IDs |
| Retrieval | Recall of relevant studies | 30–50 cross-paper questions with expected PMIDs |
| Answers | Faithfulness, citation accuracy | LLM-as-judge + manual review |
| Baseline | All of the above vs vector RAG | Same question set |

Success criterion: GraphRAG retrieves a clearly higher share of relevant studies on cross-paper questions than the vector baseline, with equal or better citation accuracy.

---

## 9. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Extraction errors drop studies | Measure recall; keep vector fallback |
| Hallucinated PICO fields | Mandatory evidence quotes, quote verification |
| Duplicate entities | Concept-ID normalization, merge step |
| Indexing cost | Domain NER models for entities; LLM only for PICO/relations; cache per PMID |
| Full-text gaps | Start with abstracts; add PMC OA full text |
| Licensing | Use open-access content; respect publisher terms |
| Graph staleness | Incremental per-article extraction; periodic community refresh |

---

## 10. Implementation roadmap

| Phase | Deliverable |
|---|---|
| 1 | Ingestion (PubMed search → abstracts + PMC OA) and vector RAG baseline with citations |
| 2 | NER + PICO extraction with schema validation; evaluation set |
| 3 | Normalization to MeSH/UMLS; load graph |
| 4 | Hybrid retriever + query router; PICO grid and NER explorer UIs |
| 5 | Community summaries for global questions |
| 6 | Evaluation against baseline; tune; incremental updates |

---

## 11. Suggested stack (starter)

- **Python**, FastAPI backend
- **Neo4j** (graph + vector index) *or* **Postgres + pgvector**
- **scispaCy** (`en_core_sci_lg` + UMLS linker) for NER/linking
- **LLM** for PICO extraction and synthesis
- **LangGraph** or **LlamaIndex** for orchestration (optional)
- **Microsoft GraphRAG** or **LightRAG** as reference implementations for community summaries
- **React** or **Streamlit** UI

## 12. Summary

GraphRAG is a strong fit because research synthesis questions need complete, normalized, cross-document evidence, which vector top-k retrieval cannot guarantee. Treat NER and PICO extraction as the graph-building layer, keep vector search for passage ranking, and benchmark against a plain RAG baseline to confirm the gain.
