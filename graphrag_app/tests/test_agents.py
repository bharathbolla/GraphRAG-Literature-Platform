import pytest
from agents.ingestion_agent import IngestionAgent
from agents.extraction_guard_agent import ExtractionGuardAgent
from agents.ontology_agent import OntologyAgent
from agents.router_agent import RouterAgent
from agents.synthesis_audit_agent import SynthesisAuditAgent
from database.knowledge_graph import KnowledgeGraphManager
from database.vector_store import VectorStore
from database.benchmark_data import get_benchmark_articles
from models.chat import QueryIntent

def test_ingestion_agent():
    agent = IngestionAgent()
    art = agent.ingest("36331190")
    assert art.pmid == "36331190"
    assert "BACKGROUND" in art.abstract
    assert "RESULTS" in art.abstract
    assert art.sample_size == 5200

def test_extraction_guard_string_verification():
    agent = ExtractionGuardAgent()
    source = "Progression of kidney disease occurred in 432 of 3304 patients (13.1%)."
    valid_quote = "Progression of kidney disease occurred in 432 of 3304 patients"
    hallucinated_quote = "Progression of kidney disease occurred in 890 patients"
    
    assert agent.verify_substring(valid_quote, source) is True
    assert agent.verify_substring(hallucinated_quote, source) is False

def test_ontology_agent_synonyms():
    agent = OntologyAgent()
    t2dm = agent.normalize_term("t2dm")
    assert t2dm is not None
    assert t2dm.name == "Type 2 Diabetes Mellitus"
    assert t2dm.cui == "C0011860"
    
    ckd = agent.normalize_term("chronic kidney disease")
    assert ckd is not None
    assert ckd.cui == "C0022661"
    
    empa = agent.normalize_term("Empagliflozin")
    assert empa is not None
    assert empa.rxnorm == "1545653"

def test_router_agent_intent_classification():
    kg = KnowledgeGraphManager()
    vs = VectorStore()
    router = RouterAgent(kg, vs)
    
    intent_graph = router.classify_intent("Which SGLT2 inhibitor trials reported kidney disease progression in CKD?")
    assert intent_graph == QueryIntent.GRAPH_ENTITY
    
    intent_agg = router.classify_intent("How many phase 3 RCTs tested dapagliflozin vs placebo?")
    assert intent_agg == QueryIntent.AGGREGATION
    
    intent_theme = router.classify_intent("What are the primary clinical themes across the cardiorenal corpus?")
    assert intent_theme == QueryIntent.GLOBAL_THEMATIC

def test_synthesis_audit_agent():
    agent = SynthesisAuditAgent()
    articles = get_benchmark_articles()
    res = agent.synthesize(
        query="Which SGLT2 inhibitor trials reported kidney disease progression in CKD?",
        intent=QueryIntent.GRAPH_ENTITY,
        matched_pmids={"36331190", "32970396", "30990260"},
        active_articles=articles
    )
    assert res.audit.audit_passed is True
    assert res.audit.nli_faithfulness_score >= 0.85
    assert len(res.evidence_table) >= 3
    assert any("EMPA-KIDNEY" in row.study_name for row in res.evidence_table)
    assert len(res.refined_prompts) == 3

def test_prompt_refiner_agent():
    from agents.prompt_refiner_agent import PromptRefinerAgent
    refiner = PromptRefinerAgent()
    prompts = refiner.generate_refined_prompts("compare heart failure drugs", set(), [])
    assert len(prompts) == 3
    categories = [p.category for p in prompts]
    assert "Comparative Head-to-Head" in categories
    assert "Safety & Biomarker Deep-Dive" in categories
    assert "Guideline & Class Landscape" in categories

def test_prompt_refiner_ingestion_suggestions():
    from agents.prompt_refiner_agent import PromptRefinerAgent
    refiner = PromptRefinerAgent()
    
    # 1. Cardiology
    hf_suggs = refiner.generate_ingestion_suggestions("heart failure sacubitril")
    assert len(hf_suggs) == 3
    assert any("4-Pillar" in s.strategy_label for s in hf_suggs)
    assert any("LCZ696" in s.optimized_query or "sacubitril" in s.optimized_query for s in hf_suggs)

    # 2. Oncology
    onco_suggs = refiner.generate_ingestion_suggestions("breast cancer ribociclib")
    assert len(onco_suggs) == 3
    assert any("CDK4/6" in s.strategy_label for s in onco_suggs)
    assert any("palbociclib" in s.optimized_query.lower() for s in onco_suggs)

    # 3. Immunology
    immuno_suggs = refiner.generate_ingestion_suggestions("psoriasis secukinumab")
    assert len(immuno_suggs) == 3
    assert any("Biologic" in s.strategy_label for s in immuno_suggs)

    # 4. Neuroscience / B-Cell Depletion
    ms_suggs = refiner.generate_ingestion_suggestions("multiple sclerosis ofatumumab")
    assert len(ms_suggs) == 3
    assert any("B-Cell" in s.strategy_label for s in ms_suggs)

    # 4b. Exact user query test
    cd20_suggs = refiner.generate_ingestion_suggestions("Targeted Anti-CD20 B-Cell Depletion Landscape")
    assert len(cd20_suggs) == 3
    assert any("B-Cell" in s.strategy_label for s in cd20_suggs)
    assert any("ofatumumab" in s.optimized_query.lower() for s in cd20_suggs)

    # 5. Dynamic Synthesis for Novel Query
    dyn_suggs = refiner.generate_ingestion_suggestions("semaglutide obesity")
    assert len(dyn_suggs) == 3
    assert any("Semaglutide Obesity" in s.strategy_label for s in dyn_suggs)
    assert any("semaglutide" in s.optimized_query.lower() for s in dyn_suggs)

    # 6. Fallback general when empty
    gen_suggs = refiner.generate_ingestion_suggestions("")
    assert len(gen_suggs) == 3

def test_hybrid_vector_store():
    vs = VectorStore()
    vs.add_chunk("c1", "36331190", "Background", "Chronic kidney disease affects millions worldwide.")
    vs.add_chunk("c2", "36331190", "Results", "Empagliflozin reduced the risk of kidney disease progression by 28%.")
    vs.add_chunk("c3", "32970396", "Primary Endpoint", "Dapagliflozin significantly reduced composite renal failure.")

    # Search with clinical section boost
    results = vs.search("kidney disease progression")
    assert len(results) >= 2
    # Verify results section is prioritized
    assert results[0]["section"] in ("Results", "Primary Endpoint")
    assert vs.has_dense_embeddings() is False

    # Test with dense mock embeddings (768-dim standard)
    mock_emb1 = [0.1] * 768
    mock_emb2 = [0.8] * 768
    vs.add_chunk("c4", "30990260", "Results", "Canagliflozin reduced ESRD", embedding=mock_emb2)
    assert vs.has_dense_embeddings() is True

