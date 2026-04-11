import { WorldState } from "./types";
import { computeGravity } from "./gravity";
import { resolveCollisions } from "./collision";

// HARD-CODED FIXED TIMESTEP for deterministic physics
export const FIXED_DT = 1 / 60;
export const STANDARD_SIM_STEPS = 300;

export function step(state: WorldState, dt: number = FIXED_DT): WorldState {
  const g = computeGravity(state);

  state.ball.velocity.x += g.x * dt;
  state.ball.velocity.y += g.y * dt;

  state.ball.position.x += state.ball.velocity.x * dt;
  state.ball.position.y += state.ball.velocity.y * dt;

  return resolveCollisions(state);
}

export function simulate(state: WorldState, steps: number = STANDARD_SIM_STEPS, dt: number = FIXED_DT): WorldState {
  let current = structuredClone(state);

  for (let i = 0; i < steps; i++) {
    current = step(current, dt);
  }

  return current;
}
