import asyncio
import json
import logging
import nats
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
import os
import hmac
from fastapi.responses import HTMLResponse
import uvicorn
from pydantic import BaseModel


app = FastAPI()

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' ws: wss:;"
    return response


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NATS Configuration
NATS_URL = "nats://localhost:4222"

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Iterate over a copy of the list to safely remove disconnected clients
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send to websocket: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

# Global state for chaos controls
chaos_config = {
    "drop_rate": 0.0,
    "latency_multiplier": 1.0,
    "force_low_salience": False
}


class ChaosConfigUpdate(BaseModel):
    drop_rate: float
    latency_multiplier: float
    force_low_salience: bool

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    expected_key = os.getenv("SIMULATOR_API_KEY")
    if not expected_key:
        logger.error("SIMULATOR_API_KEY environment variable is not set. API is unsecured.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server configuration error")

    if not api_key or not hmac.compare_digest(api_key.encode('utf-8'), expected_key.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing API Key")
    return api_key

@app.post("/api/chaos", dependencies=[Depends(verify_api_key)])
async def update_chaos(config: ChaosConfigUpdate):
    global chaos_config
    chaos_config["drop_rate"] = max(0.0, min(1.0, config.drop_rate))
    chaos_config["latency_multiplier"] = max(0.1, config.latency_multiplier)
    chaos_config["force_low_salience"] = config.force_low_salience
    logger.info(f"Chaos config updated: {chaos_config}")

    # Broadcast chaos state update to all clients
    await manager.broadcast(json.dumps({
        "type": "chaos_state",
        "data": chaos_config
    }))
    return chaos_config

@app.get("/api/chaos")
async def get_chaos():
    return chaos_config

async def nats_listener():
    """Listens to NATS JetStream subjects and broadcasts to WebSockets."""
    while True:
        try:
            logger.info(f"Attempting to connect to NATS at {NATS_URL}...")
            nc = await nats.connect(NATS_URL, max_reconnect_attempts=-1, reconnect_time_wait=2)
            logger.info("Connected to NATS")
            js = nc.jetstream()

            # Listen to Events
            async def event_cb(msg):
                try:
                    data = json.loads(msg.data.decode())

                    # Apply Chaos: Drop events
                    if random.random() < chaos_config["drop_rate"]:
                        logger.info(f"Chaos: Dropped event {data.get('event_id')}")
                        await msg.ack()
                        return

                    # Apply Chaos: Force low salience
                    if chaos_config["force_low_salience"]:
                        data['salience'] = {
                            "narrative": 0.1, "visual": 0.1, "audio": 0.1, "game_state": 0.1
                        }

                    payload = json.dumps({"type": "event", "data": data})
                    await manager.broadcast(payload)
                    await msg.ack()
                except Exception as e:
                     logger.error(f"Error parsing event msg: {e}")

            # Listen to Feedback
            async def feedback_cb(msg):
                 try:
                      data = json.loads(msg.data.decode())

                      # Apply Chaos: Inject Latency
                      data['latency_ms'] = int(data['latency_ms'] * chaos_config["latency_multiplier"])

                      payload = json.dumps({"type": "feedback", "data": data})
                      await manager.broadcast(payload)
                      await msg.ack()
                 except Exception as e:
                      logger.error(f"Error parsing feedback msg: {e}")


            # Try to subscribe, wait and retry if stream doesn't exist yet
            while True:
                try:
                    await js.subscribe("spacez.events.detected", cb=event_cb, stream="EVENTS")
                    await js.subscribe("spacez.feedback.events", cb=feedback_cb, stream="FEEDBACK")
                    logger.info("Subscribed to EVENTS and FEEDBACK streams")
                    break
                except nats.js.errors.NotFoundError:
                    logger.warning("NATS streams not found yet, retrying in 5 seconds...")
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"Failed to subscribe to streams: {e}")
                    await asyncio.sleep(5)

            # Keep connection alive monitoring
            while True:
                if nc.is_closed:
                    logger.warning("NATS connection closed, breaking loop to reconnect")
                    break
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"NATS listener error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        finally:
             if 'nc' in locals() and not nc.is_closed:
                 await nc.close()

