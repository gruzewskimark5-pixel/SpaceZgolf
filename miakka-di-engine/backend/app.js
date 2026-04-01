const express = require('express');
const cors = require('cors');
const db = require('./db');
const app = express();
app.use(express.json());
app.use(cors());

function calculate_di(hole_data, player_score) {
    // Execution Complexity (EC) - how physically demanding the hole is
    let ec = (
        (hole_data.geometry_penalty || 1.0) * 0.4 +
        (hole_data.hazard_pressure === "extreme" ? 3 : hole_data.hazard_pressure === "high" ? 2 : hole_data.hazard_pressure === "medium" ? 1 : 0) * 0.3 +
        ((hole_data.wind_strength || 0) / 20) * 0.3
    );
    ec = Math.min(Math.max(ec * 100, 0), 100);  // Scale to 0-100 roughly, based on logic

    // Decision Zone (Z) - how mentally complex the hole is
    const z_raw = (
        (hole_data.decision_complexity === "complex" ? 75 : hole_data.decision_complexity === "medium" ? 50 : 25) +
        (1 - (hole_data.cross_quartering_ratio || 0)) * 25
    );
    const z = Math.min(Math.max(z_raw, 0), 100);

    // Final DI score (0-100)
    let di = (ec * 0.65) + (z * 0.35);
    di = Math.round(di * 100) / 100;

    // Bonus: vs baseline comparison
    const baseline_delta = di - (hole_data.tour_avg_di || 0);

    return {
        hole_di: di,
        vs_baseline: Math.round(baseline_delta * 100) / 100,
        execution_component: Math.round(ec * 0.65 * 100) / 100,
        decision_component: Math.round(z * 0.35 * 100) / 100,
        player_score: player_score,
        par: hole_data.par,
        number: hole_data.number
    };
}

app.get('/api/courses/:id', (req, res) => {
  db.get("SELECT * FROM courses WHERE id = ?", [req.params.id], (err, row) => {
      if (err) {
          console.error('Database error:', err);
          return res.status(500).json({error: 'Internal server error'});
      }
      res.json(row);
  });
});

app.get('/api/courses/:id/holes', (req, res) => {
  db.all("SELECT * FROM holes WHERE course_id = ?", [req.params.id], (err, rows) => {
      if (err) {
          console.error('Database error:', err);
          return res.status(500).json({error: 'Internal server error'});
      }
      res.json(rows);
  });
});

app.post('/api/rounds/calculate-di', (req, res) => {
  const { course_id, scores } = req.body;
  if (!course_id || !scores) return res.status(400).json({error: "course_id and scores are required"});

  db.all("SELECT * FROM holes WHERE course_id = ?", [course_id], (err, holes) => {
      if (err) {
          console.error('Database error:', err);
          return res.status(500).json({error: 'Internal server error'});
      }
      if (holes.length === 0) return res.status(404).json({error: "Course not found"});

      const hole_breakdown = [];
      let total_di = 0;
      let calculated_holes = 0;

      holes.forEach(hole => {
          const score = scores[hole.number];
          if (score !== undefined) {
              const di_result = calculate_di(hole, score);
              hole_breakdown.push(di_result);
              total_di += di_result.hole_di;
              calculated_holes++;
          }
      });

      const overall_di = calculated_holes > 0 ? total_di / calculated_holes : 0;

      res.json({
          overall_di: Math.round(overall_di * 100) / 100,
          hole_breakdown
      });
  });
});

app.listen(3001, () => console.log("✅ DI Engine running on http://localhost:3001"));
