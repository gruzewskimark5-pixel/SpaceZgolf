import { WorldState, Vec2 } from "./types";
import { sub, length, normalize, scale } from "./vector";

const G = 6.674e-3; // simplified gravitational constant

export function computeGravity(state: WorldState): Vec2 {
  let total: Vec2 = { x: 0, y: 0 };

  for (const body of state.bodies) {
    const dir = sub(body.position, state.ball.position);
    const dist = Math.max(length(dir), 1);
    const force = (G * body.mass) / (dist * dist);
    const accel = scale(normalize(dir), force);
    total.x += accel.x;
    total.y += accel.y;
  }

  return total;
}
