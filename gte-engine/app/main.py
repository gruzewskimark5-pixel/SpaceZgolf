from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from .pipeline import UnifiedProtocolPipeline
from .schemas import RawTelemetryEvent, UnifiedCognitiveEvent
import logging

app = FastAPI(title="GTE Engine Protocol V2", version="1.0.0")

# Setup generic logging (failing securely)
logger = logging.getLogger("gte_engine")
logging.basicConfig(level=logging.INFO)

pipeline = UnifiedProtocolPipeline()

@app.post("/ingest", response_model=UnifiedCognitiveEvent)
async def ingest_telemetry(event: RawTelemetryEvent):
    """
    Ingest raw telemetry directly into the canonical processing pipeline.
    Produces a single versioned UnifiedCognitiveEvent.
    """
    try:
        canonical_event = pipeline.process_telemetry(event)

        # Here we would normally produce this to Kafka (cognitive_events_v1)
        # using the entity_id as the routing key
        logger.info(f"Processed telemetry to canonical event: {canonical_event.event_id}")

        return canonical_event
    except ValidationError as e:
        logger.error(f"Validation Error processing telemetry: {e}")
        raise HTTPException(status_code=422, detail="Invalid event schema")
    except Exception as e:
        logger.error(f"Internal Pipeline Error: {e}")
        # Fail securely: do not expose internal traces/exceptions
        raise HTTPException(status_code=500, detail="Internal server error processing event")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
