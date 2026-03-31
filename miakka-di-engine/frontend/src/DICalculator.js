import React, { useState } from 'react';
import axios from 'axios';

function DICalculator({ course, holes }) {
  const [scores, setScores] = useState({});
  const [calculationResult, setCalculationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleScoreChange = (holeNumber, score) => {
    setScores(prev => ({
      ...prev,
      [holeNumber]: parseInt(score, 10) || ''
    }));
  };

  const calculateDI = () => {
    setLoading(true);
    setError(null);
    setCalculationResult(null);

    const scoresToSubmit = {};
    for (const [key, value] of Object.entries(scores)) {
      if (value) {
        scoresToSubmit[key] = value;
      }
    }

    if (Object.keys(scoresToSubmit).length === 0) {
      setError("Please enter at least one score to calculate DI.");
      setLoading(false);
      return;
    }

    axios.post('http://localhost:3001/api/rounds/calculate-di', {
      course_id: course.id,
      scores: scoresToSubmit
    })
      .then(res => {
        setCalculationResult(res.data);
      })
      .catch(err => {
        console.error("Error calculating DI", err);
        setError("Failed to calculate DI. Ensure backend is running.");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div>
      <h2>DI Calculator</h2>
      <p>Enter scores for the holes you played to calculate the Decision Intelligence (DI) score.</p>

      {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(80px, 1fr))', gap: '10px', marginBottom: '20px' }}>
        {holes.map(hole => (
          <div key={hole.id} style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{ fontSize: '12px' }}>Hole {hole.number} (Par {hole.par})</label>
            <input
              type="number"
              min="1"
              max="20"
              value={scores[hole.number] || ''}
              onChange={(e) => handleScoreChange(hole.number, e.target.value)}
              style={{ padding: '5px', width: '100%' }}
            />
          </div>
        ))}
      </div>

      <button
        onClick={calculateDI}
        disabled={loading}
        style={{ padding: '10px 20px', backgroundColor: '#28a745', color: 'white', border: 'none', cursor: 'pointer', borderRadius: '4px' }}
      >
        {loading ? 'Calculating...' : 'Calculate DI'}
      </button>

      {calculationResult && (
        <div style={{ marginTop: '20px', border: '1px solid #ddd', padding: '20px', borderRadius: '8px', backgroundColor: '#f0f8ff' }}>
          <h3 style={{ margin: '0 0 15px 0' }}>Results</h3>

          <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '20px' }}>
            Overall Round DI: <span style={{ color: '#0056b3' }}>{calculationResult.overall_di}</span>
          </div>

          <h4>Hole Breakdown</h4>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
            <thead>
              <tr style={{ backgroundColor: '#e9ecef', textAlign: 'left' }}>
                <th style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>Hole</th>
                <th style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>Score</th>
                <th style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>Hole DI</th>
                <th style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>Exec. Comp.</th>
                <th style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>Dec. Comp.</th>
                <th style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>Vs Baseline</th>
              </tr>
            </thead>
            <tbody>
              {calculationResult.hole_breakdown.map(h => (
                <tr key={h.number}>
                  <td style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>{h.number} (Par {h.par})</td>
                  <td style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>{h.player_score}</td>
                  <td style={{ padding: '8px', borderBottom: '1px solid #dee2e6', fontWeight: 'bold' }}>{h.hole_di}</td>
                  <td style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>{h.execution_component}</td>
                  <td style={{ padding: '8px', borderBottom: '1px solid #dee2e6' }}>{h.decision_component}</td>
                  <td style={{ padding: '8px', borderBottom: '1px solid #dee2e6', color: h.vs_baseline > 0 ? 'red' : h.vs_baseline < 0 ? 'green' : 'black' }}>
                    {h.vs_baseline > 0 ? '+' : ''}{h.vs_baseline}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default DICalculator;
