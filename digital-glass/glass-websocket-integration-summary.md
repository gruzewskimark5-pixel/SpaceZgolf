# Digital Glass WebSocket Integration

This directory contains the production-ready WebSocket spec, React hook, and Python event normalizer for Digital Glass telemetry.

### Files

- **`glass-websocket-integration-summary.md`**: This summary file.
- **`frontend/glass-websocket-types.ts`**: Full TypeScript protocol definitions (messages and event schema).
- **`frontend/use-glass-stream.ts`**: React hook for WebSocket consumption with automatic reconnection and heartbeat monitoring.
- **`frontend/digital-glass-live-integration.tsx`**: Example wiring of the `useGlassStream` hook into a mock Digital Glass React component.
- **`backend/glass-websocket-server-spec.md`**: Server-side requirements and contract for WebSocket endpoint.
- **`backend/event_normalizer.py`**: Python reference implementation for validating and normalizing raw events into the `GlassEvent` schema.

### Next Steps

- **Frontend Team**: Integrate `use-glass-stream.ts` and `glass-websocket-types.ts` into the Digital Glass React application.
- **Backend Team**: Implement the WebSocket server matching the specification in `glass-websocket-server-spec.md`. The server should enforce authentication, use the event normalization logic, and manage connections.
