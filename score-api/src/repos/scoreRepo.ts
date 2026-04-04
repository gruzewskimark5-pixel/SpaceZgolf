import { db } from '../db';
import { scores, replays, users } from '../db/schema';
import { eq, and, desc, asc, sql } from 'drizzle-orm';

export class ScoreRepo {
  static async submitScoreWithReplay(userId: number, courseId: string, score: number, replayData: any, seasonId?: string) {
    return await db.transaction(async (tx) => {
      const [newScore] = await tx.insert(scores).values({
        userId,
        courseId,
        score,
        seasonId
      }).returning();

      await tx.insert(replays).values({
        scoreId: newScore.id,
        data: replayData,
        verified: 0
      });

      return newScore;
    });
  }

  static async getLeaderboard(courseId: string) {
    // Leaderboard can filter to only show verified scores
    const leaderboard = await db.select({
      id: scores.id,
      score: scores.score,
      username: users.username,
      createdAt: scores.createdAt,
      verified: replays.verified
    })
    .from(scores)
    .innerJoin(users, eq(scores.userId, users.id))
    .innerJoin(replays, eq(scores.id, replays.scoreId))
    .where(and(eq(scores.courseId, courseId), eq(replays.verified, 1)))
    .orderBy(asc(scores.score))
    .limit(100);

    return leaderboard;
  }

  static async getUserScores(userId: number) {
    return await db.select().from(scores).where(eq(scores.userId, userId)).orderBy(desc(scores.createdAt));
  }

  static async getUserBest(userId: number, courseId: string) {
    const [bestScore] = await db.select()
      .from(scores)
      .where(and(eq(scores.userId, userId), eq(scores.courseId, courseId)))
      .orderBy(asc(scores.score))
      .limit(1);
    return bestScore;
  }
}
