"use client"
import React, { useState, useMemo, useRef, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ReferenceDot } from "recharts";

const WS_SIM_URL = process.env.NEXT_PUBLIC_WS_SIM_URL || "ws://localhost:8000/ws/simulate";

export default function SimulationDashboard() {
  const [runs, setRuns] = useState<Record<string, { policy: any, events: any[] }>>({});
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [comparisonRunId, setComparisonRunId] = useState<string | null>(null);

  const [scrubberIndex, setScrubberIndex] = useState<number>(0);
  const [simStatus, setSimStatus] = useState("Idle");

  const [policy, setPolicy] = useState({
    heat_threshold_anchor: 3.0,
    heat_threshold_camera: 3.8,
    chaos_velocity_threshold: -0.15,
    ces_threshold: 0.9,
    chaos_probability: 0.7
  });

  const wsRef = useRef<WebSocket | null>(null);

  const startSimulation = () => {
    if (wsRef.current) wsRef.current.close();

    setSimStatus("Connecting...");
    const ws = new WebSocket(WS_SIM_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setSimStatus("Running");
      ws.send(JSON.stringify(policy));
    };

    let currentRunId = "";

    ws.onmessage = (msgEvent) => {
      const msg = JSON.parse(msgEvent.data);

      if (msg.type === "SIM_START") {
          currentRunId = msg.run_id;
          setActiveRunId(currentRunId);
          setRuns(prev => ({
              ...prev,
              [currentRunId]: { policy: msg.policy, events: [] }
          }));
          setScrubberIndex(0);
      }
      else if (msg.type === "SIM_EVENT") {
          setRuns(prev => {
              const updatedRun = { ...prev[currentRunId] };
              updatedRun.events = [...updatedRun.events, msg.data];
              return { ...prev, [currentRunId]: updatedRun };
          });
          // Auto-advance scrubber if we are at the end
          setScrubberIndex(curr => curr + 1);
      }
      else if (msg.type === "SIM_COMPLETE") {
          setSimStatus("Complete");
      }
    };

    ws.onclose = () => {
        if (simStatus === "Running") setSimStatus("Disconnected");
    }
  };

  const activeEvents = activeRunId && runs[activeRunId] ? runs[activeRunId].events : [];
  const compEvents = comparisonRunId && runs[comparisonRunId] ? runs[comparisonRunId].events : [];

  // Scrubber limits
  const maxIndex = Math.max(0, activeEvents.length - 1);
  const safeIndex = Math.min(scrubberIndex, maxIndex);
  const currentFrame = activeEvents[safeIndex] || null;

  return (
    <div className="p-8 grid gap-8 min-h-screen bg-[#0a0a0a] text-slate-200">
      <div className="flex justify-between items-end border-b border-slate-800 pb-4">
        <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">SpaceZ Simulator OS</h1>
            <p className="text-slate-500 mt-2">Director Brain Policy Testing & Replay Workbench</p>
        </div>
        <div className="flex items-center space-x-2">
            <span className={`text-sm ${simStatus === 'Running' ? 'text-emerald-400' : 'text-slate-500'}`}>{simStatus}</span>
        </div>
      </div>

      <div className="grid lg:grid-cols-4 gap-8">

          {/* Policy Controls Panel */}
          <Card className="bg-[#121212] border-slate-800 shadow-xl overflow-hidden lg:col-span-1">
             <div className="bg-slate-900/50 p-4 border-b border-slate-800">
                 <h2 className="text-xl font-semibold text-slate-100">Director Policy Limits</h2>
             </div>
             <CardContent className="p-6 flex flex-col gap-4">
                <div>
                    <label className="text-xs text-slate-400 uppercase tracking-wider mb-1 block flex justify-between">
                        <span>Anchor Amplification</span>
                        <span className="text-emerald-400">{policy.heat_threshold_anchor}</span>
                    </label>
                    <input
                        type="range" min="1.0" max="5.0" step="0.1"
                        value={policy.heat_threshold_anchor}
                        onChange={(e) => setPolicy({...policy, heat_threshold_anchor: parseFloat(e.target.value)})}
                        className="w-full accent-emerald-500"
                    />
                </div>
                <div>
                    <label className="text-xs text-slate-400 uppercase tracking-wider mb-1 block flex justify-between">
                        <span>Multi-Angle Camera (Proj)</span>
                        <span className="text-sky-400">{policy.heat_threshold_camera}</span>
                    </label>
                    <input
                        type="range" min="1.0" max="5.0" step="0.1"
                        value={policy.heat_threshold_camera}
                        onChange={(e) => setPolicy({...policy, heat_threshold_camera: parseFloat(e.target.value)})}
                        className="w-full accent-sky-500"
                    />
                </div>
                <div>
                    <label className="text-xs text-slate-400 uppercase tracking-wider mb-1 block flex justify-between">
                        <span>Chaos Injection (Vel Drop)</span>
                        <span className="text-rose-400">{policy.chaos_velocity_threshold}</span>
                    </label>
                    <input
                        type="range" min="-1.0" max="0.0" step="0.05"
                        value={policy.chaos_velocity_threshold}
                        onChange={(e) => setPolicy({...policy, chaos_velocity_threshold: parseFloat(e.target.value)})}
                        className="w-full accent-rose-500"
                    />
                </div>
                <div>
                    <label className="text-xs text-slate-400 uppercase tracking-wider mb-1 block flex justify-between">
                        <span>Chaos Trigger Probability</span>
                        <span className="text-purple-400">{policy.chaos_probability}</span>
                    </label>
                    <input
                        type="range" min="0.0" max="1.0" step="0.1"
                        value={policy.chaos_probability}
                        onChange={(e) => setPolicy({...policy, chaos_probability: parseFloat(e.target.value)})}
                        className="w-full accent-purple-500"
                    />
                </div>
                <div>
                    <label className="text-xs text-slate-400 uppercase tracking-wider mb-1 block flex justify-between">
                        <span>CES Optimization (Min)</span>
                        <span className="text-amber-400">{policy.ces_threshold}</span>
                    </label>
                    <input
                        type="range" min="0.1" max="2.0" step="0.1"
                        value={policy.ces_threshold}
                        onChange={(e) => setPolicy({...policy, ces_threshold: parseFloat(e.target.value)})}
                        className="w-full accent-amber-500"
                    />
                </div>

                <button
                    onClick={startSimulation}
                    disabled={simStatus === "Running"}
                    className="mt-4 w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2 px-4 rounded transition-colors disabled:opacity-50"
                >
                    {simStatus === "Running" ? "Simulating..." : "Run Policy Simulation"}
                </button>
             </CardContent>
          </Card>

          {/* Timeline & Replay Scrubber */}
          <div className="lg:col-span-3 grid gap-8">
              <Card className="bg-[#121212] border-slate-800 shadow-xl overflow-hidden">
                 <div className="bg-slate-900/50 p-4 border-b border-slate-800 flex justify-between items-center">
                     <h2 className="text-xl font-semibold text-slate-100">Live Simulation Run & Forecasting</h2>
                     <div className="flex gap-4">
                         {Object.keys(runs).length > 1 && (
                            <select
                                className="bg-slate-800 border-slate-700 text-slate-200 rounded px-2 py-1 text-sm"
                                value={comparisonRunId || ""}
                                onChange={(e) => setComparisonRunId(e.target.value)}
                            >
                                <option value="">No Comparison</option>
                                {Object.keys(runs).map(rid => (
                                    rid !== activeRunId && <option key={rid} value={rid}>Run: {rid.split('-')[0]}</option>
                                ))}
                            </select>
                         )}
                         <span className="text-sm font-mono text-emerald-400">
                           Step: t={safeIndex}
                         </span>
                     </div>
                 </div>
                 <CardContent className="p-6">
                    <div className="h-[300px] w-full mb-6 relative">
                      {activeEvents.length === 0 ? (
                          <div className="h-full w-full flex items-center justify-center text-slate-500">Run a simulation to view heat curves...</div>
                      ) : (
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart margin={{ top: 20, right: 20, bottom: 5, left: 0 }}>
                            <CartesianGrid stroke="#334155" strokeDasharray="3 3" vertical={false} />
                            <XAxis dataKey="t" type="number" domain={[0, 'dataMax']} stroke="#475569" tick={{fill: '#94a3b8', fontSize: 12}} />
                            <YAxis stroke="#475569" tick={{fill: '#94a3b8', fontSize: 12}} domain={[0, 6]} />
                            <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />

                            {/* Comparison Line (faded) */}
                            {compEvents.length > 0 && (
                                <Line data={compEvents} type="monotone" dataKey="heat" name="Run B Heat" stroke="#64748b" strokeWidth={2} dot={false} strokeOpacity={0.5} isAnimationActive={false} />
                            )}

                            {/* Active Line */}
                            <Line data={activeEvents} type="monotone" dataKey="heat" name="Current Heat" stroke="#10b981" strokeWidth={3} dot={false} isAnimationActive={false} />
                            <Line data={activeEvents} type="monotone" dataKey="projected" name="Projected (30s)" stroke="#0ea5e9" strokeWidth={2} strokeDasharray="4 4" dot={false} isAnimationActive={false} />

                            {/* Chaos Markers */}
                            {activeEvents.map((ev, i) => (
                                ev.actions.includes("CHAOS_INJECTION") && (
                                    <ReferenceDot key={`chaos-${i}`} x={ev.t} y={ev.heat} r={5} fill="#ef4444" stroke="none" />
                                )
                            ))}
                            {/* Anchor Markers */}
                            {activeEvents.map((ev, i) => (
                                ev.actions.includes("ANCHOR_AMPLIFICATION") && (
                                    <ReferenceDot key={`anchor-${i}`} x={ev.t} y={ev.heat} r={4} fill="#8b5cf6" stroke="none" />
                                )
                            ))}

                            {/* Scrubber Time Marker */}
                            {currentFrame && (
                                <ReferenceDot x={currentFrame.t} y={currentFrame.heat} r={6} fill="#10b981" stroke="#fff" strokeWidth={2} />
                            )}
                          </LineChart>
                        </ResponsiveContainer>
                      )}
                    </div>

                    {/* Synchronized Replay Scrubber */}
                    <div className="flex flex-col gap-2 bg-slate-900 p-4 rounded-lg border border-slate-800">
                       <div className="flex justify-between text-xs text-slate-500 font-mono">
                         <span>t=0</span>
                         <span>Timeline Scrubber</span>
                         <span>t={Math.max(0, activeEvents.length - 1)}</span>
                       </div>
                       <input
                          type="range"
                          min="0"
                          max={Math.max(0, activeEvents.length - 1)}
                          value={safeIndex}
                          onChange={(e) => setScrubberIndex(Number(e.target.value))}
                          className="w-full accent-emerald-500"
                          disabled={activeEvents.length === 0}
                       />
                    </div>
                 </CardContent>
              </Card>

              {/* Action Inspector Panel */}
              <div className="grid md:grid-cols-2 gap-8">
                  <Card className="bg-[#121212] border-slate-800 shadow-xl overflow-hidden">
                    <div className="bg-slate-900/50 p-4 border-b border-slate-800">
                        <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full bg-cyan-500"></span>
                            Frame Inspector
                        </h2>
                    </div>
                    <CardContent className="p-4">
                        {currentFrame ? (
                            <div className="space-y-4 font-mono text-sm">
                                <div className="flex justify-between border-b border-slate-800 pb-2">
                                    <span className="text-slate-500">Heat Index</span>
                                    <span className="text-emerald-400 font-bold">{currentFrame.heat.toFixed(3)}</span>
                                </div>
                                <div className="flex justify-between border-b border-slate-800 pb-2">
                                    <span className="text-slate-500">Projected Heat</span>
                                    <span className="text-sky-400 font-bold">{currentFrame.projected.toFixed(3)}</span>
                                </div>
                                <div className="flex justify-between border-b border-slate-800 pb-2">
                                    <span className="text-slate-500">Velocity (Δ)</span>
                                    <span className={`${currentFrame.velocity < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                                        {currentFrame.velocity > 0 ? "+" : ""}{currentFrame.velocity.toFixed(3)}
                                    </span>
                                </div>
                                <div className="flex justify-between border-b border-slate-800 pb-2">
                                    <span className="text-slate-500">CES (Monetization)</span>
                                    <span className="text-amber-400">{currentFrame.ces.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-500">Anchor Present</span>
                                    <span className={`${currentFrame.anchor ? 'text-purple-400' : 'text-slate-600'}`}>
                                        {currentFrame.anchor ? "TRUE" : "FALSE"}
                                    </span>
                                </div>
                            </div>
                        ) : (
                            <div className="text-slate-500 italic text-sm">Select a frame on the timeline.</div>
                        )}
                    </CardContent>
                  </Card>

                  <Card className="bg-[#121212] border-slate-800 shadow-xl overflow-hidden">
                    <div className="bg-slate-900/50 p-4 border-b border-slate-800">
                        <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full bg-rose-500 animate-pulse"></span>
                            Director Brain Actions
                        </h2>
                    </div>
                    <CardContent className="p-4 h-[200px] overflow-y-auto">
                      {currentFrame && currentFrame.actions.length > 0 ? (
                         <div className="flex flex-col gap-3">
                             {currentFrame.actions.map((act: string, idx: number) => {
                                 let color = "text-slate-300 bg-slate-800";
                                 if (act.includes("CHAOS")) color = "text-rose-100 bg-rose-900 border border-rose-500";
                                 if (act.includes("ANCHOR")) color = "text-purple-100 bg-purple-900 border border-purple-500";
                                 if (act.includes("CAMERA")) color = "text-sky-100 bg-sky-900 border border-sky-500";
                                 if (act.includes("CES")) color = "text-amber-100 bg-amber-900 border border-amber-500";

                                 return (
                                     <div key={idx} className={`p-2 rounded text-xs font-bold font-mono tracking-wider ${color}`}>
                                         [EXEC] {act}
                                     </div>
                                 )
                             })}
                         </div>
                      ) : (
                         <div className="text-slate-500 italic text-sm">Monitoring baseline. No policy triggered at this moment.</div>
                      )}
                    </CardContent>
                  </Card>
              </div>

          </div>
      </div>
    </div>
  );
}
