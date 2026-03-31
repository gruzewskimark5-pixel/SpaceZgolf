import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, AsyncGenerator
from .overlay_models import RivalryEvent, RhiSnapshot, Context
from .overlay_engine import OverlayEngine

app = FastAPI()
engine = OverlayEngine()
subscribers: List[WebSocket] = []
sub_lock = asyncio.Lock()

# --- Mock Handlers for Stream Consumption ---
async def get_rhi_snapshot(event: RivalryEvent) -> RhiSnapshot:
    # Mocks cache retrieval
    return RhiSnapshot(rhi=0.8, momentum=0.2, confidence=0.9, volatility=0.3, priority=0.8)

async def get_context(event: RivalryEvent) -> Context:
    # Mocks live context
    return Context(hole_di=0.7, proximity=0.6, event_boost=0.5)

class RivalryConsumer:
    """Mock asynchronous generator yielding events"""
    async def __aiter__(self):
        while True:
            await asyncio.sleep(2)
            yield RivalryEvent(
                source_event_id="test",
                player_a_id="A",
                player_b_id="B",
                round_id="R1",
                hole_number=18,
                di=0.8,
                event_type="LEAD_CHANGE",
                event_ts=1000.0
            )

# --- Service Layer ---
@app.websocket("/overlay/stream")
async def overlay_stream(ws: WebSocket):
    await ws.accept()
    async with sub_lock:
        subscribers.append(ws)
    try:
        while True:
            await asyncio.sleep(10) # Keep-alive
    except WebSocketDisconnect:
        async with sub_lock:
            if ws in subscribers:
                subscribers.remove(ws)

async def safe_send(ws: WebSocket, msg: dict) -> bool:
    try:
        await asyncio.wait_for(ws.send_json(msg), timeout=0.5)
        return True
    except Exception:
        return False

async def broadcast(overlays: list):
    msg = {
        "type": "OVERLAY_RENDER",
        "overlays": [o.model_dump() for o in overlays],
    }

    async with sub_lock:
        results = await asyncio.gather(*[safe_send(ws, msg) for ws in subscribers])
        # Re-assign healthy subscribers
        subscribers[:] = [ws for ws, ok in zip(subscribers, results) if ok]

async def handle_event(event: RivalryEvent):
    rhi = await get_rhi_snapshot(event)
    ctx = await get_context(event)

    overlays = engine.build_overlays(event, rhi, ctx)
    if overlays:
        await broadcast(overlays)

async def run_overlay_loop():
    consumer = RivalryConsumer()
    async for event in consumer:
        # Don't block ingestion
        asyncio.create_task(handle_event(event))

@app.on_event("startup")
async def startup():
    asyncio.create_task(run_overlay_loop())
