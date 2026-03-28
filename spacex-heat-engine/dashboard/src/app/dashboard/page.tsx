"use client";

import { useContext, useEffect, useState } from "react";
import { AuthContext } from "@/components/AuthProvider";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

export default function Dashboard() {
  const { user, token } = useContext(AuthContext);
  const [data, setData] = useState<any>(null);

  // Use a hardcoded Mastermind ID if Firebase isn't connected
  const [activePlayer, setActivePlayer] = useState("kai_trump");

  useEffect(() => {
    const uid = user?.uid || activePlayer;

    (async () => {
      try {
          const res = await fetch(
            `${API_BASE}/digital-twin/player/${uid}`,
            { headers: { Authorization: `Bearer ${token || "mock"}` } }
          );
          if (res.ok) setData(await res.json());
          else setData(null);
      } catch (err) {
          console.error("Failed to fetch Twin", err);
      }
    })();
  }, [token, user, activePlayer]);

  // Automatically refresh every 5 seconds for live demo
  useEffect(() => {
      const interval = setInterval(() => {
          const uid = user?.uid || activePlayer;
          fetch(`${API_BASE}/digital-twin/player/${uid}`, { headers: { Authorization: `Bearer ${token || "mock"}` } })
            .then(res => { if (res.ok) return res.json(); else throw new Error(); })
            .then(json => setData(json))
            .catch(() => {});
      }, 5000);
      return () => clearInterval(interval);
  }, [user, activePlayer, token]);

  const trendColor = (trend: string) => {
      if (trend === "↑") return "text-emerald-400";
      if (trend === "↓") return "text-rose-400";
      return "text-slate-400";
  }

  return (
    <main className="p-8 text-slate-50 min-h-screen bg-[#0a0a0a]">
      <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">Member Console</h1>
          <select
             className="bg-slate-900 border border-slate-700 text-slate-200 rounded p-2 text-sm focus:outline-none focus:border-emerald-500"
             value={activePlayer}
             onChange={(e) => setActivePlayer(e.target.value)}
          >
             <option value="kai_trump">Kai Trump</option>
             <option value="nelly_korda">Nelly Korda</option>
             <option value="mia_baker">Mia Baker</option>
             <option value="alexis_miestowski">Alexis Miestowski</option>
             <option value="gabriella_degasperis">Gabriella DeGasperis</option>
          </select>
      </div>

      {data ? (
          <div className="grid md:grid-cols-2 gap-8">
             <div className="bg-[#121212] border border-slate-800 shadow-xl rounded-xl p-6">
                 <h2 className="text-slate-400 uppercase text-xs tracking-wider mb-4 border-b border-slate-800 pb-2">Identity & Heat</h2>
                 <div className="text-2xl font-bold mb-1">{data.state.name}</div>
                 <div className="text-sm text-emerald-400 mb-6">{data.state.cluster} Node</div>

                 <div className="grid grid-cols-2 gap-4 text-center font-mono">
                    <div className="bg-slate-900 p-4 rounded relative">
                        <div className="text-slate-500 text-xs mb-1">Current Heat</div>
                        <div className="text-2xl text-rose-400">
                           {data.state.current_heat.toFixed(2)}
                           <span className={`absolute top-4 right-4 text-lg ${trendColor(data.state.trend_direction)}`}>{data.state.trend_direction}</span>
                        </div>
                    </div>
                    <div className="bg-slate-900 p-4 rounded relative">
                        <div className="text-slate-500 text-xs mb-1">Momentum</div>
                        <div className="text-2xl text-sky-400">{data.state.momentum > 0 ? "+" : ""}{data.state.momentum.toFixed(2)}</div>
                    </div>
                 </div>
             </div>

             <div className="bg-[#121212] border border-slate-800 shadow-xl rounded-xl p-6">
                 <h2 className="text-slate-400 uppercase text-xs tracking-wider mb-4 border-b border-slate-800 pb-2">Digital Twin Performance</h2>
                 <div className="grid grid-cols-2 gap-4 text-center font-mono h-full">
                    <div className="flex flex-col justify-center bg-slate-900 p-4 rounded">
                        <div className="text-slate-500 text-xs mb-1">Avg Ball Speed</div>
                        <div className="text-2xl text-amber-400">{data.state.avg_ball_speed.toFixed(1)}</div>
                    </div>
                    <div className="flex flex-col justify-center bg-slate-900 p-4 rounded">
                        <div className="text-slate-500 text-xs mb-1">Fairway %</div>
                        <div className="text-2xl text-emerald-400">{data.state.fairway_percentage.toFixed(1)}%</div>
                    </div>
                 </div>
             </div>

             <div className="md:col-span-2 bg-[#121212] border border-slate-800 shadow-xl rounded-xl p-6">
                 <h2 className="text-slate-400 uppercase text-xs tracking-wider mb-4 border-b border-slate-800 pb-2">Recent Digital Twin Events</h2>
                 {data.recent_events.length > 0 ? (
                     <div className="space-y-4">
                         {data.recent_events.map((ev: any, i: number) => (
                             <div key={i} className="flex justify-between items-center bg-slate-900 p-4 rounded border border-slate-800 font-mono text-sm">
                                 <span className="text-slate-500">{new Date(ev.timestamp).toLocaleString()}</span>
                                 <span className="text-slate-300">{ev.swing.club.toUpperCase()} • {ev.swing.ball_speed} mph</span>
                                 <span className="text-emerald-400">{ev.outcome.carry}y Carry</span>
                                 <span className={`text-sky-400 ${!ev.outcome.fairway && 'text-rose-400'}`}>
                                     {ev.outcome.fairway ? 'Fairway' : ev.outcome.miss_pattern.toUpperCase()}
                                 </span>
                             </div>
                         ))}
                     </div>
                 ) : (
                     <div className="text-slate-500 text-sm italic py-4">No recent events recorded in Digital Twin.</div>
                 )}
             </div>
          </div>
      ) : (
        <div className="text-slate-500 animate-pulse italic mt-8">Player has not recorded any Digital Twin data yet. Provide ingestion payload.</div>
      )}
    </main>
  );
}
