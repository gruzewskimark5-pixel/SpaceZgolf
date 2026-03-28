"use client"
import React, { useState, useMemo, useRef, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ReferenceDot, AreaChart, Area } from "recharts";

const WS_SIM_URL = process.env.NEXT_PUBLIC_WS_SIM_URL || "ws://localhost:8000/ws/simulate";
const WS_OPT_URL = process.env.NEXT_PUBLIC_WS_OPT_URL || "ws://localhost:8000/ws/optimize";
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

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

  // Optimizer State
  const [optStatus, setOptStatus] = useState("Idle");
  const [optHistory, setOptHistory] = useState<any[]>([]);
  const [bestPolicy, setBestPolicy] = useState<any>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const optWsRef = useRef<WebSocket | null>(null);

  // Initial load of runs
  useEffect(() => {
    fetch(`${API_BASE}/runs`)
      .then(res => res.json())
      .then(async data => {
        const mapped: any = {};
        for (const r of data) {
            // Need to fetch full run details for events
            try {
                const resDetails = await fetch(`${API_BASE}/runs/${r.run_id}`);
                const details = await resDetails.json();
                mapped[r.run_id] = details;
            } catch(e) {}
        }
        setRuns(mapped);
      })
      .catch(err => console.error("Error fetching initial runs:", err));
  }, []);

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

  const saveSimulationRun = async () => {
    try {
      setSimStatus("Saving...");
      const res = await fetch(`${API_BASE}/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(policy)
      });
      const data = await res.json();

      // Fetch full details
      const resDetails = await fetch(`${API_BASE}/runs/${data.run_id}`);
      const details = await resDetails.json();

      setRuns(prev => ({ ...prev, [data.run_id]: details }));
      setActiveRunId(data.run_id);
      setScrubberIndex(0);
      setSimStatus("Saved");
      setTimeout(() => setSimStatus("Idle"), 2000);
    } catch(err) {
      console.error(err);
      setSimStatus("Error Saving");
    }
  };

  const startOptimization = () => {
    if (optWsRef.current) optWsRef.current.close();
    setOptHistory([]);
    setBestPolicy(null);
    setOptStatus("Connecting...");

    const ws = new WebSocket(WS_OPT_URL);
    optWsRef.current = ws;

    ws.onopen = () => {
      setOptStatus("Optimizing");
      ws.send(JSON.stringify({
          population_size: 20,
          generations: 15,
          mutation_rate: 0.15
      }));
    };

    ws.onmessage = (msgEvent) => {
      const msg = JSON.parse(msgEvent.data);

      if (msg.type === "OPT_PROGRESS") {
          setOptHistory(prev => [...prev, msg.data]);
      }
      else if (msg.type === "OPT_COMPLETE") {
          setOptStatus("Complete");
          setBestPolicy(msg.best_policy);
      }
    };
  };

  const applyOptimizedPolicy = () => {
      if (bestPolicy) {
          setPolicy(bestPolicy);
          alert("Optimal Policy Loaded into Workbench.");
      }
  };

  const activeEvents = activeRunId && runs[activeRunId] ? runs[activeRunId].events : [];
  const compEvents = comparisonRunId && runs[comparisonRunId] ? runs[comparisonRunId].events : [];

  // Scrubber limits synchronized
  const maxIndex = Math.min(
      activeEvents.length > 0 ? activeEvents.length - 1 : 0,
      compEvents.length > 0 ? compEvents.length - 1 : (activeEvents.length > 0 ? activeEvents.length - 1 : 0)
  );
  const safeIndex = Math.min(scrubberIndex, maxIndex);

  const currentFrame = activeEvents[safeIndex] || null;

  // Comparative Metrics Helper
  const getMetrics = (events: any[]) => {
      if (!events || !events.length) return { avgHeat: 0, avgCES: 0, chaosCount: 0 };
      const avgHeat = events.reduce((a,b)=>a+b.heat,0)/events.length;
      const avgCES = events.reduce((a,b)=>a+b.ces,0)/events.length;
      const chaosCount = events.filter(e => e.actions.includes("CHAOS_INJECTION")).length;
      return { avgHeat: avgHeat.toFixed(2), avgCES: avgCES.toFixed(2), chaosCount };
  };

  const actMetrics = getMetrics(activeEvents);
  const compMetrics = getMetrics(compEvents);

  // Semantic Diff Helper
  const diffPolicy = (a: any, b: any) => {
    if (!a || !b) return [];
    return Object.keys(a).map(k => {
      const delta = b[k] - a[k];
      let impact = "Neutral";
      if (k === "chaos_probability" || k === "heat_threshold_camera") {
          impact = delta > 0 ? "More Aggressive" : "More Conservative";
      } else if (k === "chaos_velocity_threshold") {
          impact = delta > 0 ? "More Trigger Happy" : "More Resistant";
      } else {
          impact = delta > 0 ? "Stricter" : "Looser";
      }

      return {
        key: k,
        a: a[k].toFixed(2),
        b: b[k].toFixed(2),
        delta: delta.toFixed(2),
        impact: delta === 0 ? "Unchanged" : impact
      };
    });
  };

  const policyDiffs = activeRunId && comparisonRunId ? diffPolicy(runs[activeRunId].policy, runs[comparisonRunId].policy) : [];

  return (
    <div className="p-8 grid gap-8 min-h-screen bg-[#0a0a0a] text-slate-200">
      <div className="flex justify-between items-end border-b border-slate-800 pb-4">
        <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">SpaceZ Operator Intelligence</h1>
            <p className="text-slate-500 mt-2">Self-Improving Director Policy System</p>
        </div>
        <div className="flex items-center space-x-2">
            <span className={`text-sm ${simStatus === 'Running' || optStatus === 'Optimizing' ? 'text-emerald-400' : 'text-slate-500'}`}>
                System: {optStatus === 'Optimizing' ? 'Optimizing' : simStatus}
            </span>
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
                        <span>Multi-Angle Camera</span>
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
                        <span>Chaos Vel Trigger</span>
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
                        <span>Chaos Prob (%)</span>
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
                        <span>CES Optimization</span>
                        <span className="text-amber-400">{policy.ces_threshold}</span>
                    </label>
                    <input
                        type="range" min="0.1" max="2.0" step="0.1"
                        value={policy.ces_threshold}
                        onChange={(e) => setPolicy({...policy, ces_threshold: parseFloat(e.target.value)})}
                        className="w-full accent-amber-500"
                    />
                </div>

                <div className="grid grid-cols-2 gap-2 mt-4">
                    <button
                        onClick={startSimulation}
                        disabled={simStatus === "Running"}
                        className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2 px-2 rounded transition-colors disabled:opacity-50 text-xs"
                    >
                        {simStatus === "Running" ? "Simulating..." : "▶ Live Stream"}
                    </button>
                    <button
                        onClick={saveSimulationRun}
                        disabled={simStatus === "Running" || simStatus === "Saving..."}
                        className="w-full bg-sky-600 hover:bg-sky-500 text-white font-semibold py-2 px-2 rounded transition-colors disabled:opacity-50 text-xs"
                    >
                        💾 Save Run
                    </button>
                </div>
             </CardContent>
          </Card>

          {/* Timeline & Replay Scrubber */}
          <div className="lg:col-span-3 grid gap-8">
              <Card className="bg-[#121212] border-slate-800 shadow-xl overflow-hidden">
                 <div className="bg-slate-900/50 p-4 border-b border-slate-800 flex justify-between items-center">
                     <h2 className="text-xl font-semibold text-slate-100 flex items-center gap-4">
                         Simulation Run Analysis
                         <select
                                className="bg-slate-800 border-slate-700 text-emerald-400 rounded px-2 py-1 text-sm font-mono"
                                value={activeRunId || ""}
                                onChange={(e) => { setActiveRunId(e.target.value); setScrubberIndex(0); }}
                            >
                                <option value="">Select Run...</option>
                                {Object.keys(runs).map(rid => (
                                    <option key={rid} value={rid}>Run: {rid.split('-')[0]}</option>
                                ))}
                            </select>
                            <span className="text-slate-500 text-sm">vs</span>
                            <select
                                className="bg-slate-800 border-slate-700 text-sky-400 rounded px-2 py-1 text-sm font-mono"
                                value={comparisonRunId || ""}
                                onChange={(e) => { setComparisonRunId(e.target.value); setScrubberIndex(0); }}
                            >
                                <option value="">No Comparison</option>
                                {Object.keys(runs).map(rid => (
                                    rid !== activeRunId && <option key={rid} value={rid}>Run: {rid.split('-')[0]}</option>
                                ))}
                            </select>
                     </h2>
                 </div>

                 <CardContent className="p-6">
                    <div className="h-[300px] w-full mb-6 relative">
                      {activeEvents.length === 0 ? (
                          <div className="h-full w-full flex items-center justify-center text-slate-500">Select or create a run to view heat curves...</div>
                      ) : (
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart margin={{ top: 20, right: 20, bottom: 5, left: 0 }}>
                            <CartesianGrid stroke="#334155" strokeDasharray="3 3" vertical={false} />
                            <XAxis dataKey="t" type="number" domain={[0, 'dataMax']} stroke="#475569" tick={{fill: '#94a3b8', fontSize: 12}} />
                            <YAxis stroke="#475569" tick={{fill: '#94a3b8', fontSize: 12}} domain={[0, 6]} />
                            <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />

                            {/* Active Line */}
                            <Line data={activeEvents} type="monotone" dataKey="heat" name="Current Heat" stroke="#10b981" strokeWidth={3} dot={false} isAnimationActive={false} />

                            {/* Comparison Line */}
                            {compEvents.length > 0 && (
                                <Line data={compEvents} type="monotone" dataKey="heat" name="Run B Heat" stroke="#0ea5e9" strokeWidth={3} dot={false} strokeOpacity={0.8} isAnimationActive={false} />
                            )}

                            {/* Markers for Active Run */}
                            {activeEvents.map((ev, i) => (
                                ev.actions.includes("CHAOS_INJECTION") && (
                                    <ReferenceDot key={`chaos-${i}`} x={ev.t} y={ev.heat} r={5} fill="#ef4444" stroke="none" />
                                )
                            ))}
                            {activeEvents.map((ev, i) => (
                                ev.actions.includes("ANCHOR_AMPLIFICATION") && (
                                    <ReferenceDot key={`anchor-${i}`} x={ev.t} y={ev.heat} r={4} fill="#a855f7" stroke="none" />
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
                         <span>Synchronized Timeline Scrubber</span>
                         <span>t={maxIndex}</span>
                       </div>
                       <input
                          type="range"
                          min="0"
                          max={maxIndex}
                          value={safeIndex}
                          onChange={(e) => setScrubberIndex(Number(e.target.value))}
                          className="w-full accent-emerald-500"
                          disabled={activeEvents.length === 0}
                       />
                    </div>
                 </CardContent>
              </Card>

              {/* Comparative Metrics & Event Inspector Panel */}
              <div className="grid md:grid-cols-2 gap-8">
                  {/* Event Inspector */}
                  <Card className="bg-[#121212] border-slate-800 shadow-xl overflow-hidden">
                    <div className="bg-slate-900/50 p-4 border-b border-slate-800 flex justify-between">
                        <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full bg-cyan-500"></span>
                            Frame Inspector (t={safeIndex})
                        </h2>
                    </div>
                    <CardContent className="p-4 h-[250px] overflow-y-auto">
                        {currentFrame ? (
                            <div className="space-y-4 font-mono text-sm">
                                <div className="flex justify-between border-b border-slate-800 pb-2">
                                    <span className="text-slate-500">Heat Index</span>
                                    <span className="text-emerald-400 font-bold">{currentFrame.heat.toFixed(3)}</span>
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
                                <div className="mt-4 flex flex-col gap-2">
                                    <span className="text-slate-500 text-xs tracking-wider uppercase">Triggered Actions</span>
                                    {currentFrame.actions.length > 0 ? currentFrame.actions.map((act:string, i:number) => (
                                        <div key={i} className="text-slate-300 text-xs bg-slate-800 p-1 rounded inline-block w-max">
                                            [EXEC] {act}
                                        </div>
                                    )) : <span className="text-slate-600 text-xs italic">No actions triggered.</span>}
                                </div>
                            </div>
                        ) : (
                            <div className="text-slate-500 italic text-sm">Select a frame on the timeline.</div>
                        )}
                    </CardContent>
                  </Card>

                  {/* Comparative Metrics & Diff */}
                  <Card className="bg-[#121212] border-slate-800 shadow-xl overflow-hidden">
                    <div className="bg-slate-900/50 p-4 border-b border-slate-800">
                        <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full bg-indigo-500"></span>
                            Comparative Metrics
                        </h2>
                    </div>
                    <CardContent className="p-4 h-[250px] overflow-y-auto text-sm">
                        {activeRunId ? (
                            <>
                              <div className="grid grid-cols-3 gap-2 text-center border-b border-slate-800 pb-4 mb-4">
                                  <div>
                                      <div className="text-slate-500 text-xs mb-1">Avg Heat</div>
                                      <div className="text-emerald-400 font-mono text-lg">{actMetrics.avgHeat}</div>
                                      {comparisonRunId && <div className="text-sky-400 font-mono text-xs border-t border-slate-800 mt-1 pt-1">{compMetrics.avgHeat}</div>}
                                  </div>
                                  <div>
                                      <div className="text-slate-500 text-xs mb-1">Avg CES</div>
                                      <div className="text-amber-400 font-mono text-lg">{actMetrics.avgCES}</div>
                                      {comparisonRunId && <div className="text-sky-400 font-mono text-xs border-t border-slate-800 mt-1 pt-1">{compMetrics.avgCES}</div>}
                                  </div>
                                  <div>
                                      <div className="text-slate-500 text-xs mb-1">Chaos Count</div>
                                      <div className="text-rose-400 font-mono text-lg">{actMetrics.chaosCount}</div>
                                      {comparisonRunId && <div className="text-sky-400 font-mono text-xs border-t border-slate-800 mt-1 pt-1">{compMetrics.chaosCount}</div>}
                                  </div>
                              </div>

                              {comparisonRunId && policyDiffs.length > 0 && (
                                  <div>
                                      <div className="text-slate-500 text-xs uppercase tracking-wider mb-2">Semantic Policy Diff (Run B vs A)</div>
                                      <div className="space-y-2">
                                          {policyDiffs.map((diff, i) => (
                                              <div key={i} className="flex justify-between items-center bg-slate-900 p-2 rounded text-xs border border-slate-800">
                                                  <span className="text-slate-300 font-mono max-w-[120px] truncate" title={diff.key}>{diff.key.replace("heat_threshold_", "").replace("chaos_", "")}</span>
                                                  <span className="text-slate-500 font-mono">{diff.a} → {diff.b}</span>
                                                  <span className={`font-semibold ${diff.impact === 'Unchanged' ? 'text-slate-600' : 'text-indigo-400'}`}>
                                                      {diff.impact}
                                                  </span>
                                              </div>
                                          ))}
                                      </div>
                                  </div>
                              )}
                            </>
                        ) : (
                            <div className="text-slate-500 italic text-sm">Select an active run to view metrics.</div>
                        )}
                    </CardContent>
                  </Card>
              </div>
          </div>

          {/* Genetic Algorithm Optimizer View */}
          <Card className="bg-[#121212] border-slate-800 shadow-xl overflow-hidden lg:col-span-4 mt-8">
             <div className="bg-slate-900/50 p-4 border-b border-slate-800 flex justify-between items-center">
                 <h2 className="text-xl font-semibold text-slate-100 flex items-center gap-2">
                     <span className="h-3 w-3 rounded-full bg-purple-500 animate-pulse"></span>
                     Genetic Policy Optimizer (GA)
                 </h2>
                 <button
                     onClick={startOptimization}
                     disabled={optStatus === "Optimizing"}
                     className="bg-purple-600 hover:bg-purple-500 text-white font-semibold py-1 px-4 rounded transition-colors disabled:opacity-50 text-sm"
                 >
                     {optStatus === "Optimizing" ? "Evolving Generations..." : "Run GA Optimizer"}
                 </button>
             </div>
             <CardContent className="p-6">
                <div className="grid md:grid-cols-2 gap-8">
                    <div className="h-[250px] w-full">
                      {optHistory.length === 0 ? (
                          <div className="h-full w-full flex items-center justify-center text-slate-500 border border-slate-800 rounded bg-slate-900">Run Optimizer to view generational fitness evolution...</div>
                      ) : (
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={optHistory} margin={{ top: 5, right: 0, bottom: 5, left: 0 }}>
                            <defs>
                                <linearGradient id="colorFitness" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3}/>
                                  <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                                </linearGradient>
                            </defs>
                            <CartesianGrid stroke="#334155" strokeDasharray="3 3" vertical={false} />
                            <XAxis dataKey="generation" stroke="#475569" tick={{fill: '#94a3b8', fontSize: 12}} />
                            <YAxis stroke="#475569" tick={{fill: '#94a3b8', fontSize: 12}} domain={['dataMin - 0.5', 'dataMax + 0.5']} />
                            <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                            <Area type="monotone" dataKey="best_fitness" name="Best Fitness" stroke="#a855f7" strokeWidth={3} fillOpacity={1} fill="url(#colorFitness)" isAnimationActive={false} />
                            <Line data={optHistory} type="monotone" dataKey="avg_fitness" name="Avg Fitness" stroke="#cbd5e1" strokeWidth={1} dot={false} strokeDasharray="3 3" isAnimationActive={false} />
                          </AreaChart>
                        </ResponsiveContainer>
                      )}
                    </div>

                    <div className="bg-slate-900 border border-slate-800 rounded p-4 flex flex-col justify-between">
                        <div>
                            <h3 className="text-lg font-semibold text-purple-400 mb-4">Winning Policy (Tournament Best)</h3>
                            {bestPolicy ? (
                                <div className="grid grid-cols-2 gap-4 font-mono text-sm">
                                    <div><span className="text-slate-500 block text-xs">Anchor Trigger</span> <span className="text-slate-200">{bestPolicy.heat_threshold_anchor.toFixed(2)}</span></div>
                                    <div><span className="text-slate-500 block text-xs">Camera Trigger</span> <span className="text-slate-200">{bestPolicy.heat_threshold_camera.toFixed(2)}</span></div>
                                    <div><span className="text-slate-500 block text-xs">Chaos Vel Drop</span> <span className="text-slate-200">{bestPolicy.chaos_velocity_threshold.toFixed(2)}</span></div>
                                    <div><span className="text-slate-500 block text-xs">Chaos Prob</span> <span className="text-slate-200">{bestPolicy.chaos_probability.toFixed(2)}</span></div>
                                    <div><span className="text-slate-500 block text-xs">CES Floor</span> <span className="text-slate-200">{bestPolicy.ces_threshold.toFixed(2)}</span></div>
                                </div>
                            ) : (
                                <div className="text-slate-500 italic text-sm">Awaiting evolution results...</div>
                            )}
                        </div>
                        <button
                            onClick={applyOptimizedPolicy}
                            disabled={!bestPolicy}
                            className="w-full mt-4 bg-slate-800 hover:bg-slate-700 text-purple-400 border border-purple-500 font-semibold py-2 px-4 rounded transition-colors disabled:opacity-50"
                        >
                            Apply Winning Policy to Workbench
                        </button>
                    </div>
                </div>
             </CardContent>
          </Card>
      </div>
    </div>
  );
}
