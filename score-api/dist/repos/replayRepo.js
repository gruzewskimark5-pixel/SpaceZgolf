"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReplayRepo = void 0;
const db_1 = require("../db");
const schema_1 = require("../db/schema");
const drizzle_orm_1 = require("drizzle-orm");
class ReplayRepo {
    static async setVerifiedStatus(replayId, verified) {
        const [replay] = await db_1.db.update(schema_1.replays)
            .set({ verified })
            .where((0, drizzle_orm_1.eq)(schema_1.replays.id, replayId))
            .returning();
        return replay;
    }
    static async findByScoreId(scoreId) {
        const [replay] = await db_1.db.select().from(schema_1.replays).where((0, drizzle_orm_1.eq)(schema_1.replays.scoreId, scoreId));
        return replay;
    }
}
exports.ReplayRepo = ReplayRepo;
