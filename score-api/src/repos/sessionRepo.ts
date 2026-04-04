import { db } from '../db';
import { sessions } from '../db/schema';
import { eq, and, lt } from 'drizzle-orm';

export class SessionRepo {
  static async createSession(userId: number, refreshTokenHash: string, expiresAt: Date) {
    const [session] = await db.insert(sessions).values({ userId, refreshTokenHash, expiresAt }).returning();
    return session;
  }

  static async findSession(userId: number, refreshTokenHash: string) {
    const [session] = await db.select().from(sessions).where(
      and(eq(sessions.userId, userId), eq(sessions.refreshTokenHash, refreshTokenHash))
    );
    return session;
  }

  static async revokeSession(id: number) {
    await db.delete(sessions).where(eq(sessions.id, id));
  }

  static async revokeAllSessionsForUser(userId: number) {
    await db.delete(sessions).where(eq(sessions.userId, userId));
  }

  static async pruneExpired() {
    await db.delete(sessions).where(lt(sessions.expiresAt, new Date()));
  }
}
