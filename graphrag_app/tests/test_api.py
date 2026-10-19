from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_index_route():
    r = client.get("/")
    assert r.status_code == 200
    assert "GraphRAG Literature Platform" in r.text

def test_stats_route():
    r = client.get("/api/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["total_articles"] >= 7
    assert data["total_nodes"] >= 30
    assert data["total_edges"] >= 30
    assert data["total_enrolled_patients"] > 40000

def test_articles_route():
    r = client.get("/api/articles")
    assert r.status_code == 200
    data = r.json()
    assert len(data["articles"]) >= 7

def test_pico_route():
    r = client.get("/api/pico")
    assert r.status_code == 200
    data = r.json()
    assert data["total_rows"] >= 10
    
    # Test drug filter
    r_empa = client.get("/api/pico?drug=Empagliflozin")
    assert r_empa.status_code == 200
    for row in r_empa.json()["pico_rows"]:
        assert "Empagliflozin" in row["intervention"]

def test_pico_csv_export():
    r = client.get("/api/export/pico.csv")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "PMID" in r.text
    assert "EMPA-KIDNEY" in r.text

def test_ner_routes():
    r = client.get("/api/ner")
    assert r.status_code == 200
    ents = r.json()["entities"]
    assert len(ents) >= 5
    
    # Test co-occurrences
    r_co = client.get("/api/ner/Empagliflozin/cooccurrences")
    assert r_co.status_code == 200
    assert r_co.json()["target_entity"] == "Empagliflozin"

    # Test mentions
    r_men = client.get("/api/ner/Empagliflozin/mentions")
    assert r_men.status_code == 200
    assert r_men.json()["total_mentions"] >= 1
    assert "evidence_sentence" in r_men.json()["mentions"][0]

    # Test concept JSON export
    r_exp = client.get("/api/ner/export/concepts.json")
    assert r_exp.status_code == 200
    assert "concepts" in r_exp.json()

def test_graph_route():
    r = client.get("/api/graph")
    assert r.status_code == 200
    data = r.json()
    assert len(data["nodes"]) >= 30
    assert len(data["edges"]) >= 30

def test_chat_route():
    r = client.post("/api/chat", json={"query": "Which SGLT2 inhibitor trials reported kidney disease progression in CKD?"})
    assert r.status_code == 200
    data = r.json()
    assert data["intent"] == "graph_entity"
    assert data["audit"]["audit_passed"] is True
    assert len(data["evidence_table"]) >= 3
    assert len(data["citations"]) >= 1
    assert len(data["refined_prompts"]) == 3
    assert "EMPA-KIDNEY" in data["synthesis"]

def test_ingest_route():
    r = client.post("/api/articles/ingest", json={"query_or_pmid": "36331190"})
    assert r.status_code == 200
    data = r.json()
    assert "Success" in data["message"]
    assert "suggested_next_queries" in data
    assert len(data["suggested_next_queries"]) >= 3

def test_suggest_ingestion_queries():
    # 1. Default / General Suggestions
    r_gen = client.post("/api/articles/suggest_queries", json={"query": ""})
    assert r_gen.status_code == 200
    suggestions = r_gen.json()
    assert len(suggestions) >= 3
    for s in suggestions:
        assert "strategy_label" in s
        assert "optimized_query" in s
        assert "expected_yield" in s
        assert "rationale" in s
        assert "target_drugs" in s

    # 2. Oncology / Breast Cancer Suggestions
    r_onco = client.post("/api/articles/suggest_queries", json={"query": "ribociclib breast cancer"})
    assert r_onco.status_code == 200
    onco_suggestions = r_onco.json()
    assert any("CDK4/6" in s["strategy_label"] for s in onco_suggestions)
    assert any("palbociclib" in s["optimized_query"].lower() for s in onco_suggestions)

    # 3. Heart Failure / Cardiorenal Suggestions
    r_hf = client.post("/api/articles/suggest_queries", json={"query": "sacubitril heart failure"})
    assert r_hf.status_code == 200
    hf_suggestions = r_hf.json()
    assert any("4-Pillar" in s["strategy_label"] or "Active Comparators" in s["strategy_label"] for s in hf_suggestions)

    # 4. User's exact query test (Targeted Anti-CD20 B-Cell Depletion Landscape)
    r_cd20 = client.post("/api/articles/suggest_queries", json={"query": "Targeted Anti-CD20 B-Cell Depletion Landscape"})
    assert r_cd20.status_code == 200
    cd20_suggestions = r_cd20.json()
    assert any("B-Cell" in s["strategy_label"] for s in cd20_suggestions)
    assert any("ofatumumab" in s["optimized_query"].lower() for s in cd20_suggestions)

def test_audit_history_route():
    # Chat should have logged query
    r = client.get("/api/history")
    assert r.status_code == 200
    data = r.json()
    assert data["total_queries_logged"] >= 1
    assert "queries" in data or "recent_queries" in data
    # Check that retrieved documents are saved with query
    latest_query = data["recent_queries"][0]
    assert "documents" in latest_query
    assert len(latest_query["documents"]) >= 1

def test_benchmark_reset():
    r = client.post("/api/benchmark/reset")
    assert r.status_code == 200
    assert r.json()["status"] == "success"
    assert r.json()["article_count"] == 7
