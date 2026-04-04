import { Vec2 } from "./types";

export const add = (a: Vec2, b: Vec2): Vec2 => ({ x: a.x + b.x, y: a.y + b.y });
export const sub = (a: Vec2, b: Vec2): Vec2 => ({ x: a.x - b.x, y: a.y - b.y });
export const scale = (v: Vec2, s: number): Vec2 => ({ x: v.x * s, y: v.y * s });
export const length = (v: Vec2): number => Math.sqrt(v.x * v.x + v.y * v.y);
export const normalize = (v: Vec2): Vec2 => {
  const len = length(v) || 1;
  return { x: v.x / len, y: v.y / len };
};
