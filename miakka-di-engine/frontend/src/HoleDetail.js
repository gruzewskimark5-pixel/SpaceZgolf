import React from 'react';

function HoleDetail({ hole }) {
  if (!hole) return null;

  return (
    <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
      <h2>Hole {hole.number} Details</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div>
          <h3>Basic Stats</h3>
          <ul>
            <li><strong>Par:</strong> {hole.par}</li>
            <li><strong>Yards (Champion):</strong> {hole.yards_champion}</li>
            <li><strong>Fairway Width:</strong> {hole.fairway_width_avg} yds</li>
            <li><strong>Hazard Pressure:</strong> {hole.hazard_pressure}</li>
            <li><strong>Decision Complexity:</strong> {hole.decision_complexity}</li>
          </ul>
        </div>

        <div>
          <h3>DI Baseline Stats</h3>
          <ul>
            <li><strong>Tour Avg DI:</strong> {hole.tour_avg_di}</li>
            <li><strong>Amateur Avg DI:</strong> {hole.amateur_avg_di}</li>
            <li><strong>Signature Test:</strong> {hole.signature_test}</li>
            <li><strong>Geometry Penalty:</strong> {hole.geometry_penalty}</li>
            <li><strong>Primary Angle:</strong> {hole.primary_angle}</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default HoleDetail;
