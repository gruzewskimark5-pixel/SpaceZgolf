import { WorldState } from "./types";
import { sub, length, normalize, scale } from "./vector";

export function resolveCollisions(state: WorldState): WorldState {
  for (const body of state.bodies) {
    const dir = sub(state.ball.position, body.position);
    const dist = length(dir);

    if (dist < body.radius) {
      const n = normalize(dir);
      state.ball.position = {
        x: body.position.x + n.x * body.radius,
        y: body.position.y + n.y * body.radius,
      };

      // simple reflection
      const v = state.ball.velocity;
      const dot = v.x * n.x + v.y * n.y;
      state.ball.velocity = {
        x: v.x - 2 * dot * n.x,
        y: v.y - 2 * dot * n.y,
      };
    }
  }

  return state;
}
