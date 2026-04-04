"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const migrator_1 = require("drizzle-orm/node-postgres/migrator");
const index_1 = require("./index");
async function main() {
    console.log('Running migrations...');
    try {
        await (0, migrator_1.migrate)(index_1.db, { migrationsFolder: './drizzle' });
        console.log('Migrations complete!');
    }
    catch (e) {
        console.error('Migration failed. Database may not be running locally.');
    }
    process.exit(0);
}
main().catch((err) => {
    console.error('Migration failed!', err);
    process.exit(1);
});
