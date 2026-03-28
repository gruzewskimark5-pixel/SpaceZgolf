from fastapi import APIRouter
from typing import Dict, List
from ..markos_models import MarkOSNode, MarkOSNodeEvent

router = APIRouter(prefix="/api/v1/markos", tags=["Mark OS Golf Nodes"])

NODES: Dict[str, MarkOSNode] = {}
NODE_EVENTS: Dict[str, List[MarkOSNodeEvent]] = {}

@router.post("/ingest-node-event")
async def ingest_node_event(event: MarkOSNodeEvent):
    if event.node_id not in NODES:
        NODES[event.node_id] = MarkOSNode(
            node_id=event.node_id,
            owner=event.owner,
            type="club",
            spec={},
            metrics={},
        )

    if event.node_id not in NODE_EVENTS:
        NODE_EVENTS[event.node_id] = []

    NODE_EVENTS[event.node_id].append(event)

    # In a full system, update aggregates and mirror into DigitalTwinEvent here

    return {"status": "ok", "node_id": event.node_id}

@router.get("/nodes")
async def list_nodes():
    return list(NODES.values())

@router.get("/nodes/{node_id}/events")
async def node_events(node_id: str):
    return NODE_EVENTS.get(node_id, [])
