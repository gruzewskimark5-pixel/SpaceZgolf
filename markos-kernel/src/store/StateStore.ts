export class StateStore {
  private agentStates: Map<string, Map<string, any>> = new Map();
  private kernelState: Map<string, any> = new Map();

  constructor() {}

  async getState<T>(namespace: string, key: string): Promise<T | null> {
    const nsMap = this.agentStates.get(namespace);
    if (!nsMap) return null;
    const val = nsMap.get(key);
    return val !== undefined ? val as T : null;
  }

  async setState<T>(namespace: string, key: string, val: T): Promise<void> {
    let nsMap = this.agentStates.get(namespace);
    if (!nsMap) {
      nsMap = new Map();
      this.agentStates.set(namespace, nsMap);
    }
    nsMap.set(key, val);
  }

  async getKernelState<T>(key: string): Promise<T | null> {
    const val = this.kernelState.get(key);
    return val !== undefined ? val as T : null;
  }

  // For internal kernel use
  async setKernelState<T>(key: string, val: T): Promise<void> {
     this.kernelState.set(key, val);
  }
}
