export function calculateScore(params: {
  strokes: number;
  optimalDistance: number;
  actualDistance: number;
  precision: number;
}) {
  const efficiency = params.optimalDistance / Math.max(params.actualDistance, 1);

  const score = (efficiency * 100) - (params.strokes * 10) - params.precision;

  return {
    efficiency,
    score
  };
}
