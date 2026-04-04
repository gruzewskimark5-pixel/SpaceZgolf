export type AgentState =
  | 'REGISTERED'
  | 'INITIALIZING'
  | 'READY'
  | 'ACTIVE'
  | 'SUSPENDED'
  | 'DRAINING'
  | 'TERMINATED'
  | 'FAULTED';

export interface MessageEnvelope {
  id: string;
  topic: string;
  source: string;
  target?: string;
  correlationId?: string;
  payload: any;
  timestamp: number;
}

export interface CapabilityDescriptor {
  id: string;
  name: string;
  inputSchema: any;
  outputSchema: any;
}

export interface ResourceLimits {
  maxMemory?: number;
  maxCpu?: number;
}

export interface AgentManifest {
  agentId: string;
  name: string;
  version: string;
  tier: 'kernel' | 'core' | 'specialist' | 'ephemeral';
  subscriptions: string[];
  publications: string[];
  dependencies: string[];
  capabilities: CapabilityDescriptor[];
  resourceLimits: ResourceLimits;
  identityConstraints: string[];
}

export interface AgentContext {
  publish(topic: string, payload: any): Promise<void>;
  send(targetId: string, topic: string, payload: any): Promise<void>;
  request<T>(targetId: string, topic: string, payload: any, timeoutMs?: number): Promise<T>;
  invoke<T>(capabilityId: string, input: any, timeoutMs?: number): Promise<T>;
  getState<T>(key: string): Promise<T | null>;
  setState<T>(key: string, val: T): Promise<void>;
  getKernelState<T>(key: string): Promise<T | null>;
  validateOutput(output: any): Promise<any>;
  log: {
    info(msg: string, ...args: any[]): void;
    warn(msg: string, ...args: any[]): void;
    error(msg: string, ...args: any[]): void;
    debug(msg: string, ...args: any[]): void;
  };
}

export interface IAgent {
  onInit(ctx: AgentContext): Promise<void>;
  onActivate(ctx: AgentContext): Promise<void>;
  onSuspend(ctx: AgentContext): Promise<void>;
  onResume(ctx: AgentContext): Promise<void>;
  onDrain(ctx: AgentContext): Promise<void>;
  onTerminate(ctx: AgentContext): Promise<void>;
  onMessage(ctx: AgentContext, envelope: MessageEnvelope): Promise<void>;
  healthCheck(): Promise<boolean>;
}

export interface IdentityAnchor {
  id: string;
  description: string;
  category: 'constraint' | 'value' | 'voice' | 'boundary';
  weight: number;
  immutable: boolean;
}

export interface DriftReport {
  score: number;
  passed: boolean;
  violations: Array<{
    anchorId: string;
    severity: 'critical' | 'violation' | 'warning';
    description: string;
  }>;
}

export interface CalibrationEvent {
  timestamp: number;
  agentId: string;
  report: DriftReport;
  action: 'blocked' | 'warned' | 'adjusted';
}

export interface IDriftEvaluator {
  evaluate(anchor: IdentityAnchor, output: any): Promise<{ severity: 'critical' | 'violation' | 'warning' | null, description?: string }>;
}

export interface IIdentityKernel {
  getAnchors(): IdentityAnchor[];
  addAnchor(anchor: IdentityAnchor): Promise<void>;
  updateAnchor(id: string, update: Partial<IdentityAnchor>): Promise<void>;
  validate(agentId: string, output: any): Promise<DriftReport>;
  getDriftHistory(agentId: string, limit?: number): Promise<DriftReport[]>;
  getCalibrationLog(since?: number, limit?: number): Promise<CalibrationEvent[]>;
  driftThreshold: number;
  setDriftThreshold(n: number): void;
  registerEvaluator(category: string, evaluator: IDriftEvaluator): void;
}
