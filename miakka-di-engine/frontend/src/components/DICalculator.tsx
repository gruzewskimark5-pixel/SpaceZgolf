import React, { useState } from 'react';
import { Activity, ArrowDownRight, ArrowUpRight, Crosshair, Flag, BrainCircuit, ActivitySquare } from 'lucide-react';

interface DIResponse {
  overall_di: number;
  hole_breakdown: HoleBreakdown[];
}

interface HoleBreakdown {
  hole: number;
  di: number;
  vs_baseline: number;
  execution_component: number;
  decision_component: number;
  score: number;
  par: number;
}

export const DICalculator = () => {
  const [loading, setLoading] = useState(false);
  const [diData, setDiData] = useState<DIResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [scores, setScores] = useState(
    Array.from({ length: 18 }, (_, i) => ({ hole: i + 1, score: 4 }))
  );

  const handleScoreChange = (hole: number, score: number) => {
    setScores(scores.map(s => s.hole === hole ? { ...s, score } : s));
  };

  const calculateDI = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8001/api/rounds/calculate-di', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          course_id: 'miakka',
          scores: scores
        })
      });

      if (!response.ok) {
        throw new Error('Failed to calculate DI');
      }

      const data = await response.json();
      setDiData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Input Section */}
      <section className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl">
        <h2 className="text-xl font-semibold mb-6 flex items-center text-gray-200">
          <Flag className="w-5 h-5 mr-3 text-emerald-500" />
          Miakka Round Calibration
        </h2>

        <div className="grid grid-cols-6 gap-4 mb-8">
          {scores.map((score) => (
            <div key={score.hole} className="bg-gray-800/50 p-3 rounded-lg border border-gray-700/50 flex flex-col items-center">
              <span className="text-xs text-gray-400 font-medium mb-2">HOLE {score.hole}</span>
              <input
                type="number"
                min="1"
                max="10"
                value={score.score}
                onChange={(e) => handleScoreChange(score.hole, parseInt(e.target.value) || 4)}
                className="w-12 h-10 bg-gray-950 border border-gray-700 rounded text-center text-lg text-white focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none transition-all"
              />
            </div>
          ))}
        </div>

        <button
          onClick={calculateDI}
          disabled={loading}
          className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 flex justify-center items-center shadow-lg shadow-emerald-900/20"
        >
          {loading ? (
            <span className="flex items-center">
              <Activity className="w-5 h-5 mr-2 animate-spin" />
              Calibrating Engine...
            </span>
          ) : (
            <span className="flex items-center">
              <ActivitySquare className="w-5 h-5 mr-2" />
              Calculate DI Signatures
            </span>
          )}
        </button>

        {error && (
          <div className="mt-4 p-4 bg-red-900/20 border border-red-900/50 text-red-400 rounded-lg text-sm">
            {error}
          </div>
        )}
      </section>

      {/* Results Section */}
      {diData && (
        <section className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Overall DI Banner */}
          <div className="bg-gradient-to-br from-emerald-900/40 to-gray-900 border border-emerald-800/50 rounded-xl p-8 flex items-center justify-between shadow-xl">
            <div>
              <h3 className="text-sm font-semibold text-emerald-400 tracking-wider mb-1">AGGREGATE CALIBRATION</h3>
              <p className="text-gray-400 text-sm">Course-level difficulty index.</p>
            </div>
            <div className="text-5xl font-bold text-white drop-shadow-md flex items-baseline">
              {diData.overall_di.toFixed(1)}
              <span className="text-xl text-gray-500 ml-2 font-medium">DI</span>
            </div>
          </div>

          {/* Breakdown Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {diData.hole_breakdown.map((hole) => (
              <div key={hole.hole} className="bg-gray-900 border border-gray-800 rounded-lg p-5 shadow-lg relative overflow-hidden group hover:border-emerald-800 transition-colors">
                <div className="absolute top-0 right-0 p-3 opacity-20 group-hover:opacity-40 transition-opacity">
                  <span className="text-6xl font-black italic text-gray-700">{hole.hole}</span>
                </div>

                <div className="relative z-10">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Hole {hole.hole}</span>
                      <div className="text-2xl font-bold text-gray-100 mt-1">{hole.di.toFixed(1)}</div>
                    </div>

                    <div className={`flex items-center text-sm font-medium px-2 py-1 rounded-full ${
                      hole.vs_baseline > 0
                        ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    }`}>
                      {hole.vs_baseline > 0 ? <ArrowUpRight className="w-4 h-4 mr-1" /> : <ArrowDownRight className="w-4 h-4 mr-1" />}
                      {Math.abs(hole.vs_baseline).toFixed(1)}
                    </div>
                  </div>

                  <div className="space-y-3 border-t border-gray-800/80 pt-4 mt-2">
                    <div className="flex justify-between items-center text-sm">
                      <span className="flex items-center text-gray-400">
                        <Crosshair className="w-4 h-4 mr-2 text-blue-400" />
                        Execution
                      </span>
                      <span className="text-gray-200 font-medium">{hole.execution_component.toFixed(1)}</span>
                    </div>

                    <div className="flex justify-between items-center text-sm">
                      <span className="flex items-center text-gray-400">
                        <BrainCircuit className="w-4 h-4 mr-2 text-purple-400" />
                        Decision
                      </span>
                      <span className="text-gray-200 font-medium">{hole.decision_component.toFixed(1)}</span>
                    </div>

                    <div className="flex justify-between items-center text-sm pt-2 border-t border-gray-800/40">
                       <span className="text-gray-500">Score vs Par</span>
                       <span className="text-gray-300 font-medium">{hole.score} / {hole.par}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
