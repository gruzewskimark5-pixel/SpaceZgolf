from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uuid
import random
import asyncio
import logging
from ..services.optimizer import GeneticOptimizer

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Simulation"])

RUNS_DB = {}

class DirectorPolicy(BaseModel):
    heat_threshold_anchor: float = 3.0
    heat_threshold_camera: float = 3.8
    chaos_velocity_threshold: float = -0.15
    ces_threshold: float = 0.9
    chaos_probability: float = 0.7

def run_simulation(policy: DirectorPolicy | dict, steps: int = 50):
    if isinstance(policy, BaseModel):
        policy_dict = policy.model_dump()
    else:
        policy_dict = policy

    events = []
    prev_heat = 2.5

    for t in range(steps):
        heat = round(prev_heat + random.uniform(-0.4, 0.5), 3)
        heat = max(1.0, min(5.0, heat))

        velocity = round(heat - prev_heat, 3)
        projected = round(heat + velocity * 1.5 + random.uniform(-0.2, 0.2), 3)

        anchor_present = random.random() > 0.6
        ces = round(random.uniform(0.5, 2.0), 3)

        actions = []

        if projected > policy_dict["heat_threshold_camera"]:
            actions.append("PRIORITIZE_CAMERA")

        if anchor_present and heat > policy_dict["heat_threshold_anchor"]:
            actions.append("ANCHOR_AMPLIFICATION")

        if velocity < policy_dict["chaos_velocity_threshold"] and random.random() < policy_dict["chaos_probability"]:
            actions.append("CHAOS_INJECTION")
            heat += 0.8

        if ces < policy_dict["ces_threshold"]:
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
    # Return limited data for list
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

        events = run_simulation(policy, steps=60)

        run_id = str(uuid.uuid4())
        RUNS_DB[run_id] = {
            "policy": policy.model_dump(),
            "events": events
        }

        await websocket.send_json({"type": "SIM_START", "run_id": run_id, "policy": policy.model_dump()})

        for event in events:
            await websocket.send_json({"type": "SIM_EVENT", "data": event})
            await asyncio.sleep(0.5)

        await websocket.send_json({"type": "SIM_COMPLETE", "run_id": run_id})

    except WebSocketDisconnect:
        logger.info("Simulation websocket disconnected")
    except Exception as e:
        logger.error(f"Error in websocket simulation: {e}")

@router.websocket("/ws/optimize")
async def websocket_optimize(websocket: WebSocket):
    await websocket.accept()

    try:
        config = await websocket.receive_json()

        # Wrapper to match GeneticOptimizer interface
        def run_sim_wrapper(policy_dict, steps=30):
            return run_simulation(policy_dict, steps)

        optimizer = GeneticOptimizer(
            run_sim_func=run_sim_wrapper,
            population_size=config.get("population_size", 20),
            generations=config.get("generations", 10),
            mutation_rate=config.get("mutation_rate", 0.1)
        )

        await websocket.send_json({"type": "OPT_START", "config": config})

        # Async callback for streaming generation progress
        async def stream_progress(gen_data):
            await websocket.send_json({"type": "OPT_PROGRESS", "data": gen_data})
            await asyncio.sleep(0.1)

        history = await optimizer.optimize(websocket_callback=stream_progress)

        best_overall = history[-1]["best_policy"]
        await websocket.send_json({"type": "OPT_COMPLETE", "best_policy": best_overall, "history": history})

    except WebSocketDisconnect:
        logger.info("Optimization websocket disconnected")
    except Exception as e:
        logger.error(f"Error in optimization simulation: {e}")
