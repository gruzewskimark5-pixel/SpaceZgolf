import express from "express";
import { simulate, STANDARD_SIM_STEPS } from "../engine/core";
import { calculateScore } from "../services/scoring";
import { validateReplay } from "../services/replay";
import { saveScore, getLeaderboard } from "../services/db";

const app = express();
app.use(express.json());

// POST /simulateShot
app.post("/simulateShot", (req, res) => {
  const { world, steps } = req.body;

  const simSteps = steps || STANDARD_SIM_STEPS;
  const result = simulate(world, simSteps);

  res.json({ finalState: result });
});

// POST /submitScore
app.post("/submitScore", async (req, res) => {
  const { user, strokes, optimalDistance, actualDistance, precision, initialState, input, clientFinalState, steps } = req.body;

  if (!user) {
    return res.status(400).json({ error: "User is required." });
  }

  const simSteps = steps || STANDARD_SIM_STEPS;

  // Anti-cheat: Validate the shot locally
  if (initialState && input && clientFinalState) {
    const isValid = validateReplay(initialState, input, clientFinalState, simSteps);
    if (!isValid) {
      return res.status(403).json({ error: "Anti-cheat validation failed. Replay mismatch." });
    }
  }

  const result = calculateScore({
    strokes,
    optimalDistance,
    actualDistance,
    precision
  });

  try {
    await saveScore(user, result.score);
    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to save score." });
  }
});

// GET /leaderboard
app.get("/leaderboard", async (_, res) => {
  try {
    const topScores = await getLeaderboard();
    res.json(topScores);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to fetch leaderboard." });
  }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`SpaceZgolf API running on port ${PORT}`);
});