@app.on_event("startup")
async def startup_event():
    # Start the NATS listener background task
    asyncio.create_task(nats_listener())

html = """
<!DOCTYPE html>
<html>
<head>
    <title>SpaceZ v2 Live Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #121212; color: #e0e0e0; margin: 0; padding: 20px; }
        h1 { color: #bb86fc; text-align: center; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #888; margin-bottom: 20px; }
        .container { display: flex; gap: 20px; max-width: 1600px; margin: 0 auto; }
        .column { flex: 1; background: #1e1e1e; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); display: flex; flex-direction: column; }
        .column h2 { margin-top: 0; color: #03dac6; border-bottom: 1px solid #333; padding-bottom: 10px; }
        .card { background: #2d2d2d; padding: 15px; margin-bottom: 15px; border-radius: 6px; border-left: 4px solid #bb86fc; transition: all 0.3s ease; }
        .card.high-salience { border-left-color: #ff0266; box-shadow: 0 0 10px rgba(255, 2, 102, 0.2); }
        .card.feedback { border-left-color: #03dac6; }
        .meta { font-size: 0.8em; color: #888; margin-bottom: 5px; }
        .title { font-weight: bold; font-size: 1.1em; margin-bottom: 8px; }
        .salience-bar-container { background: #444; height: 6px; border-radius: 3px; margin: 4px 0; overflow: hidden; }
        .salience-bar { height: 100%; background: #03dac6; transition: width 0.3s ease; }
        .salience-label { display: flex; justify-content: space-between; font-size: 0.8em; color: #aaa; }
        #health-score { font-size: 3.5em; font-weight: bold; color: #03dac6; text-align: center; margin: 20px 0; text-shadow: 0 0 10px rgba(3, 218, 198, 0.3); }
        .feed-container { flex: 1; overflow-y: auto; padding-right: 5px; }

        /* Chaos Controls */
        .chaos-panel { background: #2a1b38; padding: 15px; border-radius: 8px; border: 1px solid #bb86fc; margin-bottom: 20px; }
        .chaos-panel h3 { color: #ff5252; margin-top: 0; display: flex; align-items: center; gap: 10px; }
        .chaos-control { margin-bottom: 15px; }
        .chaos-control label { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.9em; }
        .chaos-control input[type=range] { width: 100%; accent-color: #ff5252; }
        .chaos-control input[type=checkbox] { accent-color: #ff5252; transform: scale(1.2); }

        /* Custom scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #1e1e1e; border-radius: 4px; }
        ::-webkit-scrollbar-thumb { background: #444; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #555; }
    </style>
</head>
<body>
    <h1>SpaceZ v2 Autonomous Dashboard</h1>
    <div class="subtitle">Live Simulation Harness</div>

    <div class="container">
        <!-- Chaos & Status Column -->
        <div class="column" style="flex: 0.8;">
            <h2>System Control</h2>

            <div class="chaos-panel">
                <h3>⚠️ Chaos Engineering</h3>


                <div class="chaos-control">
                    <label>
                        <span>API Key</span>
                    </label>
                    <input type="password" id="api-key" placeholder="Enter API Key">
                </div>
                <div class="chaos-control">
                    <label>
                        <span>Event Drop Rate (Packet Loss)</span>
                        <span id="drop-rate-val">0%</span>
                    </label>
                    <input type="range" id="drop-rate" min="0" max="100" value="0" onchange="updateChaos()">
                </div>

                <div class="chaos-control">
                    <label>
                        <span>Feedback Latency Multiplier</span>
                        <span id="latency-val">1.0x</span>
                    </label>
                    <input type="range" id="latency-mult" min="10" max="500" value="100" onchange="updateChaos()">
                </div>

                <div class="chaos-control" style="display: flex; align-items: center; gap: 10px; margin-top: 10px;">
                    <input type="checkbox" id="force-low" onchange="updateChaos()">
                    <label for="force-low" style="margin: 0;">Force Low Salience (Boring Match)</label>
                </div>
            </div>

            <div style="text-align: center; margin-top: 20px;">
                <p>Overall Broadcast Health</p>
                <div id="health-score">--</div>
            </div>

            <h3 style="margin-top: 30px;">Latest Director Decision</h3>
            <div id="latest-decision" class="card high-salience">Waiting for events...</div>

            <h3>Commentary Generation</h3>
            <div id="latest-commentary" class="card" style="border-left-color: #ff9800; font-style: italic;">...</div>
        </div>

        <!-- Event Stream Column -->
        <div class="column">
            <h2>Live Event Firehose</h2>
            <div class="feed-container" id="events-feed"></div>
        </div>

        <!-- Feedback Loop Column -->
        <div class="column">
            <h2>Real-time Feedback Loop</h2>
            <div class="feed-container" id="feedback-feed"></div>
        </div>
    </div>

    <script>
        const eventsFeed = document.getElementById('events-feed');
        const feedbackFeed = document.getElementById('feedback-feed');
        const latestDecision = document.getElementById('latest-decision');
        const latestCommentary = document.getElementById('latest-commentary');
        const healthScoreEl = document.getElementById('health-score');

        // Security: Escape HTML to prevent XSS
        function escapeHTML(str) {
            if (str === null || str === undefined) return '';
            return String(str)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        // Chaos inputs
        const dropRateInput = document.getElementById('drop-rate');
        const latencyInput = document.getElementById('latency-mult');
        const forceLowInput = document.getElementById('force-low');
        const dropRateVal = document.getElementById('drop-rate-val');
        const latencyVal = document.getElementById('latency-val');

        // Initial setup for range displays
        dropRateInput.oninput = () => { dropRateVal.innerText = dropRateInput.value + '%'; };
        latencyInput.oninput = () => { latencyVal.innerText = (latencyInput.value / 100).toFixed(1) + 'x'; };

        function updateChaos() {
            const config = {
                drop_rate: parseInt(dropRateInput.value) / 100.0,
                latency_multiplier: parseInt(latencyInput.value) / 100.0,
                force_low_salience: forceLowInput.checked
            };

            const apiKey = document.getElementById('api-key').value;
            fetch('/api/chaos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': apiKey
                },
                body: JSON.stringify(config)
            }).catch(err => console.error("Error updating chaos config", err));
        }

        // Fetch initial chaos config
        fetch('/api/chaos')
            .then(res => res.json())
            .then(data => {
                dropRateInput.value = data.drop_rate * 100;
                dropRateVal.innerText = dropRateInput.value + '%';

                latencyInput.value = data.latency_multiplier * 100;
                latencyVal.innerText = (latencyInput.value / 100).toFixed(1) + 'x';

                forceLowInput.checked = data.force_low_salience;
            });

        // Simple state for health score
        let recentEngagement = [];
        let avgEngagement = 0.5;

        // Determine protocol based on window location
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        let ws;

        function connect() {
            ws = new WebSocket(wsUrl);

            ws.onopen = function() {
                console.log("WebSocket connection established");
            };

            ws.onmessage = function(event) {
                const msg = JSON.parse(event.data);

                if (msg.type === 'event') {
                    handleEvent(msg.data);
                } else if (msg.type === 'feedback') {
                    handleFeedback(msg.data);
                } else if (msg.type === 'chaos_state') {
                    // Sync inputs if updated from another client
                    dropRateInput.value = msg.data.drop_rate * 100;
                    dropRateVal.innerText = dropRateInput.value + '%';
                    latencyInput.value = msg.data.latency_multiplier * 100;
                    latencyVal.innerText = (latencyInput.value / 100).toFixed(1) + 'x';
                    forceLowInput.checked = msg.data.force_low_salience;
                }
            };

            ws.onclose = function(e) {
                console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
                setTimeout(function() {
                    connect();
                }, 1000);
            };

            ws.onerror = function(err) {
                console.error('Socket encountered error: ', err.message, 'Closing socket');
                ws.close();
            };
        }

        connect();

        function createSalienceBar(label, value) {
            return `
                <div class="salience-label"><span>${label}</span><span>${(value*100).toFixed(0)}%</span></div>
                <div class="salience-bar-container">
                    <div class="salience-bar" style="width: ${value * 100}%; background: ${value > 0.8 ? '#ff0266' : '#03dac6'}"></div>
                </div>
            `;
        }

        function handleEvent(data) {
            const el = document.createElement('div');

            // Calculate avg salience for styling
            const s = data.salience;
            const avgSal = (s.narrative + s.visual + s.audio + s.game_state) / 4;
            const isHighSalience = avgSal > 0.65;

            el.className = `card ${isHighSalience ? 'high-salience' : ''}`;

            let timeString = new Date(data.timestamp).toLocaleTimeString();

            el.innerHTML = `
                <div class="meta">${escapeHTML(timeString)} | ID: ${escapeHTML(data.event_id)} | Type: ${escapeHTML(data.event_type)}</div>
                <div class="title">${escapeHTML(data.description)}</div>
                ${createSalienceBar('Narrative', s.narrative)}
                ${createSalienceBar('Visual', s.visual)}
                ${createSalienceBar('Audio', s.audio)}
                ${createSalienceBar('Game State', s.game_state)}
            `;

            // Prepend to top
            eventsFeed.insertBefore(el, eventsFeed.firstChild);

            // Keep only last 50
            if (eventsFeed.children.length > 50) {
                eventsFeed.removeChild(eventsFeed.lastChild);
            }

            // Simulate Director Decision based on high salience
            if (isHighSalience) {
                latestDecision.innerHTML = `
                    <div class="meta">Triggered by: ${escapeHTML(data.event_id)}</div>
                    <div class="title">Action: ASSEMBLE_HIGHLIGHT_CLIP</div>
                    <div>Confidence: ${(avgSal * 100).toFixed(1)}%</div>
                    <div style="color: #aaa; font-size: 0.85em; margin-top: 5px;">
                        Queueing FFmpeg process... (Est pre-roll: 4s)
                    </div>
                `;

                // Simulate Commentary
                const phrases = [
                    "Absolutely devastating play right there!",
                    "They had no idea what hit them.",
                    "The spatial awareness on display is unbelievable.",
                    "That rotation just won them the game.",
                    "A textbook execution of a third party.",
                    "The mechanics are off the charts right now."
                ];
                latestCommentary.innerHTML = `"${phrases[Math.floor(Math.random() * phrases.length)]}" <br/><span class="meta">Persona: Analytical Hype</span>`;
            }
        }

        function handleFeedback(data) {
            const el = document.createElement('div');
            el.className = 'card feedback';

            let timeString = new Date(data.timestamp).toLocaleTimeString();
            let retColor = data.retention_delta > 0 ? '#4caf50' : '#f44336';

            el.innerHTML = `
                <div class="meta">${escapeHTML(timeString)} | Ref: ${escapeHTML(data.event_id)}</div>
                <div class="title">Engagement Score: ${(data.engagement_score * 100).toFixed(1)}</div>
                <div>Retention Delta: <span style="color: ${retColor}">${(data.retention_delta > 0 ? '+' : '')}${(data.retention_delta * 100).toFixed(2)}%</span></div>
                <div class="meta" style="margin-top: 5px;">Latency: <span style="${data.latency_ms > 200 ? 'color: #ff5252; font-weight: bold;' : ''}">${escapeHTML(data.latency_ms)}ms</span></div>
            `;

            feedbackFeed.insertBefore(el, feedbackFeed.firstChild);

            if (feedbackFeed.children.length > 50) {
                feedbackFeed.removeChild(feedbackFeed.lastChild);
            }

            // Update Health Score
            recentEngagement.push(data.engagement_score);
            if (recentEngagement.length > 20) recentEngagement.shift();

            avgEngagement = recentEngagement.reduce((a, b) => a + b, 0) / recentEngagement.length;

            // Map 0-1 to 0-100 score
            const displayScore = Math.round(avgEngagement * 100);
            healthScoreEl.innerText = displayScore;

            // Color based on health
            if (displayScore > 80) healthScoreEl.style.color = '#03dac6'; // Good
            else if (displayScore > 50) healthScoreEl.style.color = '#ff9800'; // Warning
            else healthScoreEl.style.color = '#ff0266'; // Danger
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
