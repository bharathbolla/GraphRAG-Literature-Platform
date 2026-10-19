# GraphRAG Literature Platform (Production Architecture)

A modular, reliable, explainable, and scalable enterprise AI platform for multi-document clinical evidence synthesis, biomedical Named Entity Recognition (NER), and structured PICO grid extraction with 100% sentence-level provenance.

Directly aligned with all 15 slides of the **Novartis AI Hackathon Presentation Deck**.

---

## 🌟 Presentation Feature Alignment (15 Slides Ground Truth)

| Slide # | Presentation Feature | Implementation in `graphrag_app` |
|---|---|---|
| **Slide 01-03** | **Ingest to Graph** | Live PubMed E-Utilities integration, section-aware chunking (32 chunks), 88 KG edges, 32 normalized entities, 8 Leiden communities, and instant live ingestion banner. |
| **Slide 04-05, 14-15** | **Multi-Document Literature Chat & Synthesis** | `Auto Route (Hybrid)`, 4 query suggestion chips, intent badge (`graph_entity`), and **Tri-View Answer Card** with `Synthesis Answer`, `Evidence Table (14)`, and `Citations (7)`. |
| **Slide 06, 10-12** | **Biomedical NER & Concept Explorer** | Category filters (Conditions, Drugs, Outcomes), concept search, UMLS CUI mapping, **Entity Co-occurrence Graph Connections**, **Source Mentions & Sentences** with highlighted text spans, and `Export Concept IDs (JSON)`. |
| **Slide 07** | **Structured PICO Evidence Extraction Grid** | 10-column systematic review evidence matrix, drug & outcome filters, and RFC 4180 compliant `Export Systematic Review (CSV)`. |
| **Slide 08-09, 13** | **Interactive Knowledge Graph (KG Explorer)** | Vis-Network force-directed graph with `Entity Type` vs `Community Clusters` toggle, `Hide Chunks` toggle, `Freeze Layout` button, and bottom filter checkboxes. |

---

## 🏛️ Architecture Overview

The system is organized into decoupled architectural tiers adhering to standard enterprise software engineering principles:

```
graphrag_app/
├── config.py                     # Central environment & runtime configuration
├── main.py                       # Production FastAPI ASGI entrypoint
├── models/                       # Strongly-typed Pydantic schemas
│   ├── pico.py                   # Population, Intervention, Comparator, ClinicalOutcome, PICOData
│   ├── entity.py                 # BiomedicalEntity, EntityType
│   ├── article.py                # Article, SectionChunk, IngestRequest, ArticleStats
│   ├── chat.py                   # ChatRequest, ChatResponse, EvidenceRow, CitationCard, AuditReport
│   └── graph.py                  # GraphNode, GraphEdge, GraphDataResponse
├── database/                     # In-memory graph & vector storage layer
│   ├── benchmark_data.py         # 7 Landmark Phase 3 cardiorenal trials with verbatim quotes
│   ├── knowledge_graph.py        # NetworkX directed graph engine with chunks & community clusters
│   └── vector_store.py           # In-memory passage chunking and cosine ranking
├── agents/                       # The 5 Autonomous Micro-Agents
│   ├── ingestion_agent.py        # Agent 1: Ingestion & Document Decomposition
│   ├── extraction_guard_agent.py # Agent 2: PICO Extraction with Verbatim String Guard
│   ├── ontology_agent.py         # Agent 3: Biomedical Ontology Normalizer & UMLS CUI Linker
│   ├── router_agent.py           # Agent 4: Hybrid Router & Pathfinding Engine
│   └── synthesis_audit_agent.py  # Agent 5: Evidence Synthesis & NLI Entailment Audit
├── api/                          # Modular FastAPI route controllers
│   ├── routes_corpus.py          # /api/stats, /api/articles, /api/articles/ingest, /api/benchmark/reset
│   ├── routes_chat.py            # /api/chat (Hybrid Multi-Doc Clinical QA with tri-view response)
│   ├── routes_ner.py             # /api/ner, /api/ner/{name}/cooccurrences, /api/ner/{name}/mentions, export JSON
│   ├── routes_pico.py            # /api/pico, /api/export/pico.csv
│   └── routes_graph.py           # /api/graph (Vis-Network payload with community clusters & chunks)
├── static/                       # Production Single-Page Application (SPA)
│   ├── index.html                # 5-Tab responsive interface with complete slide fidelity
│   ├── css/style.css             # Custom dark theme & styling
│   └── js/app.js                 # Client controller with sub-tabs, NER inspector, & graph controls
├── tests/                        # Comprehensive unit & integration test suite (15 tests)
│   ├── test_agents.py            # Unit tests for the 5 micro-agents
│   └── test_api.py               # Integration tests for all REST endpoints
├── Dockerfile                    # Multi-stage production container definition
├── requirements.txt              # Python dependencies
├── deploy.sh                     # Linux/macOS deployment script
└── deploy.ps1                    # Windows PowerShell deployment script
```

---

## 🧪 Automated Testing

Run the test suite directly from the `graphrag_app` directory:

```powershell
# From project root:
cd graphrag_app
python -m pytest tests/
```

All 15 agent unit tests and API route integration tests will execute and validate:
* Schema compliance and section-chunk parsing
* Verbatim String Guard verification
* UMLS CUI synonym normalization
* Intent classification and hybrid routing
* Citation entailment scores (>0.85)
* Graph node/edge serialization with community clusters
* NER co-occurrences and source mentions with verbatim sentences
* Live PubMed ingestion and benchmark reset

---

## ⚡ Local Development

```powershell
cd "h:\Novartis AI Hackathon\graphrag_app"
pip install -r requirements.txt
python main.py
```
* Web Application: **`http://localhost:8080`**
* OpenAPI / Swagger Documentation: **`http://localhost:8080/docs`**

---

## ☁️ Google Cloud Run Deployment

Deploy globally in under 3 minutes with zero-ops scalability:

```powershell
# Windows PowerShell:
.\deploy.ps1 -ProjectId "[YOUR_PROJECT_ID]" -Region "us-central1"

# Linux / macOS / Cloud Shell:
./deploy.sh [YOUR_PROJECT_ID] us-central1
```

---

## 📄 Complete Technical Specification & HLD Document

A comprehensive 10-section Word document detailing the complete project, architecture, agentic AI strategy, technology justification, Google Cloud deployment, and feature specifications is generated at:
* [`GraphRAG_Literature_Platform_Technical_Architecture_and_HLD_v2.docx`](file:///h:/Novartis%20AI%20Hackathon/GraphRAG_Literature_Platform_Technical_Architecture_and_HLD_v2.docx)
