export type Vec2 = { x: number; y: number };

export type Body = {
  id: string;
  position: Vec2;
  mass: number;
  radius: number;
};

export type Ball = {
  position: Vec2;
  velocity: Vec2;
};

export type WorldState = {
  ball: Ball;
  bodies: Body[];
};

export type ShotInput = {
  angle: number; // radians
  power: number; // normalized [0,1]
};
