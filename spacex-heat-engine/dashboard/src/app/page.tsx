export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-slate-950 text-slate-50">
      <h1 className="text-3xl font-semibold mb-4">Apex League Member Console</h1>
      <p className="text-slate-300 mb-6">
        Log in to see your rating, Heat, and Digital Twin.
      </p>

      <div className="flex gap-4">
          <a href="/dashboard" className="px-4 py-2 bg-emerald-600 rounded text-sm hover:bg-emerald-500 transition-colors">
              Access Dashboard (Mock Login)
          </a>
          <a href="/simulator" className="px-4 py-2 bg-slate-800 border border-slate-700 rounded text-sm hover:bg-slate-700 transition-colors">
              Operator Workspace
          </a>
      </div>
    </main>
  );
}
