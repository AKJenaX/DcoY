import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { Hexagon } from "../components/Hexagon";
import { SvgLineChart } from "../components/charts/SvgLineChart";
import { Activity, ShieldCheck, Database, ChevronDown, ChevronRight, Info, Cpu, Play, Trash2 } from "lucide-react";

interface HealthData {
  uptime_seconds: number;
  services: {
    fastapi_backend: string;
    sqlite_database: string;
    rule_engine: string;
    knowledge_graph: string;
    deception_agent: string;
    ai_copilot_service: string;
  };
  metrics: {
    average_latency_ms: number;
    cache_hits: number;
    cache_misses: number;
    cache_efficiency_pct: number;
    active_rules: number;
    enabled_rules: number;
    monitored_assets: number;
    graph_relationships: number;
  };
  latency_history: number[];
  websocket_connections: {
    telemetry: number;
    geolocation: number;
    simulation: number;
  };
  sqlite_lock_retries: {
    commit_retries: number;
    flush_retries: number;
  };
  copilot_source: "live" | "fallback";
}

export const PlatformHealth: React.FC = () => {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [docs, setDocs] = useState<any>(null);
  const [apiInventory, setApiInventory] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [demoActionLoading, setDemoActionLoading] = useState(false);
  const [demoMessage, setDemoMessage] = useState("");

  // Expander States
  const [openGuide, setOpenGuide] = useState(false);
  const [openER, setOpenER] = useState(false);
  const [openMermaid, setOpenMermaid] = useState(false);

  const fetchHealth = async () => {
    try {
      const hData = await api.getPlatformHealth();
      setHealth(hData);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to update platform metrics.");
    }
  };

  const fetchStaticDocs = async () => {
    try {
      const dData = await api.getPlatformDocs();
      setDocs(dData);
      const invData = await api.getApiInventory();
      setApiInventory(invData);
    } catch (err) {
      console.error("Failed to load platform document assets", err);
    }
  };

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await Promise.all([fetchHealth(), fetchStaticDocs()]);
      setLoading(false);
    };
    init();

    // Set polling interval for health metrics
    const interval = setInterval(fetchHealth, 8000);
    return () => clearInterval(interval);
  }, []);

  const triggerDemo = async () => {
    setDemoActionLoading(true);
    setDemoMessage("");
    try {
      await api.triggerDemoAttack();
      setDemoMessage("Demo attack scenario successfully triggered.");
      fetchHealth();
    } catch (err: any) {
      setDemoMessage(`Error: ${err.message || "Failed to trigger"}`);
    } finally {
      setDemoActionLoading(false);
    }
  };

  const clearDemo = async () => {
    setDemoActionLoading(true);
    setDemoMessage("");
    try {
      await api.clearDemoTelemetry();
      setDemoMessage("Demo telemetry logs cleared.");
      fetchHealth();
    } catch (err: any) {
      setDemoMessage(`Error: ${err.message || "Failed to clear"}`);
    } finally {
      setDemoActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-cyan-400 font-mono text-xs">
        <Activity className="w-8 h-8 animate-spin mb-2" />
        INITIALIZING OBSERVABILITY TELEMETRY...
      </div>
    );
  }

  // Format uptime
  const formatUptime = (sec: number) => {
    const hrs = Math.floor(sec / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    return `${hrs}h ${mins}m ${sec % 60}s`;
  };

  const metrics = health?.metrics || {
    average_latency_ms: 0,
    cache_efficiency_pct: 0,
    cache_hits: 0,
    cache_misses: 0,
    enabled_rules: 0,
    active_rules: 0,
    monitored_assets: 0,
    graph_relationships: 0
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-[#202020]/40 pb-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Activity className="w-6 h-6 text-cyan-400" />
            Platform Diagnostics & Health
          </h1>
          <p className="text-sm text-gray-400">Observability middleware latency metrics, database health, and API catalog</p>
        </div>
        <div className="text-xs font-mono bg-[#050b14]/80 px-3 py-1.5 border border-gray-800 rounded text-gray-400">
          SYSTEM UP: <span className="text-green-400 font-bold">{health ? formatUptime(health.uptime_seconds) : "0s"}</span>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-950/20 border border-red-500/50 rounded-md text-red-400 text-xs font-mono">
          [WARNING] {error}
        </div>
      )}

      {/* Hex KPIs Dashboard grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 justify-items-center py-1 perspective-container w-full">
        <div className="tile-3d-elevation">
          <Hexagon 
            size={116} 
            glowColor={metrics.average_latency_ms > 50 ? "amber" : "cyan"} 
            pulse={metrics.average_latency_ms > 50}
          >
            <Activity className="w-5 h-5 text-cyan-400 mb-1" />
            <span className="text-xl font-extrabold text-white">{metrics.average_latency_ms} ms</span>
            <span className="text-[10px] text-gray-400 uppercase tracking-widest mt-1 text-center">Avg API Latency</span>
          </Hexagon>
        </div>

        <div className="tile-3d-elevation">
          <Hexagon 
            size={116} 
            glowColor="cyan"
            pulse={false}
          >
            <Cpu className="w-5 h-5 text-cyan-400 mb-1" />
            <span className="text-xl font-extrabold text-white">{metrics.cache_efficiency_pct}%</span>
            <span className="text-[10px] text-gray-400 uppercase tracking-widest mt-1 text-center">Cache Efficiency</span>
          </Hexagon>
        </div>

        <div className="tile-3d-elevation">
          <Hexagon 
            size={116} 
            glowColor="green"
            pulse={false}
          >
            <ShieldCheck className="w-5 h-5 text-green-400 mb-1" />
            <span className="text-xl font-extrabold text-white">{metrics.enabled_rules} / {metrics.active_rules}</span>
            <span className="text-[10px] text-gray-400 uppercase tracking-widest mt-1 text-center">Active Rules</span>
          </Hexagon>
        </div>

        <div className="tile-3d-elevation">
          <Hexagon 
            size={116} 
            glowColor="cyan"
            pulse={false}
          >
            <Database className="w-5 h-5 text-cyan-400 mb-1" />
            <span className="text-xl font-extrabold text-white">{metrics.monitored_assets}</span>
            <span className="text-[10px] text-gray-400 uppercase tracking-widest mt-1 text-center">Monitored Assets</span>
          </Hexagon>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left Side Details Panel (2/3 width) */}
        <div className="xl:col-span-2 space-y-6">
          
          {/* Latency History Chart */}
          <div className="faceted-panel p-5 bg-[#0a0f18]/80 space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2">
              Observability API Request Latency (ms)
            </h2>
            {health?.latency_history && health.latency_history.length > 0 ? (
              <div className="h-40 flex items-center justify-center">
                <SvgLineChart 
                  data={health.latency_history} 
                  labels={health.latency_history.map((_, i) => `T-${health.latency_history.length - 1 - i}`)} 
                  color="#22d3ee" 
                  height={140}
                />
              </div>
            ) : (
              <div className="text-center py-10 text-gray-500 text-xs font-mono">No latency log series computed yet.</div>
            )}
          </div>

          {/* Interactive Demo Orchestrator */}
          <div className="faceted-panel p-5 bg-[#0a0f18]/80 space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-widest text-amber-500 border-b border-amber-500/15 pb-2">
              🎮 Interactive Demo Orchestrator
            </h2>
            <p className="text-xs text-gray-400 leading-relaxed font-mono">
              Simulate high-velocity attacks (brute-forcing SSH, password spraying, asset compromise) to trigger deception rules and test SOC responsiveness.
            </p>
            <div className="flex flex-wrap gap-4 pt-1">
              <button
                onClick={triggerDemo}
                disabled={demoActionLoading}
                className="px-4 py-2 bg-amber-500 hover:bg-amber-600 disabled:bg-gray-800 text-black font-bold text-xs uppercase rounded flex items-center gap-1.5 transition-all shadow-[0_0_10px_rgba(245,158,11,0.15)]"
              >
                <Play className="w-3.5 h-3.5 fill-black" /> Trigger Scenario
              </button>
              <button
                onClick={clearDemo}
                disabled={demoActionLoading}
                className="px-4 py-2 bg-red-950/40 border border-red-500/30 hover:border-red-500/60 disabled:bg-gray-800 text-red-400 font-bold text-xs uppercase rounded flex items-center gap-1.5 transition-all"
              >
                <Trash2 className="w-3.5 h-3.5" /> Clear Records
              </button>
            </div>
            {demoMessage && (
              <div className="text-[10px] font-mono text-cyan-400 bg-cyan-950/10 border border-cyan-500/20 px-3 py-2 rounded">
                [SYSTEM] {demoMessage}
              </div>
            )}
          </div>

          {/* API Inventory Table */}
          <div className="faceted-panel p-5 bg-[#0a0f18]/80 space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2">
              📖 API Route Catalog Inventory
            </h2>
            <div className="max-h-[300px] overflow-y-auto border border-gray-900 rounded">
              <table className="w-full text-xs font-mono border-collapse">
                <thead>
                  <tr className="bg-[#050b14] border-b border-gray-800 text-gray-400 text-left">
                    <th className="p-2">HTTP Endpoint Path</th>
                    <th className="p-2">Route Handler ID</th>
                    <th className="p-2 text-right">Methods</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-900/40">
                  {apiInventory?.routes?.map((route: any, idx: number) => (
                    <tr key={idx} className="hover:bg-gray-900/15 text-gray-300">
                      <td className="p-2 text-cyan-400">{route.path}</td>
                      <td className="p-2">{route.name}</td>
                      <td className="p-2 text-right">
                        {route.methods?.map((m: string) => (
                          <span key={m} className="px-1.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-black text-[9px] uppercase ml-1">
                            {m}
                          </span>
                        ))}
                      </td>
                    </tr>
                  )) || (
                    <tr>
                      <td colSpan={3} className="p-4 text-center text-gray-500">Route inventory offline.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Side Sidebar Details Panel (1/3 width) */}
        <div className="space-y-6">
          
          {/* Active Services Checkbox status */}
          <div className="faceted-panel p-5 bg-[#0a0f18]/80 space-y-3">
            <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2">
              Platform Services Status
            </h2>
            <div className="space-y-2.5 font-mono text-xs">
              {health?.services ? (
                Object.entries(health.services).map(([service, status]) => {
                  const isOnline = status.toLowerCase() === "online" || status.toLowerCase() === "active" || status.toLowerCase() === "operational" || status.toLowerCase() === "fresh" || status.toLowerCase() === "live";
                  return (
                    <div key={service} className="flex justify-between items-center bg-[#050b14]/50 border border-gray-900 rounded p-2">
                      <span className="text-gray-400 capitalize">{service.replace(/_/g, " ")}</span>
                      <span className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide ${
                        isOnline ? "bg-green-500/10 text-green-400 border border-green-500/20" : "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${isOnline ? "bg-green-500 animate-pulse" : "bg-amber-500"}`}></span>
                        {status}
                      </span>
                    </div>
                  );
                })
              ) : (
                <div className="text-gray-500">Services offline.</div>
              )}
            </div>
          </div>

          {/* SQLite DB Retries Observability */}
          <div className="faceted-panel p-5 bg-[#0a0f18]/80 space-y-3">
            <h2 className="text-xs font-bold uppercase tracking-widest text-amber-500 border-b border-amber-500/15 pb-2 flex items-center gap-1.5">
              <Database className="w-4 h-4 text-amber-500" />
              SQLite Concurrency Lock Retries
            </h2>
            <div className="grid grid-cols-2 gap-3 text-center font-mono">
              <div className="bg-[#050b14] border border-gray-800 rounded p-3">
                <span className="text-[9px] text-gray-500 block uppercase">Commit Retries</span>
                <span className="text-lg font-black text-amber-500">{health?.sqlite_lock_retries?.commit_retries ?? 0}</span>
              </div>
              <div className="bg-[#050b14] border border-gray-800 rounded p-3">
                <span className="text-[9px] text-gray-500 block uppercase">Flush Retries</span>
                <span className="text-lg font-black text-cyan-400">{health?.sqlite_lock_retries?.flush_retries ?? 0}</span>
              </div>
            </div>
            <div className="flex items-start gap-1.5 text-[9px] font-mono text-gray-500 mt-1">
              <Info className="w-3.5 h-3.5 text-cyan-500 flex-shrink-0" />
              <span>Indicates database lock write contention. Auto-retry uses exponential backoff to handle sqlite lock limits.</span>
            </div>
          </div>

          {/* WebSockets Link Status */}
          <div className="faceted-panel p-5 bg-[#0a0f18]/80 space-y-3">
            <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-cyan-400" />
              Active WebSocket Sockets
            </h2>
            <div className="divide-y divide-gray-900/60 font-mono text-xs text-gray-300">
              <div className="flex justify-between py-1.5">
                <span>/ws/telemetry</span>
                <span className="text-cyan-400 font-bold">{health?.websocket_connections?.telemetry ?? 0} clients</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span>/ws/geolocation</span>
                <span className="text-cyan-400 font-bold">{health?.websocket_connections?.geolocation ?? 0} clients</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span>/ws/simulation</span>
                <span className="text-cyan-400 font-bold">{health?.websocket_connections?.simulation ?? 0} clients</span>
              </div>
            </div>
          </div>

          {/* Onboarding expanders */}
          <div className="space-y-2">
            <h3 className="text-[10px] font-bold uppercase tracking-widest text-gray-500 px-1">Onboarding Guides</h3>

            {/* Developer Guide */}
            <div className="border border-gray-800 rounded bg-[#0a0f18]/60 overflow-hidden text-xs">
              <button 
                onClick={() => setOpenGuide(!openGuide)}
                className="w-full p-3 flex justify-between items-center font-bold text-gray-300 hover:bg-gray-900/20 text-left font-mono"
              >
                <span>🛠️ Developer Onboarding Guide</span>
                {openGuide ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </button>
              {openGuide && docs?.onboarding_guide && (
                <div className="p-3 bg-[#050b14] border-t border-gray-900 max-h-[300px] overflow-y-auto leading-relaxed text-gray-400 font-mono text-[10px] whitespace-pre-wrap">
                  {docs.onboarding_guide}
                </div>
              )}
            </div>

            {/* ER Models Schema */}
            <div className="border border-gray-800 rounded bg-[#0a0f18]/60 overflow-hidden text-xs">
              <button 
                onClick={() => setOpenER(!openER)}
                className="w-full p-3 flex justify-between items-center font-bold text-gray-300 hover:bg-gray-900/20 text-left font-mono"
              >
                <span>📊 Entity-Relationship Schemas</span>
                {openER ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </button>
              {openER && docs?.er_documentation && (
                <div className="p-3 bg-[#050b14] border-t border-gray-900 max-h-[300px] overflow-y-auto leading-relaxed text-gray-400 font-mono text-[10px] whitespace-pre-wrap">
                  {docs.er_documentation}
                </div>
              )}
            </div>

            {/* Core System Flow */}
            <div className="border border-gray-800 rounded bg-[#0a0f18]/60 overflow-hidden text-xs">
              <button 
                onClick={() => setOpenMermaid(!openMermaid)}
                className="w-full p-3 flex justify-between items-center font-bold text-gray-300 hover:bg-gray-900/20 text-left font-mono"
              >
                <span>📐 System Flow Diagram (Mermaid)</span>
                {openMermaid ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </button>
              {openMermaid && docs?.mermaid_diagram && (
                <div className="p-3 bg-[#050b14] border-t border-gray-900">
                  <pre className="p-3 bg-[#020509] rounded border border-gray-900 font-mono text-[9px] text-cyan-400 overflow-x-auto whitespace-pre">
                    {docs.mermaid_diagram}
                  </pre>
                </div>
              )}
            </div>

          </div>

        </div>
      </div>
    </div>
  );
};
export default PlatformHealth;
