import sqlite3 from 'sqlite3';

const db = new sqlite3.Database('./leaderboard.db', (err) => {
  if (err) {
    console.error('Error opening database', err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS leaderboard (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user TEXT NOT NULL,
      score REAL NOT NULL
    )`);
  }
});

export function saveScore(user: string, score: number): Promise<void> {
  return new Promise((resolve, reject) => {
    db.run(
      'INSERT INTO leaderboard (user, score) VALUES (?, ?)',
      [user, score],
      function (err) {
        if (err) reject(err);
        else resolve();
      }
    );
  });
}

export function getLeaderboard(limit: number = 10): Promise<{ user: string; score: number }[]> {
  return new Promise((resolve, reject) => {
    db.all(
      'SELECT user, score FROM leaderboard ORDER BY score DESC LIMIT ?',
      [limit],
      (err, rows: { user: string; score: number }[]) => {
        if (err) reject(err);
        else resolve(rows);
      }
    );
  });
}
