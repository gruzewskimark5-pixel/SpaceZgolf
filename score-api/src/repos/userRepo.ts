import { db } from '../db';
import { users } from '../db/schema';
import { eq, or } from 'drizzle-orm';

export class UserRepo {
  static async createUser(username: string, email: string, passwordHash: string) {
    const [user] = await db.insert(users).values({ username, email, passwordHash }).returning();
    return user;
  }

  static async findByUsernameOrEmail(identifier: string) {
    const [user] = await db.select().from(users).where(
      or(eq(users.username, identifier), eq(users.email, identifier))
    );
    return user;
  }

  static async findById(id: number) {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user;
  }
}
