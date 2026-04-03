# Horizon Protocol API Contract v1.0.0

**Integrity Checksum:** (build-time SHA-256 generated here)

## REST API (Base: `/api/v1`)

### 1. Health
- `GET /health` - Service status & dependency checks (Doctrine, DB, Redis)

### 2. Auth
- `POST /auth/register`
- `POST /auth/login` - Returns JWT
- `POST /auth/refresh`
- `POST /auth/logout`

### 3. Player
- `GET /players/{id}` - Public profile view
- `GET /players/me` - Private profile view
- `PUT /players/me` - Update profile settings

### 4. Swings
- `POST /swings` - Full sensor payload submission, USIH hash computation, on-chain write

### 5. Sessions
- `POST /sessions` - Start a round/range/event
- `GET /sessions/{id}` - Session details
- `PUT /sessions/{id}/complete` - End session lifecycle

### 6. Dominance Index (DI)
- `GET /di/player/{id}` - 5-component DI query
- `GET /di/compare?p1={id1}&p2={id2}` - Player comparison

### 7. Leaderboard
- `GET /leaderboard/global` - Scoped global leaderboard (paginated)
- `GET /leaderboard/event/{id}`
- `GET /leaderboard/regional/{region}`
- `GET /leaderboard/seasonal`

### 8. Simulation
- `POST /simulation/request` - Physics engine request with trajectory + collision events

### 9. Replay Validation
- `POST /replay/validate` - Determinism check with delta reporting

### 10. Doctrine
- `POST /doctrine/reload` - Admin hot-reload
- `GET /doctrine/status` - State machine status

---

## WebSocket Protocol (Base: `/ws/v1/session`)

**Connection:** 10 conn/IP limit, 1hr idle timeout.

### Client → Kernel Messages
1. `session.start`
2. `swing.submit`
3. `swing.stream`
4. `simulation.request`
5. `heartbeat`

### Kernel → Client Messages (11 types, incl.)
1. `di.update`
2. `chain.confirmed`
3. `leaderboard.update`
4. ... (and 8 others)

### Custom Close Codes
- `4001`: Auth failure
- `4002`: Session error
- `4003`: Rate limit exceeded
- `4004`: Protocol error
- `4010`: Server shutdown

### Reconnection
- Exponential backoff
- Event replay via `seq` monotonic counter

---

*Breaking changes require version bump + bilateral compatibility test.*
