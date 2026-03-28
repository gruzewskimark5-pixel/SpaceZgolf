from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uuid
import random
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Simulation"])

# In-memory store for simulation runs
RUNS_DB = {}

class DirectorPolicy(BaseModel):
    heat_threshold_anchor: float = 3.0
    heat_threshold_camera: float = 3.8
    chaos_velocity_threshold: float = -0.15
    ces_threshold: float = 0.9
    chaos_probability: float = 0.7

def run_simulation(policy: DirectorPolicy, steps: int = 50):
    events = []
    prev_heat = 2.5

    for t in range(steps):
        # Base heat walks randomly but trends up slightly early on
        heat = round(prev_heat + random.uniform(-0.4, 0.5), 3)
        # Bounded between 1.0 and 5.0
        heat = max(1.0, min(5.0, heat))

        velocity = round(heat - prev_heat, 3)

        # Simulated prediction has some error
        projected = round(heat + velocity * 1.5 + random.uniform(-0.2, 0.2), 3)

        anchor_present = random.random() > 0.6
        ces = round(random.uniform(0.5, 2.0), 3)

        actions = []

        if projected > policy.heat_threshold_camera:
            actions.append("PRIORITIZE_CAMERA")

        if anchor_present and heat > policy.heat_threshold_anchor:
            actions.append("ANCHOR_AMPLIFICATION")

        if velocity < policy.chaos_velocity_threshold and random.random() < policy.chaos_probability:
            actions.append("CHAOS_INJECTION")
            # Chaos will spike the next heat value
            heat += 0.8

        if ces < policy.ces_threshold:
            actions.append("CES_OPTIMIZATION")

        events.append({
            "t": t,
            "heat": heat,
            "projected": projected,
            "velocity": velocity,
            "ces": ces,
            "anchor": anchor_present,
            "actions": actions
        })

        prev_heat = heat

    return events

@router.post("/api/v1/simulate")
def simulate_run(policy: DirectorPolicy):
    run_id = str(uuid.uuid4())
    events = run_simulation(policy)

    RUNS_DB[run_id] = {
        "policy": policy.model_dump(),
        "events": events
    }

    return {"run_id": run_id, "events_count": len(events)}

@router.get("/api/v1/runs")
def list_runs():
    return [{"run_id": rid, "policy": data["policy"]} for rid, data in RUNS_DB.items()]

@router.get("/api/v1/runs/{run_id}")
def get_run(run_id: str):
    if run_id in RUNS_DB:
        return RUNS_DB[run_id]
    return {"error": "Run not found"}

@router.websocket("/ws/simulate")
async def websocket_sim(websocket: WebSocket):
    await websocket.accept()

    try:
        policy_data = await websocket.receive_json()
        policy = DirectorPolicy(**policy_data)

        # Run a 60 step simulation
        events = run_simulation(policy, steps=60)

        run_id = str(uuid.uuid4())
        RUNS_DB[run_id] = {
            "policy": policy.model_dump(),
            "events": events
        }

        # Send initial metadata
        await websocket.send_json({"type": "SIM_START", "run_id": run_id, "policy": policy.model_dump()})

        # Stream events one by one to simulate live time
        for event in events:
            await websocket.send_json({"type": "SIM_EVENT", "data": event})
            await asyncio.sleep(0.5) # Simulate 1 frame per half second

        await websocket.send_json({"type": "SIM_COMPLETE", "run_id": run_id})

    except WebSocketDisconnect:
        logger.info("Simulation websocket disconnected")
    except Exception as e:
        logger.error(f"Error in websocket simulation: {e}")
        try:
             await websocket.close()
        except:
             pass
