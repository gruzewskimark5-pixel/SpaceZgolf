import { KernelRequest, KernelResponse } from "./types";
import { simulate } from "../../engine/core";
import { calculateScore } from "../../services/scoring";
import { validateReplay } from "../../services/replayValidator";
import { db } from "../../services/db";

export async function handleKernelRequest(
  req: KernelRequest
): Promise<KernelResponse> {
  try {
    switch (req.type) {
      case "SIMULATE_SHOT": {
        const { world, steps, dt } = req.payload;
        const result = simulate(world, steps, dt);
        return { success: true, data: result };
      }

      case "SUBMIT_SCORE": {
        const { user, strokes, optimalDistance, actualDistance, precision } =
          req.payload;

        const result = calculateScore({
          strokes,
          optimalDistance,
          actualDistance,
          precision,
        });

        db.addScore({
          user,
          score: result.score,
          timestamp: Date.now(),
        });

        return { success: true, data: result };
      }

      case "VALIDATE_REPLAY": {
        const { replay, clientFinal } = req.payload;

        const validation = validateReplay(clientFinal, replay);

        if (!validation.valid) {
          return {
            success: false,
            error: "determinism mismatch",
          };
        }

        return { success: true, data: validation };
      }

      default:
        return { success: false, error: "unknown request type" };
    }
  } catch (err: any) {
    console.error("Kernel Request Error:", err);
    return { success: false, error: "Internal server error" };
  }
}
