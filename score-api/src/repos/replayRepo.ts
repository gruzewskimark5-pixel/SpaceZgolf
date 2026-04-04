import { db } from '../db';
import { replays, scores } from '../db/schema';
import { eq } from 'drizzle-orm';

export class ReplayRepo {
  static async setVerifiedStatus(replayId: number, verified: number) {
    const [replay] = await db.update(replays)
      .set({ verified })
      .where(eq(replays.id, replayId))
      .returning();
    return replay;
  }

  static async findByScoreId(scoreId: number) {
    const [replay] = await db.select().from(replays).where(eq(replays.scoreId, scoreId));
    return replay;
  }
}
