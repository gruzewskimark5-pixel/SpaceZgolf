import { WorldState } from "./types";
import { computeGravity } from "./gravity";
import { resolveCollisions } from "./collision";

// HARD-CODED FIXED TIMESTEP for deterministic physics
export const FIXED_DT = 1 / 60;
export const STANDARD_SIM_STEPS = 300;

export function step(state: WorldState): WorldState {
  const g = computeGravity(state);

  state.ball.velocity.x += g.x * FIXED_DT;
  state.ball.velocity.y += g.y * FIXED_DT;

  state.ball.position.x += state.ball.velocity.x * FIXED_DT;
  state.ball.position.y += state.ball.velocity.y * FIXED_DT;

  return resolveCollisions(state);
}

export function simulate(state: WorldState, steps: number = STANDARD_SIM_STEPS): WorldState {
  let current = structuredClone(state);

  for (let i = 0; i < steps; i++) {
    current = step(current);
  }

  return current;
}
