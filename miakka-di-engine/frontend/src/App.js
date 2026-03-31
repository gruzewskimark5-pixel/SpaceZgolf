import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CourseOverview from './CourseOverview';
import DICalculator from './DICalculator';

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [course, setCourse] = useState(null);
  const [holes, setHoles] = useState([]);

  useEffect(() => {
    // Fetch course data on mount
    axios.get('http://localhost:3001/api/courses/miakka')
      .then(res => setCourse(res.data))
      .catch(err => console.error("Error fetching course", err));

    axios.get('http://localhost:3001/api/courses/miakka/holes')
      .then(res => setHoles(res.data))
      .catch(err => console.error("Error fetching holes", err));
  }, []);

  if (!course) return <div>Loading...</div>;

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>{course.name} - DI Engine</h1>

      <div style={{ marginBottom: '20px' }}>
        <button
          style={{ marginRight: '10px', padding: '10px' }}
          onClick={() => setActiveTab('overview')}
          disabled={activeTab === 'overview'}
        >
          Course Overview
        </button>
        <button
          style={{ padding: '10px' }}
          onClick={() => setActiveTab('calculator')}
          disabled={activeTab === 'calculator'}
        >
          DI Calculator
        </button>
      </div>

      {activeTab === 'overview' && <CourseOverview course={course} holes={holes} />}
      {activeTab === 'calculator' && <DICalculator course={course} holes={holes} />}
    </div>
  );
}

export default App;
