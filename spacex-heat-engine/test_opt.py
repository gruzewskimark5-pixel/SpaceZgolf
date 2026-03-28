import asyncio
import websockets
import json

async def test_opt():
    uri = "ws://localhost:8000/ws/optimize"
    config = {
        "population_size": 10,
        "generations": 5,
        "mutation_rate": 0.1
    }

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(config))

        while True:
            response = await websocket.recv()
            msg = json.loads(response)
            if msg["type"] == "OPT_START":
                print(f"Started Optimization")
            elif msg["type"] == "OPT_PROGRESS":
                data = msg["data"]
                print(f"Gen {data['generation']} | Best Fitness: {data['best_fitness']} | Avg: {data['avg_fitness']}")
            elif msg["type"] == "OPT_COMPLETE":
                print(f"Completed! Best Policy: {msg['best_policy']}")
                break

if __name__ == "__main__":
    asyncio.run(test_opt())
