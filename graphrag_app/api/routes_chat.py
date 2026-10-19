from fastapi import APIRouter
from models.chat import ChatRequest, ChatResponse
from state import app_state

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_synthesize(req: ChatRequest):
    """
    Executes hybrid Agentic Retrieval & Clinical Synthesis:
    1. Agent 4 (Router): Classifies natural language query intent and retrieves relevant trials/passages.
    2. Agent 5 (Synthesis & Audit): Builds comparative PICO table, synthesizes cross-trial prose,
       constructs 3 refined prompt variants, and audits citation faithfulness via the NLI Gatekeeper Loop.
    3. History Store: Persistently records the user query and the exact documents retrieved.
    """
    # 1. Routing & Retrieval
    intent, matched_pmids, ranked_chunks = app_state.router_agent.route_and_retrieve(
        query=req.query,
        active_articles=app_state.articles
    )

    # 2. Evidence Synthesis & Gatekeeper Audit
    response = app_state.synthesis_audit_agent.synthesize(
        query=req.query,
        intent=intent,
        matched_pmids=matched_pmids,
        active_articles=app_state.articles
    )

    # 3. Save Query & Retrieved Documents to Persistent Audit History Store
    retrieved_docs = [
        art.model_dump() for art in app_state.articles if art.pmid in response.relevant_pmids
    ]
    app_state.history_store.log_query(
        query_text=req.query,
        intent=response.intent.value if hasattr(response.intent, "value") else str(response.intent),
        retrieved_articles=retrieved_docs,
        synthesis=response.synthesis,
        refined_prompts=[p.model_dump() for p in response.refined_prompts],
        audit_badge=response.audit.status_badge
    )

    return response

@router.get("/history")
async def get_audit_history():
    """Returns persistent audit logs of all user queries and document ingestions."""
    return app_state.history_store.get_full_history()

@router.delete("/history")
async def clear_audit_history():
    """Clears persistent query and ingestion audit history."""
    app_state.history_store.clear()
    return {"status": "success", "message": "Audit history successfully cleared."}
