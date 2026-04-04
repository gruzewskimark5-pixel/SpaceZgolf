"use client";


import { DICalculator } from '@/components/DICalculator';

export default function Home() {
  return (
    <main className="min-h-screen p-8 bg-gray-950 text-gray-100">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="border-b border-gray-800 pb-6">
          <h1 className="text-3xl font-bold text-white tracking-tight">
            zMindPumpZ Miakka
            <span className="text-emerald-500 ml-2 text-xl font-medium tracking-normal">DI Calibration Engine</span>
          </h1>
          <p className="text-gray-400 mt-2">Real-time Difficulty Index calibration and telemetry feed.</p>
        </header>

        <DICalculator />
      </div>
    </main>
  );
}
