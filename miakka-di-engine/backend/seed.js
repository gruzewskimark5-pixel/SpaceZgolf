const db = require('./db');

// Seed Miakka data (focus on holes 3, 7, 14 first)
const seedData = [
  // Hole 3 example
  { number: 3, par: 4, yards_champion: 480, fairway_width_avg: 32, hazard_pressure: "high", decision_complexity: "complex", signature_test: "committed line", tour_avg_di: 78 },
  // Hole 7 example
  { number: 7, par: 5, yards_champion: 620, fairway_width_avg: 28, hazard_pressure: "extreme", decision_complexity: "medium", signature_test: "drift detector", tour_avg_di: 85 },
  // Hole 14 example
  { number: 14, par: 3, yards_champion: 210, fairway_width_avg: 0, hazard_pressure: "high", decision_complexity: "complex", signature_test: "width discipline", tour_avg_di: 82 },
  // ... (remaining 15 holes can be added with baseline values)
];

db.serialize(() => {
  db.run("INSERT OR IGNORE INTO courses VALUES ('miakka', 'Miakka', 72, 7200, 6800, 6200)");
  seedData.forEach(h => {
    // We have 20 columns: id (NULL), course_id ('miakka'), and 18 data values.
    db.run(`INSERT OR IGNORE INTO holes VALUES (
      NULL, 'miakka', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )`, [
      h.number,
      h.par,
      h.yards_champion,
      h.yards_blue || h.yards_champion,
      h.yards_white || h.yards_champion,
      h.fairway_width_avg,
      30, // green_depth
      25, // green_width
      h.primary_angle || "fade",
      h.hazard_pressure,
      "SE", // wind_direction
      12, // wind_strength
      0.4, // cross_quartering_ratio
      h.tour_avg_di,
      h.amateur_avg_di || 65,
      h.geometry_penalty || 1.2,
      h.decision_complexity,
      h.signature_test
    ]);
  });
});
console.log("✅ Miakka seeded");
