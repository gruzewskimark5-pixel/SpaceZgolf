import { migrate } from 'drizzle-orm/node-postgres/migrator';
import { db } from './index';

async function main() {
  console.log('Running migrations...');
  try {
    await migrate(db, { migrationsFolder: './drizzle' });
    console.log('Migrations complete!');
  } catch(e) {
    console.error('Migration failed. Database may not be running locally.');
  }
  process.exit(0);
}

main().catch((err) => {
  console.error('Migration failed!', err);
  process.exit(1);
});
