import {
  IAgent,
  AgentManifest,
  AgentContext,
  AgentState,
  MessageEnvelope,
  IIdentityKernel
} from '../types';
import { StateStore } from '../store/StateStore';
import { MessageBus } from '../bus/MessageBus';

export class MarkOSKernel {
  private stateStore: StateStore;
  private messageBus: MessageBus;
  private identityKernel?: IIdentityKernel;

  private agents: Map<string, IAgent> = new Map();
  private manifests: Map<string, AgentManifest> = new Map();
  private agentStates: Map<string, AgentState> = new Map();

  constructor() {
    this.stateStore = new StateStore();
    this.messageBus = new MessageBus();
  }

  async boot(config: any): Promise<void> {
    console.log("Kernel booting...");
    // Initialize identity kernel if provided in config or later when registered
  }

  async register(manifest: AgentManifest, instance: IAgent): Promise<void> {
    if (this.agents.has(manifest.agentId)) {
      throw new Error(`Agent ${manifest.agentId} already registered.`);
    }

    // Dependency check
    for (const dep of manifest.dependencies) {
      if (!this.agents.has(dep) || this.agentStates.get(dep) !== 'READY' && this.agentStates.get(dep) !== 'ACTIVE') {
         throw new Error(`Dependency ${dep} not satisfied for agent ${manifest.agentId}`);
      }
    }

    this.agents.set(manifest.agentId, instance);
    this.manifests.set(manifest.agentId, manifest);
    this.transitionState(manifest.agentId, 'REGISTERED');

    // Wire up subscriptions
    for (const topic of manifest.subscriptions) {
      this.messageBus.subscribe(topic, async (envelope) => {
         // Only deliver if agent is ACTIVE
         if (this.agentStates.get(manifest.agentId) === 'ACTIVE') {
            const ctx = this.createAgentContext(manifest.agentId);
            await instance.onMessage(ctx, envelope);
         }
      });
    }

    // Auto-transition to READY after registration
    this.transitionState(manifest.agentId, 'INITIALIZING');
    const ctx = this.createAgentContext(manifest.agentId);
    await instance.onInit(ctx);
    this.transitionState(manifest.agentId, 'READY');
  }

  async activate(agentId: string): Promise<void> {
    const state = this.agentStates.get(agentId);
    if (state !== 'READY' && state !== 'SUSPENDED') {
      throw new Error(`Cannot activate agent in state ${state}`);
    }

    const instance = this.agents.get(agentId)!;
    const ctx = this.createAgentContext(agentId);

    if (state === 'READY') {
       await instance.onActivate(ctx);
    } else {
       await instance.onResume(ctx);
    }

    this.transitionState(agentId, 'ACTIVE');
  }

  async suspend(agentId: string): Promise<void> {
    const state = this.agentStates.get(agentId);
    if (state !== 'ACTIVE') {
      throw new Error(`Cannot suspend agent in state ${state}`);
    }

    const instance = this.agents.get(agentId)!;
    const ctx = this.createAgentContext(agentId);

    await instance.onSuspend(ctx);
    this.transitionState(agentId, 'SUSPENDED');
  }

  async shutdown(): Promise<void> {
    console.log("Kernel shutting down...");

    // Sort by tier for shutdown (ephemeral -> specialist -> core -> kernel)
    const tierOrder: Record<string, number> = {
       'ephemeral': 0,
       'specialist': 1,
       'core': 2,
       'kernel': 3
    };

    const sortedAgents = Array.from(this.manifests.values()).sort((a, b) => {
       return tierOrder[a.tier] - tierOrder[b.tier];
    });

    for (const manifest of sortedAgents) {
       const agentId = manifest.agentId;
       if (this.agentStates.get(agentId) === 'ACTIVE') {
          this.transitionState(agentId, 'DRAINING');
          const instance = this.agents.get(agentId)!;
          const ctx = this.createAgentContext(agentId);
          await instance.onDrain(ctx);
       }

       const instance = this.agents.get(agentId)!;
       const ctx = this.createAgentContext(agentId);
       await instance.onTerminate(ctx);
       this.transitionState(agentId, 'TERMINATED');
    }
  }

  private transitionState(agentId: string, newState: AgentState) {
     this.agentStates.set(agentId, newState);
     console.log(`Agent ${agentId} transitioned to ${newState}`);
  }

  setIdentityKernel(ik: IIdentityKernel) {
      this.identityKernel = ik;
  }

  private createAgentContext(agentId: string): AgentContext {
    const manifest = this.manifests.get(agentId)!;

    return {
      publish: async (topic: string, payload: any) => {
        if (!manifest.publications.includes(topic)) {
          throw new Error(`Agent ${agentId} is not authorized to publish to ${topic}`);
        }
        await this.messageBus.publish({
           id: Math.random().toString(36).substring(7),
           topic,
           source: agentId,
           payload,
           timestamp: Date.now()
        });
      },
      send: async (targetId: string, topic: string, payload: any) => {
         // Direct message routing - in a real implementation this might bypass wildcards
         await this.messageBus.publish({
           id: Math.random().toString(36).substring(7),
           topic,
           source: agentId,
           target: targetId,
           payload,
           timestamp: Date.now()
        });
      },
      request: async <T>(targetId: string, topic: string, payload: any, timeoutMs = 5000) => {
         // Placeholder for req/res implementation
         throw new Error("Not implemented");
      },
      invoke: async <T>(capabilityId: string, input: any, timeoutMs = 5000) => {
         // Placeholder for capability routing
         throw new Error("Not implemented");
      },
      getState: async <T>(key: string) => {
         return this.stateStore.getState<T>(agentId, key);
      },
      setState: async <T>(key: string, val: T) => {
         await this.stateStore.setState(agentId, key, val);
      },
      getKernelState: async <T>(key: string) => {
         return this.stateStore.getKernelState<T>(key);
      },
      validateOutput: async (output: any) => {
         if (!this.identityKernel) {
             console.warn("Identity kernel not wired, skipping validation.");
             return output;
         }
         const report = await this.identityKernel.validate(agentId, output);
         if (!report.passed) {
             throw new Error(`Output blocked due to identity drift: ${report.score} > ${this.identityKernel.driftThreshold}`);
         }
         return output;
      },
      log: {
        info: (msg: string, ...args: any[]) => console.log(`[INFO][${agentId}] ${msg}`, ...args),
        warn: (msg: string, ...args: any[]) => console.warn(`[WARN][${agentId}] ${msg}`, ...args),
        error: (msg: string, ...args: any[]) => console.error(`[ERROR][${agentId}] ${msg}`, ...args),
        debug: (msg: string, ...args: any[]) => console.debug(`[DEBUG][${agentId}] ${msg}`, ...args),
      }
    };
  }
}
