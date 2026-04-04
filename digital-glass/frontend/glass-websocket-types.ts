export interface Telemetry {
  hrv: number;
  focus_index: number;
  stress_index: number;
  swing_speed: number;
  club_face_angle: number;
}

export interface Decision {
  decision_id: string;
  club_selected: string;
  target_line: number;
  confidence_score: number;
  execution_complexity: number;
}

export interface Trace {
  input_variable: string;
  threshold: number;
  actual: number;
  passed: boolean;
}

export interface Outcome {
  carry_distance: number;
  fairway_hit: boolean;
  proximity_to_hole: number;
  strokes_gained: number;
}

export interface Context {
  hole_id: string;
  weather: {
    wind_speed: number;
    wind_direction: number;
    temperature: number;
  };
  lie: string;
  distance_to_pin: number;
}

export interface GlassEvent {
  event_id: string;
  timestamp: string;
  privacy_mode: 'public' | 'pii_redacted' | 'internal';
  athlete_id: string;
  context: Context;
  telemetry: Telemetry;
  decision: Decision;
  trace: Trace[];
  outcome: Outcome;
}

// Server -> Client Messages
export interface EventMessage {
  type: 'event';
  event: GlassEvent;
}

export interface HeartbeatMessage {
  type: 'heartbeat';
  ts: string;
}

export interface ErrorMessage {
  type: 'error';
  code: string;
  message: string;
}

export interface AckMessage {
  type: 'ack';
  message: string;
}

export type ServerMessage = EventMessage | HeartbeatMessage | ErrorMessage | AckMessage;

// Client -> Server Messages
export interface SubscribeMessage {
  type: 'subscribe';
  view: string;
  athlete_id?: string;
  hole_id?: string;
}

export interface UnsubscribeMessage {
  type: 'unsubscribe';
  view: string;
}

export interface PingMessage {
  type: 'ping';
  ts: string;
}

export type ClientMessage = SubscribeMessage | UnsubscribeMessage | PingMessage;
