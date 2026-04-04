import React from 'react';

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
    <div style={{
      backgroundColor: colors.black,
      color: colors.white,
      fontFamily: 'monospace', // Mocking 'Apex Mono'
      minHeight: '100vh',
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      letterSpacing: '1px',
    }}>

      {/* --- TOP MODULE: LIVE MATCH TILE --- */}
      <section style={{
        backgroundColor: colors.graphite,
        border: `2px solid ${colors.white}`,
        padding: '24px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ margin: 0, textTransform: 'uppercase', fontWeight: 900 }}>Live Telemetry</h2>
          <span style={{ backgroundColor: colors.white, color: colors.black, padding: '4px 8px', fontWeight: 'bold', fontSize: '12px' }}>
            {liveMatchData.status}
          </span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {/* Player A */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
             <h1 style={{ margin: 0, fontSize: '32px', fontWeight: 900 }}>{liveMatchData.playerA.name}</h1>
             <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
               <div style={{ width: '12px', height: '12px', backgroundColor: liveMatchData.playerA.color }} />
               <span style={{ textTransform: 'uppercase' }}>{liveMatchData.playerA.archetype}</span>
             </div>
             <div style={{ marginTop: '8px', color: liveMatchData.playerA.pEloDelta.startsWith('+') ? colors.white : colors.white, opacity: 0.8 }}>
               pELO: {liveMatchData.playerA.pEloDelta}
             </div>
          </div>

          {/* VS */}
          <div style={{ fontSize: '24px', fontWeight: 900, opacity: 0.5 }}>VS</div>

          {/* Player B */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
             <h1 style={{ margin: 0, fontSize: '32px', fontWeight: 900 }}>{liveMatchData.playerB.name}</h1>
             <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
               <span style={{ textTransform: 'uppercase' }}>{liveMatchData.playerB.archetype}</span>
               <div style={{ width: '12px', height: '12px', backgroundColor: liveMatchData.playerB.color }} />
             </div>
             <div style={{ marginTop: '8px', color: liveMatchData.playerB.pEloDelta.startsWith('+') ? colors.white : colors.white, opacity: 0.8 }}>
               pELO: {liveMatchData.playerB.pEloDelta}
             </div>
          </div>
        </div>

        {/* Heat Index Bar */}
        <div style={{ marginTop: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '12px' }}>
            <span>HEAT INDEX</span>
            <span>{liveMatchData.heatIndex}%</span>
          </div>
          <div style={{ width: '100%', height: '8px', backgroundColor: colors.black, border: `1px solid ${colors.white}` }}>
            <div style={{ width: `${liveMatchData.heatIndex}%`, height: '100%', backgroundColor: colors.white }} />
          </div>
        </div>
      </section>

      {/* --- MIDDLE MODULE: MOMENTUM CURVES (Mock) --- */}
      <section style={{
        backgroundColor: colors.graphite,
        border: `2px solid ${colors.white}`,
        padding: '24px',
        flexGrow: 1,
      }}>
        <h2 style={{ margin: 0, marginBottom: '24px', textTransform: 'uppercase', fontWeight: 900 }}>Momentum Vectors</h2>
        <div style={{ position: 'relative', height: '150px', borderBottom: `1px solid ${colors.white}`, borderLeft: `1px solid ${colors.white}` }}>
           {/* Mock SVG lines to represent deterministic data */}
           <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
              <polyline fill="none" stroke={colors.athlete} strokeWidth="2" points="0,50 20,40 40,80 60,30 80,60 100,20" />
              <polyline fill="none" stroke={colors.technician} strokeWidth="2" points="0,50 20,60 40,30 60,70 80,40 100,50" />
           </svg>
        </div>
      </section>

      {/* --- BOTTOM MODULE: RIVALRY FEED --- */}
      <section style={{
        backgroundColor: colors.graphite,
        border: `2px solid ${colors.white}`,
        padding: '24px',
      }}>
        <h2 style={{ margin: 0, marginBottom: '24px', textTransform: 'uppercase', fontWeight: 900 }}>System Feed</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {rivalryFeed.map(feed => (
            <div key={feed.id} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: `1px solid #333`, paddingBottom: '12px' }}>
              <div>
                <span style={{ fontWeight: 'bold', marginRight: '8px', color: feed.type === 'HEAT_SPIKE' ? colors.athlete : feed.type === 'CHAOS_EVENT' ? colors.outlier : colors.technician }}>
                  [{feed.type}]
                </span>
                {feed.message}
              </div>
              <div style={{ opacity: 0.5 }}>{feed.timestamp}</div>
            </div>
          ))}
        </div>
      </section>

    </div>
  );
};

export default ApexLeagueApp;
