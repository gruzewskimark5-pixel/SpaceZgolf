# Digital Glass WebSocket Integration Spec

## 1. High-Level Architecture

`text
Sensors → DI Engine → Jules SDK → Event Normalizer → WS Hub → Digital Glass UI
`

- **Jules SDK:** produces fully-typed events (Telemetry/Decision/Trace/Outcome envelope).
- **Event Normalizer:** enforces schema, attaches `privacy_mode`, drops/flags invalid events.
- **WebSocket Hub:** broadcasts normalized events to all subscribed clients.
- **Digital Glass UI:** subscribes to a single stream, renders one `event_id` at a time.

## 2. Server-Side WebSocket Spec

### Endpoint
- **URL:** `wss://glass.spacezgolf.com/stream`
- **Protocol:** JSON messages, one event per frame.
- **Auth:**
  - **Header:** `Authorization: Bearer <token>`
  - Token maps to: investor / coach / internal role.

### Message Format (Server → Client)

Exactly the envelope:

```jsonc
{
  "type": "event",
  "event": {
    "event_id": "uuid",
    "timestamp": "2026-03-31T19:45:12.345Z",
    "privacy_mode": "pii_redacted", // or "public" or "internal"
    "athlete_id": "athlete_123",
    "context": {
      "hole_id": "miakka_7",
      "weather": { "wind_speed": 12, "wind_direction": 90, "temperature": 75 },
      "lie": "fairway",
      "distance_to_pin": 150
    },
    "telemetry": { ... },
    "decision": { ... },
    "trace": [ ... ],
    "outcome": { ... }
  }
}
```

Control frames:

```jsonc
{ "type": "heartbeat", "ts": "2026-03-31T19:45:13.000Z" }
{ "type": "error", "code": "unauthorized", "message": "Invalid token" }
```

## 3. Event Normalizer Contract

**Input:** Raw event from DI/Jules pipeline.
**Output:** Strict Digital Glass event.

### Responsibilities:
- Enforce required fields (`event_id`, `timestamp`, `privacy_mode`, `context.hole_id`, etc.).
- Normalize units (ms, %, degrees).
- Clamp/validate ranges.
- Drop or quarantine malformed events.
- Attach `privacy_mode` based on source + role.

### Pseudocode

```python
def normalize(raw: dict, role: str) -> dict:
    # 1. Validate required fields
    if "event_id" not in raw:
        raise ValueError("Missing event_id")

    # 2. Normalize units
    raw["telemetry"]["swing_speed"] = clamp(raw["telemetry"].get("swing_speed", 0), 0, 150)

    # 3. Apply privacy mode
    privacy_mode = determine_privacy(role)
    raw["privacy_mode"] = privacy_mode

    if privacy_mode == "pii_redacted":
        raw["athlete_id"] = hash(raw["athlete_id"])

    return raw
```

Only normalized events hit the WebSocket.

## 4. Connection Lifecycle & Reliability

### Client Behavior
- **On open:** send `{"type": "subscribe", "view": "digital_glass", "athlete_id": "...", "hole_id": "miakka_7"}`
- **On message:** update UI with latest event (keep a small buffer for prev/next).
- **On heartbeat timeout (15s):** mark connection as stale, attempt reconnect.
- **On close:** exponential backoff reconnect (1s, 2s, 4s, 8s…).

### Server Behavior
- Send heartbeat every 5s.
- Drop idle connections after 3 missed heartbeats.
- Enforce max connections per token.

## 5. Minimal Production Checklist

- [ ] Auth enforced on WS connect
- [ ] Normalizer validates every event against schema
- [ ] `privacy_mode` applied per event
- [ ] Heartbeat + reconnect implemented
- [ ] Backpressure handled (drop oldest, not newest, if needed)
- [ ] Logs + traces for: connect, subscribe, broadcast, error
