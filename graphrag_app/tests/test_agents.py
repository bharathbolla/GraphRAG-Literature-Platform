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

def test_open_domain_generalizability():
    """Verifies that the entire pipeline generalizes to arbitrary non-cardiorenal drugs and conditions."""
    from models.article import Article, SectionChunk
    from models.entity import EntityType

    # 1. Unseen Oncology Article (Pembrolizumab in Advanced Melanoma)
    novel_art = Article(
        pmid="25891178",
        title="Pembrolizumab versus Ipilimumab in Patients with Advanced Melanoma",
        journal="N Engl J Med",
        year=2015,
        authors="Robert C, Schachter J, Long GV, et al.",
        study_design="Phase 3 Randomized Controlled Trial",
        sample_size=834,
        abstract=(
            "BACKGROUND: The immune checkpoint inhibitor pembrolizumab has shown antitumor activity in advanced melanoma.\n"
            "METHODS: We conducted a randomized, controlled, phase 3 study comparing pembrolizumab with ipilimumab in 834 patients.\n"
            "RESULTS: Progression-free survival was significantly longer with pembrolizumab than with ipilimumab "
            "(hazard ratio, 0.58; 95% confidence interval [CI], 0.46 to 0.72; P<0.001).\n"
            "CONCLUSIONS: Pembrolizumab prolonged progression-free survival."
        ),
        section_chunks=[
            SectionChunk(section_name="BACKGROUND", content="The immune checkpoint inhibitor pembrolizumab has shown antitumor activity in advanced melanoma."),
            SectionChunk(section_name="METHODS", content="We conducted a randomized, controlled, phase 3 study comparing pembrolizumab with ipilimumab in 834 patients."),
            SectionChunk(section_name="RESULTS", content="Progression-free survival was significantly longer with pembrolizumab than with ipilimumab (hazard ratio, 0.58; 95% confidence interval [CI], 0.46 to 0.72; P<0.001)."),
            SectionChunk(section_name="CONCLUSIONS", content="Pembrolizumab prolonged progression-free survival.")
        ]
    )

    # 2. Test ExtractionGuardAgent Generalizability
    extractor = ExtractionGuardAgent()
    pico = extractor.extract_and_verify(novel_art)
    novel_art.pico = pico

    assert pico is not None
    assert "Melanoma" in pico.population.condition
    assert "CKD" not in pico.population.condition
    assert "Pembrolizumab" in pico.interventions[0].name
    assert "Empagliflozin" not in pico.interventions[0].name
    assert pico.outcomes[0].effect == "0.58"
    assert pico.outcomes[0].ci_low == "0.46"
    assert pico.outcomes[0].ci_high == "0.72"

    # 3. Test OntologyAgent Generalizability on Novel Entity
    ont_agent = OntologyAgent()
    novel_entities = ont_agent.normalize_article_entities(novel_art)
    novel_art.entities = novel_entities
    
    assert len(novel_entities) >= 2
    ent_names = [e.name for e in novel_entities]
    assert any("Melanoma" in n for n in ent_names)
    assert any("Pembrolizumab" in n for n in ent_names)

    # Test open-domain normalization on completely arbitrary compound
    novel_comp = ont_agent.normalize_term("tirzepatide")
    assert novel_comp is not None
    assert novel_comp.type == EntityType.DRUG
    assert novel_comp.cui is not None

    # 4. Test KnowledgeGraphManager Dynamic Class Building (No SGLT2i for Pembrolizumab)
    kg = KnowledgeGraphManager()
    kg.rebuild_from_articles([novel_art])
    
    # Verify Pembrolizumab is NOT linked to SGLT2i
    edges = list(kg.graph.edges(data=True))
    assert not any(u == "drug_C3886580" and v == "class_sglt2i" for u, v, d in edges)
    # Verify Pembrolizumab is linked to an immune checkpoint or oncology class
    drug_classes = [v for u, v, d in edges if "drug_" in u and d.get("relationship") == "IS_A"]
    assert len(drug_classes) >= 1
    assert "class_sglt2i" not in drug_classes

    # 5. Test RouterAgent Dynamic Matching on Oncology Query
    vs = VectorStore()
    router = RouterAgent(kg, vs)
    intent, matched_pmids, _ = router.route_and_retrieve("Which trials evaluated progression-free survival in melanoma?", [novel_art])
    assert "25891178" in matched_pmids

