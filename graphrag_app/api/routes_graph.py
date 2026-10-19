from fastapi import APIRouter
from models.graph import GraphDataResponse
from state import app_state

router = APIRouter()

@router.get("/graph", response_model=GraphDataResponse)
async def get_graph():
    """Returns knowledge graph nodes and edges in Vis-Network format for interactive 2D/3D force-directed exploration."""
    return app_state.kg_manager.get_vis_network_data()
