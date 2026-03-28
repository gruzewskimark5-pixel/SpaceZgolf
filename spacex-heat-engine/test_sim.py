import asyncio
import websockets
import json

async def test_sim():
    uri = "ws://localhost:8000/ws/simulate"
    policy = {
        "heat_threshold_anchor": 3.0,
        "heat_threshold_camera": 3.8,
        "chaos_velocity_threshold": -0.15,
        "ces_threshold": 0.9,
        "chaos_probability": 0.7
    }

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(policy))

        while True:
            response = await websocket.recv()
            msg = json.loads(response)
            if msg["type"] == "SIM_START":
                print(f"Started Simulation: {msg['run_id']}")
            elif msg["type"] == "SIM_EVENT":
                event = msg["data"]
                print(f"t={event['t']} | Heat: {event['heat']} | Actions: {event['actions']}")
            elif msg["type"] == "SIM_COMPLETE":
                print(f"Completed: {msg['run_id']}")
                break

if __name__ == "__main__":
    asyncio.run(test_sim())
