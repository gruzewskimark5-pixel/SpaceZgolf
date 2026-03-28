import asyncio
import json
import random
import time
from datetime import datetime, timezone
import nats
from pydantic import BaseModel, Field

class Salience(BaseModel):
    narrative: float = Field(ge=0.0, le=1.0)
    visual: float = Field(ge=0.0, le=1.0)
    audio: float = Field(ge=0.0, le=1.0)
    game_state: float = Field(ge=0.0, le=1.0)

class DetectedEvent(BaseModel):
    event_id: str
    timestamp: str
    event_type: str
    description: str
    salience: Salience
    metadata: dict = Field(default_factory=dict)

class FeedbackEvent(BaseModel):
    event_id: str
    timestamp: str
    engagement_score: float = Field(ge=0.0, le=1.0)
    retention_delta: float = Field(ge=-1.0, le=1.0)
    latency_ms: int

# Configuration
NATS_URL = "nats://localhost:4222"
EVENT_SUBJECT = "spacez.events.detected"
FEEDBACK_SUBJECT = "spacez.feedback.events"

# Simulated event types and their base properties
EVENT_TYPES = [
    {"type": "kill", "desc": "Player {player} eliminated {target}", "base_salience": 0.6},
    {"type": "knockdown", "desc": "Player {player} knocked down {target}", "base_salience": 0.4},
    {"type": "zone_close", "desc": "Ring is closing to phase {phase}", "base_salience": 0.5},
    {"type": "celebration", "desc": "Player {player} celebrating", "base_salience": 0.3},
    {"type": "revive", "desc": "Player {player} reviving teammate", "base_salience": 0.4},
    {"type": "third_party", "desc": "Squad {squad} engaging existing fight", "base_salience": 0.8},
    {"type": "champion_eliminated", "desc": "Champion squad eliminated!", "base_salience": 0.9},
]

PLAYERS = ["ImperialHal", "Genburten", "Reps", "Sweetdreams", "Nafen", "Albralelie", "HisWattson", "Pandxrz", "Phony", "Frexs"]
SQUADS = ["TSM", "DarkZero", "NRG", "FaZe", "Optic", "XSET"]

def generate_random_event(event_id: int) -> DetectedEvent:
    event_template = random.choice(EVENT_TYPES)

    # Simulate match phases (intensity increases over time)
    # Just a simple proxy: higher event_id -> slightly higher base salience
    phase_modifier = min(0.3, (event_id % 100) / 300.0)

    # Add random jitter to salience dimensions
    base = event_template["base_salience"] + phase_modifier

    salience = Salience(
        narrative=min(1.0, max(0.0, base + random.uniform(-0.2, 0.3))),
        visual=min(1.0, max(0.0, base + random.uniform(-0.1, 0.2))),
        audio=min(1.0, max(0.0, base + random.uniform(-0.1, 0.2))),
        game_state=min(1.0, max(0.0, base + random.uniform(-0.1, 0.1)))
    )

    player1 = random.choice(PLAYERS)
    player2 = random.choice([p for p in PLAYERS if p != player1])
    squad = random.choice(SQUADS)
    phase = random.randint(1, 6)

    desc = event_template["desc"].format(player=player1, target=player2, squad=squad, phase=phase)

    metadata = {}
    if "player" in event_template["desc"]:
        metadata["player"] = player1
    if "target" in event_template["desc"]:
        metadata["target"] = player2
    if "squad" in event_template["desc"]:
        metadata["squad"] = squad
    if "phase" in event_template["desc"]:
        metadata["phase"] = phase

    # Simulate memory context
    if salience.narrative > 0.8:
         metadata["rivalry_detected"] = True

    return DetectedEvent(
        event_id=f"evt_{event_id:06d}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_type=event_template["type"],
        description=desc,
        salience=salience,
        metadata=metadata
    )

def generate_feedback(event: DetectedEvent) -> FeedbackEvent:
    # Simulate feedback based loosely on salience (good events get better feedback usually)
    avg_salience = (event.salience.narrative + event.salience.visual + event.salience.audio + event.salience.game_state) / 4.0

    # Introduce some randomness and "surprises"
    engagement = min(1.0, max(0.0, avg_salience + random.uniform(-0.2, 0.2)))

    # High engagement usually leads to positive retention delta
    retention = min(1.0, max(-1.0, (engagement - 0.5) * 0.5 + random.uniform(-0.1, 0.1)))

    # Simulate processing latency (ms) - occasional spikes
    latency = int(random.lognormvariate(4.0, 0.5)) + 20

    return FeedbackEvent(
        event_id=event.event_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        engagement_score=engagement,
        retention_delta=retention,
        latency_ms=latency
    )

async def run_simulator():
    try:
        nc = await nats.connect(NATS_URL)
        print(f"Connected to NATS at {NATS_URL}")

        js = nc.jetstream()

        # Ensure streams exist
        try:
            await js.add_stream(name="EVENTS", subjects=[EVENT_SUBJECT])
            print("Created EVENTS stream")
        except Exception as e:
             print(f"Stream EVENTS might already exist: {e}")

        try:
            await js.add_stream(name="FEEDBACK", subjects=[FEEDBACK_SUBJECT])
            print("Created FEEDBACK stream")
        except Exception as e:
             print(f"Stream FEEDBACK might already exist: {e}")


        event_counter = 1
        print("Starting Event Firehose Simulator...")

        while True:
            # 1. Generate and publish a detected event
            event = generate_random_event(event_counter)
            event_json = event.model_dump_json()

            await js.publish(EVENT_SUBJECT, event_json.encode())
            print(f"Published Event: {event.event_type} | ID: {event.event_id} | Avg Sal: {sum(event.salience.model_dump().values())/4:.2f}")

            # 2. Simulate Director Brain / System processing delay
            processing_delay = random.uniform(0.5, 2.0)
            await asyncio.sleep(processing_delay)

            # 3. Generate and publish feedback for that event
            # (In reality, feedback comes much later from broadcast telemetry, but we simulate it close for demo purposes)
            feedback = generate_feedback(event)
            feedback_json = feedback.model_dump_json()

            await js.publish(FEEDBACK_SUBJECT, feedback_json.encode())
            print(f"Published Feedback: ID: {feedback.event_id} | Eng: {feedback.engagement_score:.2f} | Latency: {feedback.latency_ms}ms")

            # 4. Wait before next event
            # Simulate bursty traffic (sometimes very fast, sometimes slow)
            if random.random() < 0.2:
                 # Burst!
                 await asyncio.sleep(random.uniform(0.1, 0.5))
            else:
                 # Normal pace
                 await asyncio.sleep(random.uniform(2.0, 5.0))

            event_counter += 1

    except Exception as e:
        print(f"Simulator error: {e}")
    finally:
        if 'nc' in locals() and nc.is_connected:
            await nc.close()
            print("Disconnected from NATS")

if __name__ == "__main__":
    asyncio.run(run_simulator())
