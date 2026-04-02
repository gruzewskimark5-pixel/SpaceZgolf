"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.UserRepo = void 0;
const db_1 = require("../db");
const schema_1 = require("../db/schema");
const drizzle_orm_1 = require("drizzle-orm");
class UserRepo {
    static async createUser(username, email, passwordHash) {
        const [user] = await db_1.db.insert(schema_1.users).values({ username, email, passwordHash }).returning();
        return user;
    }
    static async findByUsernameOrEmail(identifier) {
        const [user] = await db_1.db.select().from(schema_1.users).where((0, drizzle_orm_1.or)((0, drizzle_orm_1.eq)(schema_1.users.username, identifier), (0, drizzle_orm_1.eq)(schema_1.users.email, identifier)));
        return user;
    }
    static async findById(id) {
        const [user] = await db_1.db.select().from(schema_1.users).where((0, drizzle_orm_1.eq)(schema_1.users.id, id));
        return user;
    }
}
exports.UserRepo = UserRepo;
