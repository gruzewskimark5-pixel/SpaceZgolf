export type Player = {
  id: string;
  rating: number;
  avatar: string;
  region: string;
  skill: number;
  streak: number;
};

export type ShotContext = {
  holeImportance: number; // 1-10
  scoreDiff: number; // strokes
  streak: number;
};

export function calculateHeat({
  holeImportance,
  scoreDiff,
  streak,
}: ShotContext) {
  let heat =
    holeImportance * 10 +
    (3 - scoreDiff) * 5 +
    streak * 4;

  return Math.max(0, Math.min(100, heat));
}

export function applyAvatarModifiers(player: Player, heat: number, basePerformance: number) {
  switch (player.avatar) {
    case "closer":
      return basePerformance + heat * 0.2;

    case "ice":
      return basePerformance; // ignores heat

    case "gambler":
      return basePerformance + (Math.random() * 20 - 10);

    case "momentum":
      return basePerformance + player.streak * 5;

    default:
      return basePerformance;
  }
}

export function resolveShot(player: Player, context: ShotContext) {
  const heat = calculateHeat(context);

  let performance = player.skill;

  performance = applyAvatarModifiers(player, heat, performance);

  // randomness layer
  const variance = Math.random() * 10;

  return {
    heat,
    result: performance - variance
  };
}
