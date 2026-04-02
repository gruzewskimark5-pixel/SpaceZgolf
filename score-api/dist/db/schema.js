"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.replaysRelations = exports.scoresRelations = exports.usersRelations = exports.replays = exports.scores = exports.sessions = exports.users = void 0;
const pg_core_1 = require("drizzle-orm/pg-core");
const drizzle_orm_1 = require("drizzle-orm");
exports.users = (0, pg_core_1.pgTable)('users', {
    id: (0, pg_core_1.serial)('id').primaryKey(),
    username: (0, pg_core_1.text)('username').notNull().unique(),
    email: (0, pg_core_1.text)('email').notNull().unique(),
    passwordHash: (0, pg_core_1.text)('password_hash').notNull(),
    createdAt: (0, pg_core_1.timestamp)('created_at').defaultNow().notNull(),
});
exports.sessions = (0, pg_core_1.pgTable)('sessions', {
    id: (0, pg_core_1.serial)('id').primaryKey(),
    userId: (0, pg_core_1.integer)('user_id').notNull().references(() => exports.users.id, { onDelete: 'cascade' }),
    refreshTokenHash: (0, pg_core_1.text)('refresh_token_hash').notNull(),
    expiresAt: (0, pg_core_1.timestamp)('expires_at').notNull(),
    createdAt: (0, pg_core_1.timestamp)('created_at').defaultNow().notNull(),
});
exports.scores = (0, pg_core_1.pgTable)('scores', {
    id: (0, pg_core_1.serial)('id').primaryKey(),
    userId: (0, pg_core_1.integer)('user_id').notNull().references(() => exports.users.id, { onDelete: 'cascade' }),
    courseId: (0, pg_core_1.text)('course_id').notNull(),
    score: (0, pg_core_1.integer)('score').notNull(),
    seasonId: (0, pg_core_1.text)('season_id'),
    createdAt: (0, pg_core_1.timestamp)('created_at').defaultNow().notNull(),
});
exports.replays = (0, pg_core_1.pgTable)('replays', {
    id: (0, pg_core_1.serial)('id').primaryKey(),
    scoreId: (0, pg_core_1.integer)('score_id').notNull().references(() => exports.scores.id, { onDelete: 'cascade' }),
    data: (0, pg_core_1.jsonb)('data').notNull(),
    verified: (0, pg_core_1.integer)('verified').notNull().default(0), // 0: pending, 1: verified, -1: invalid
    createdAt: (0, pg_core_1.timestamp)('created_at').defaultNow().notNull(),
});
exports.usersRelations = (0, drizzle_orm_1.relations)(exports.users, ({ many }) => ({
    scores: many(exports.scores),
    sessions: many(exports.sessions),
}));
exports.scoresRelations = (0, drizzle_orm_1.relations)(exports.scores, ({ one }) => ({
    user: one(exports.users, {
        fields: [exports.scores.userId],
        references: [exports.users.id],
    }),
    replay: one(exports.replays, {
        fields: [exports.scores.id],
        references: [exports.replays.scoreId],
    }),
}));
exports.replaysRelations = (0, drizzle_orm_1.relations)(exports.replays, ({ one }) => ({
    score: one(exports.scores, {
        fields: [exports.replays.scoreId],
        references: [exports.scores.id],
    }),
}));
