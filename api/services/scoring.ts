export function calculateScore(data: { strokes: number, optimalDistance: number, actualDistance: number, precision: number }) {
    return { score: data.strokes * 100, precision: data.precision };
}
