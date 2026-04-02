import { WorldState } from "./types";
import { simulate, STANDARD_SIM_STEPS } from "./core";

export function predictTrajectory(state: WorldState, steps: number = STANDARD_SIM_STEPS) {
  const trajectory: { x: number; y: number }[] = [];
  let current = structuredClone(state);

  for (let i = 0; i < steps; i++) {
    current = simulate(current, 1);
    trajectory.push({ ...current.ball.position });
  }

  return trajectory;
}
