import { pgTable, serial, text, integer, timestamp, jsonb, boolean, index, primaryKey } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  username: text('username').notNull().unique(),
  email: text('email').notNull().unique(),
  passwordHash: text('password_hash').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const sessions = pgTable('sessions', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  refreshTokenHash: text('refresh_token_hash').notNull(),
  expiresAt: timestamp('expires_at').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const scores = pgTable('scores', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  courseId: text('course_id').notNull(),
  score: integer('score').notNull(),
  seasonId: text('season_id'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const replays = pgTable('replays', {
  id: serial('id').primaryKey(),
  scoreId: integer('score_id').notNull().references(() => scores.id, { onDelete: 'cascade' }),
  data: jsonb('data').notNull(),
  verified: integer('verified').notNull().default(0), // 0: pending, 1: verified, -1: invalid
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const usersRelations = relations(users, ({ many }) => ({
  scores: many(scores),
  sessions: many(sessions),
}));

export const scoresRelations = relations(scores, ({ one }) => ({
  user: one(users, {
    fields: [scores.userId],
    references: [users.id],
  }),
  replay: one(replays, {
    fields: [scores.id],
    references: [replays.scoreId],
  }),
}));

export const replaysRelations = relations(replays, ({ one }) => ({
  score: one(scores, {
    fields: [replays.scoreId],
    references: [scores.id],
  }),
}));
