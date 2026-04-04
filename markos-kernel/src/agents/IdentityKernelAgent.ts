import {
  IAgent,
  AgentContext,
  MessageEnvelope,
  IIdentityKernel,
  IdentityAnchor,
  DriftReport,
  CalibrationEvent,
  IDriftEvaluator
} from '../types';

export class IdentityKernelAgent implements IAgent, IIdentityKernel {
  private anchors: Map<string, IdentityAnchor> = new Map();
  private evaluators: Map<string, IDriftEvaluator[]> = new Map();
  private driftHistory: Map<string, DriftReport[]> = new Map();
  private calibrationLog: CalibrationEvent[] = [];

  public driftThreshold: number = 0.5;

  constructor() {
    this.initDefaultAnchors();
  }

  private initDefaultAnchors() {
    const defaultAnchors: IdentityAnchor[] = [
      { id: 'no-fluff', description: 'No fluff — every token carries signal', category: 'constraint', weight: 0.90, immutable: true },
      { id: 'binary-execution', description: 'Binary execution — ship artifacts, not interpretations', category: 'constraint', weight: 0.85, immutable: true },
      { id: 'operational-integrity', description: 'Operational integrity — never game for optics', category: 'value', weight: 0.95, immutable: true },
      { id: 'compounding-advantage', description: 'Compounding advantage — build data moats', category: 'value', weight: 0.80, immutable: true },
      { id: 'operator-voice', description: 'Operator-grade voice — no hedging', category: 'voice', weight: 0.70, immutable: true },
      { id: 'no-drift', description: 'No drift — block and recalibrate', category: 'boundary', weight: 1.00, immutable: true }
    ];

    for (const anchor of defaultAnchors) {
      this.anchors.set(anchor.id, anchor);
    }
  }

  // --- IAgent Implementation ---

  async onInit(ctx: AgentContext): Promise<void> {
    ctx.log.info("IdentityKernelAgent initializing. Loading immutable anchors.");
    await ctx.setState('anchorsLoaded', true);
  }

  async onActivate(ctx: AgentContext): Promise<void> {
    ctx.log.info("IdentityKernelAgent active. Identity enforcement online.");
  }

  async onSuspend(ctx: AgentContext): Promise<void> {
    ctx.log.info("IdentityKernelAgent suspended.");
  }

  async onResume(ctx: AgentContext): Promise<void> {
    ctx.log.info("IdentityKernelAgent resumed.");
  }

  async onDrain(ctx: AgentContext): Promise<void> {
    ctx.log.info("IdentityKernelAgent draining in-flight evaluations.");
  }

  async onTerminate(ctx: AgentContext): Promise<void> {
    ctx.log.info("IdentityKernelAgent terminated.");
  }

  async onMessage(ctx: AgentContext, envelope: MessageEnvelope): Promise<void> {
    ctx.log.debug(`Received message on ${envelope.topic}`);
    if (envelope.topic === 'identity.validate') {
       // Typically handled via request/response or direct context invocation
       ctx.log.info(`Validating output for ${envelope.source}`);
    }
  }

  async healthCheck(): Promise<boolean> {
    return true;
  }

  // --- IIdentityKernel Implementation ---

  getAnchors(): IdentityAnchor[] {
    return Array.from(this.anchors.values());
  }

  async addAnchor(anchor: IdentityAnchor): Promise<void> {
    if (this.anchors.has(anchor.id)) {
      throw new Error(`Anchor ${anchor.id} already exists.`);
    }
    this.anchors.set(anchor.id, anchor);
  }

  async updateAnchor(id: string, update: Partial<IdentityAnchor>): Promise<void> {
    const anchor = this.anchors.get(id);
    if (!anchor) throw new Error(`Anchor ${id} not found.`);
    if (anchor.immutable) throw new Error(`Anchor ${id} is immutable and cannot be modified.`);

    this.anchors.set(id, { ...anchor, ...update });
  }

  async validate(agentId: string, output: any): Promise<DriftReport> {
    const violations: DriftReport['violations'] = [];
    let totalScore = 0;
    let totalWeight = 0;

    for (const anchor of this.anchors.values()) {
       const categoryEvaluators = this.evaluators.get(anchor.category) || [];
       totalWeight += anchor.weight;

       for (const evaluator of categoryEvaluators) {
          const result = await evaluator.evaluate(anchor, output);
          if (result.severity) {
             violations.push({
                anchorId: anchor.id,
                severity: result.severity,
                description: result.description || `Violation of anchor ${anchor.id}`
             });

             // Calculate penalty
             let penaltyMultiplier = 0;
             if (result.severity === 'critical') penaltyMultiplier = 1.0;
             else if (result.severity === 'violation') penaltyMultiplier = 0.7;
             else if (result.severity === 'warning') penaltyMultiplier = 0.3;

             totalScore += anchor.weight * penaltyMultiplier;
          }
       }
    }

    // Normalized score
    const normalizedScore = totalWeight > 0 ? (totalScore / totalWeight) : 0;
    const passed = normalizedScore <= this.driftThreshold;

    const report: DriftReport = {
       score: normalizedScore,
       passed,
       violations
    };

    // Save history
    let history = this.driftHistory.get(agentId) || [];
    history.push(report);
    this.driftHistory.set(agentId, history);

    // Log calibration event if failed
    if (!passed) {
       this.calibrationLog.push({
          timestamp: Date.now(),
          agentId,
          report,
          action: 'blocked'
       });
    } else if (violations.length > 0) {
       this.calibrationLog.push({
          timestamp: Date.now(),
          agentId,
          report,
          action: 'warned'
       });
    }

    return report;
  }

  async getDriftHistory(agentId: string, limit?: number): Promise<DriftReport[]> {
    const history = this.driftHistory.get(agentId) || [];
    return limit ? history.slice(-limit) : history;
  }

  async getCalibrationLog(since?: number, limit?: number): Promise<CalibrationEvent[]> {
    let logs = this.calibrationLog;
    if (since) logs = logs.filter(l => l.timestamp >= since);
    if (limit) logs = logs.slice(-limit);
    return logs;
  }

  setDriftThreshold(n: number): void {
    this.driftThreshold = n;
  }

  registerEvaluator(category: string, evaluator: IDriftEvaluator): void {
    const evals = this.evaluators.get(category) || [];
    evals.push(evaluator);
    this.evaluators.set(category, evals);
  }
}
