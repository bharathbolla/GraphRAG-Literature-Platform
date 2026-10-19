from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class GraphNode(BaseModel):
    id: str
    label: str
    title: str
    group: str
    color: str
    size: int
    font: Dict[str, Any] = Field(default_factory=lambda: {"color": "#FFFFFF", "size": 12, "face": "Inter"})

class GraphEdge(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    label: str
    title: str
    arrows: str = "to"
    color: Dict[str, str] = Field(default_factory=lambda: {"color": "#64748B", "highlight": "#38BDF8"})
    font: Dict[str, Any] = Field(default_factory=lambda: {"color": "#94A3B8", "size": 9, "align": "middle"})

class GraphDataResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
