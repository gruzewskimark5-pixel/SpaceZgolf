const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./miakka.db');

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS courses (
    id TEXT PRIMARY KEY,
    name TEXT,
    par INTEGER,
    yards_champion INTEGER,
    yards_blue INTEGER,
    yards_white INTEGER
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS holes (
    id INTEGER PRIMARY KEY,
    course_id TEXT,
    number INTEGER,
    par INTEGER,
    yards_champion INTEGER,
    yards_blue INTEGER,
    yards_white INTEGER,
    fairway_width_avg REAL,
    green_depth REAL,
    green_width REAL,
    primary_angle TEXT,
    hazard_pressure TEXT,
    wind_direction TEXT,
    wind_strength REAL,
    cross_quartering_ratio REAL,
    tour_avg_di REAL,
    amateur_avg_di REAL,
    geometry_penalty REAL,
    decision_complexity TEXT,
    signature_test TEXT,
    FOREIGN KEY(course_id) REFERENCES courses(id)
  )`);
});

module.exports = db;
