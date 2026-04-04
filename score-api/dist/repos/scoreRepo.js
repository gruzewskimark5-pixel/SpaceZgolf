"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ScoreRepo = void 0;
const db_1 = require("../db");
const schema_1 = require("../db/schema");
const drizzle_orm_1 = require("drizzle-orm");
class ScoreRepo {
    static async submitScoreWithReplay(userId, courseId, score, replayData, seasonId) {
        return await db_1.db.transaction(async (tx) => {
            const [newScore] = await tx.insert(schema_1.scores).values({
                userId,
                courseId,
                score,
                seasonId
            }).returning();
            await tx.insert(schema_1.replays).values({
                scoreId: newScore.id,
                data: replayData,
                verified: 0
            });
            return newScore;
        });
    }
    static async getLeaderboard(courseId) {
        // Leaderboard can filter to only show verified scores
        const leaderboard = await db_1.db.select({
            id: schema_1.scores.id,
            score: schema_1.scores.score,
            username: schema_1.users.username,
            createdAt: schema_1.scores.createdAt,
            verified: schema_1.replays.verified
        })
            .from(schema_1.scores)
            .innerJoin(schema_1.users, (0, drizzle_orm_1.eq)(schema_1.scores.userId, schema_1.users.id))
            .innerJoin(schema_1.replays, (0, drizzle_orm_1.eq)(schema_1.scores.id, schema_1.replays.scoreId))
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.scores.courseId, courseId), (0, drizzle_orm_1.eq)(schema_1.replays.verified, 1)))
            .orderBy((0, drizzle_orm_1.asc)(schema_1.scores.score))
            .limit(100);
        return leaderboard;
    }
    static async getUserScores(userId) {
        return await db_1.db.select().from(schema_1.scores).where((0, drizzle_orm_1.eq)(schema_1.scores.userId, userId)).orderBy((0, drizzle_orm_1.desc)(schema_1.scores.createdAt));
    }
    static async getUserBest(userId, courseId) {
        const [bestScore] = await db_1.db.select()
            .from(schema_1.scores)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.scores.userId, userId), (0, drizzle_orm_1.eq)(schema_1.scores.courseId, courseId)))
            .orderBy((0, drizzle_orm_1.asc)(schema_1.scores.score))
            .limit(1);
        return bestScore;
    }
}
exports.ScoreRepo = ScoreRepo;
