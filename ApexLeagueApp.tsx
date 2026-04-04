import React from 'react';
import Lobby from './spacez-golf-mvp/ui/Lobby';

// --- APEX LEAGUE COLOR SYSTEM ---
const colors = {
  athlete: '#FF2A2A',
  technician: '#1A7CFF',
  outlier: '#FF00A8',
  hybrid: '#00D4C7',
  black: '#0A0A0A',
  graphite: '#1F1F1F',
  white: '#FFFFFF',
  gold: '#F5C542',
};

// --- MOCK DATA ---
const liveMatchData = {
  playerA: { name: 'Kael', archetype: 'Athlete', color: colors.athlete, pEloDelta: '+12.4' },
  playerB: { name: 'Rin', archetype: 'Technician', color: colors.technician, pEloDelta: '-4.1' },
  heatIndex: 87,
  status: 'IDENTITY COLLISION DETECTED',
};

const rivalryFeed = [
  { id: 1, type: 'HEAT_SPIKE', message: 'Rivalry Heat Spike: Kael vs Rin now at 9.4', timestamp: '10s' },
  { id: 2, type: 'CHAOS_EVENT', message: 'Chaos Event: Outlier interference detected', timestamp: '45s' },
  { id: 3, type: 'STABILITY_LOCK', message: 'Technician Lock: Rin stabilizes match state', timestamp: '2m' },
];

export const ApexLeagueApp: React.FC = () => {
  return (
    <div style={{ backgroundColor: colors.black, color: colors.white, fontFamily: 'monospace', minHeight: '100vh', padding: '20px' }}>
      <h1>Apex League</h1>
      <Lobby />
    </div>
  );
};

export default ApexLeagueApp;
