"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SessionRepo = void 0;
const db_1 = require("../db");
const schema_1 = require("../db/schema");
const drizzle_orm_1 = require("drizzle-orm");
class SessionRepo {
    static async createSession(userId, refreshTokenHash, expiresAt) {
        const [session] = await db_1.db.insert(schema_1.sessions).values({ userId, refreshTokenHash, expiresAt }).returning();
        return session;
    }
    static async findSession(userId, refreshTokenHash) {
        const [session] = await db_1.db.select().from(schema_1.sessions).where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.sessions.userId, userId), (0, drizzle_orm_1.eq)(schema_1.sessions.refreshTokenHash, refreshTokenHash)));
        return session;
    }
    static async revokeSession(id) {
        await db_1.db.delete(schema_1.sessions).where((0, drizzle_orm_1.eq)(schema_1.sessions.id, id));
    }
    static async revokeAllSessionsForUser(userId) {
        await db_1.db.delete(schema_1.sessions).where((0, drizzle_orm_1.eq)(schema_1.sessions.userId, userId));
    }
    static async pruneExpired() {
        await db_1.db.delete(schema_1.sessions).where((0, drizzle_orm_1.lt)(schema_1.sessions.expiresAt, new Date()));
    }
}
exports.SessionRepo = SessionRepo;
