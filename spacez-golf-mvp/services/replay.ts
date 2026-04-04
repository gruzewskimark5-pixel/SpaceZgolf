import { WorldState, ShotInput } from "../engine/types";
import { simulate, STANDARD_SIM_STEPS } from "../engine/core";

// Normalizes input to deterministic bounds
function normalizeInput(input: ShotInput): ShotInput {
  return {
    angle: input.angle % (2 * Math.PI), // Keep angle within 0 to 2PI
    power: Math.max(0, Math.min(1, input.power)) // Clamp power between 0 and 1
  };
}

// We validate that the final state matches what the client says, by applying the shot and running the simulation.
export function validateReplay(
  initialState: WorldState,
  input: ShotInput,
  clientFinalState: WorldState,
  steps: number = STANDARD_SIM_STEPS
): boolean {
  // 1. Normalize input bounds
  const normalizedInput = normalizeInput(input);

  // 2. Apply input to initialState
  const stateToSim = structuredClone(initialState);

  // Apply power and angle to the velocity
  // We multiply power by an arbitrary maximum launch speed (e.g., 50)
  const MAX_LAUNCH_SPEED = 50;
  const launchSpeed = normalizedInput.power * MAX_LAUNCH_SPEED;

  stateToSim.ball.velocity = {
    x: Math.cos(normalizedInput.angle) * launchSpeed,
    y: Math.sin(normalizedInput.angle) * launchSpeed
  };

  // 3. Simulate
  const serverFinalState = simulate(stateToSim, steps);

  // 4. Compare serverFinalState and clientFinalState
  const tolerance = 0.001; // Allow small floating point variations

  const distance = Math.sqrt(
    Math.pow(serverFinalState.ball.position.x - clientFinalState.ball.position.x, 2) +
    Math.pow(serverFinalState.ball.position.y - clientFinalState.ball.position.y, 2)
  );

  return distance < tolerance;
}
