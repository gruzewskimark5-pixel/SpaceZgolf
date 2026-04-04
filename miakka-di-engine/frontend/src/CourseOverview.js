import React, { useState } from 'react';
import HoleDetail from './HoleDetail';

function CourseOverview({ course, holes }) {
  const [selectedHole, setSelectedHole] = useState(null);

  return (
    <div>
      <h2>Course Overview</h2>
      <p>Par: {course.par} | Champion: {course.yards_champion} yds | Blue: {course.yards_blue} yds | White: {course.yards_white} yds</p>

      <h3>Holes</h3>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '20px' }}>
        {holes.map(hole => (
          <button
            key={hole.id}
            style={{
              padding: '15px',
              fontSize: '16px',
              backgroundColor: selectedHole && selectedHole.id === hole.id ? '#007bff' : '#f0f0f0',
              color: selectedHole && selectedHole.id === hole.id ? 'white' : 'black',
              border: '1px solid #ccc',
              cursor: 'pointer'
            }}
            onClick={() => setSelectedHole(hole)}
          >
            Hole {hole.number}
          </button>
        ))}
      </div>

      {selectedHole && <HoleDetail hole={selectedHole} />}
    </div>
  );
}

export default CourseOverview;
