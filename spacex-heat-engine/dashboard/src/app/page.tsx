"use client"
import React, { useEffect, useMemo, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, Tooltip, CartesianGrid, ZAxis } from "recharts";

const WS_BASE = process.env.NEXT_PUBLIC_WS_BASE || "ws://localhost:8000/ws/stream";

export default function Dashboard() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("Connecting...");

  useEffect(() => {
    let ws: WebSocket;

    const connect = () => {
        ws = new WebSocket(WS_BASE);

        ws.onopen = () => {
            console.log("WebSocket connected");
            setStatus("Live (Stream)");
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === "leaderboard_update") {
                    setData(msg.data);
                    setLoading(false);
                }
            } catch (err) {
                console.error("Error parsing websocket message", err);
            }
        };

        ws.onclose = () => {
            console.log("WebSocket disconnected, reconnecting in 3s...");
            setStatus("Disconnected");
            setTimeout(connect, 3000);
        };

        ws.onerror = (err) => {
            console.error("WebSocket error", err);
        };
    };

    connect();

    return () => {
        if (ws) ws.close();
    };
  }, []);

  const sortedByHeat = useMemo(() => {
    return [...data].sort((a, b) => (b.hi || 0) - (a.hi || 0));
  }, [data]);

  if (loading) {
    return <div className="p-6 flex items-center justify-center min-h-screen bg-[#0a0a0a] text-xl text-emerald-400">Loading SpaceZ Command Center...</div>;
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case "ANCHOR": return "#3b82f6";
      case "DISRUPTOR": return "#ef4444";
      case "CONVERTER": return "#10b981";
      case "PRESTIGE": return "#8b5cf6";
      case "AMPLIFIER": return "#f59e0b";
      default: return "#94a3b8";
    }
  }

  return (
    <div className="p-8 grid gap-8 min-h-screen bg-[#0a0a0a] text-slate-200">
      <div className="flex justify-between items-end border-b border-slate-800 pb-4">
        <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">SpaceZ Command Center</h1>
            <p className="text-slate-500 mt-2">Heat & Attention OS (Golf Focus)</p>
        </div>
        <div className="flex items-center space-x-2">
            <span className="relative flex h-3 w-3">
              {status === "Live (Stream)" && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
              <span className={`relative inline-flex rounded-full h-3 w-3 ${status === 'Live (Stream)' ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
            </span>
            <span className={`text-sm ${status === 'Live (Stream)' ? 'text-slate-400' : 'text-red-400'}`}>{status}</span>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
          <Card className="bg-[#121212] border-slate-800 shadow-xl overflow-hidden">
            <div className="bg-slate-900/50 p-4 border-b border-slate-800">
                <h2 className="text-xl font-semibold text-slate-100">Live Heat Leaderboard</h2>
            </div>
            <CardContent className="p-0">
              <Table>
                <TableHeader className="bg-slate-900/20">
                  <TableRow className="border-slate-800 hover:bg-transparent">
                    <TableHead className="text-slate-400">Player</TableHead>
                    <TableHead className="text-slate-400">Role</TableHead>
                    <TableHead className="text-right text-slate-400">Avg Heat Index</TableHead>
                    <TableHead className="text-right text-slate-400">Avg CES</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedByHeat.map((p, idx) => (
                    <TableRow key={idx} className="border-slate-800 hover:bg-slate-800/50 transition-colors">
                      <TableCell className="font-medium">{p.name}</TableCell>
                      <TableCell>
                          <span className="px-2 py-1 rounded text-xs font-medium bg-opacity-20" style={{ color: getRoleColor(p.role), backgroundColor: `${getRoleColor(p.role)}33` }}>
                              {p.role}
                          </span>
                      </TableCell>
                      <TableCell className="text-right font-mono text-emerald-400">{Number(p.hi || 0).toFixed(2)}</TableCell>
                      <TableCell className="text-right font-mono text-cyan-400">{Number(p.ces || 0).toFixed(2)}</TableCell>
                    </TableRow>
                  ))}
                  {sortedByHeat.length === 0 && (
                      <TableRow>
                          <TableCell colSpan={4} className="text-center text-slate-500 py-8">Waiting for events...</TableCell>
                      </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <Card className="bg-[#121212] border-slate-800 shadow-xl overflow-hidden">
             <div className="bg-slate-900/50 p-4 border-b border-slate-800">
                 <h2 className="text-xl font-semibold text-slate-100">Heat vs CES Matrix</h2>
             </div>
            <CardContent className="p-6">
              <div className="h-[400px] w-full flex items-center justify-center text-slate-500">
                  {sortedByHeat.length === 0 ? "Not enough data yet." :
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis
                          type="number"
                          dataKey="hi"
                          name="Heat Index"
                          tick={{ fill: '#94a3b8' }}
                          axisLine={{ stroke: '#475569' }}
                          label={{ value: "Heat Index (Attention)", position: 'insideBottom', offset: -10, fill: '#cbd5e1' }}
                      />
                      <YAxis
                          type="number"
                          dataKey="ces"
                          name="CES"
                          tick={{ fill: '#94a3b8' }}
                          axisLine={{ stroke: '#475569' }}
                          label={{ value: "Conversion Efficiency Score (Revenue)", angle: -90, position: 'insideLeft', offset: 0, fill: '#cbd5e1' }}
                      />
                      <ZAxis type="category" dataKey="name" name="Player" />
                      <Tooltip
                          cursor={{ strokeDasharray: "3 3" }}
                          contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                      />
                      {sortedByHeat.map((entry, index) => (
                          <Scatter key={`scatter-${index}`} name={entry.name} data={[entry]} fill={getRoleColor(entry.role)} />
                      ))}
                    </ScatterChart>
                  </ResponsiveContainer>}
              </div>
            </CardContent>
          </Card>
      </div>
    </div>
  );
}
