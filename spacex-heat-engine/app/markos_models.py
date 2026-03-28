from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class MarkOSNode(BaseModel):
    node_id: str
    owner: str
    type: str  # "club" | "course" | "session"
    spec: Dict
    metrics: Dict

class MarkOSNodeEvent(BaseModel):
    node_id: str
    owner: str
    timestamp: datetime
    context: Dict
    swing: Dict
    outcome: Dict
