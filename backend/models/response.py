from pydantic import BaseModel
from typing import List, Optional

class GraphNode(BaseModel):
    id: str
    label: str
    score: float

class GraphEdge(BaseModel):
    source: str
    target: str
    type: str

class GraphMeta(BaseModel):
    definition: Optional[str] = None
    etymology: Optional[str] = None
    usage: Optional[str] = None

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    meta: GraphMeta
    synonyms: Optional[List[str]] = []
    semantic: Optional[List[str]] = []
    morphological: Optional[List[str]] = []
