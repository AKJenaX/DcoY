import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { Hexagon } from "../components/Hexagon";
import { GlassPanel } from "../components/GlassPanel";
import { Shield, Bug, ClipboardList, Activity, RefreshCw, Clock3, RadioTower, Network } from "lucide-react";
import { useRealtimeChannel } from "../hooks/useRealtimeChannel";

export const Overview: React.FC = () => {
  const { data: realtimeLogs, status: telemetryStatus } = useRealtimeChannel("telemetry");
  const [metrics, setMetrics] = useState<any>(null);
  const [error, setError] = useState("");

  const loadMetrics = async () => {
    try {
      const metricData = await api.getExecutiveMetrics();
      setMetrics(metricData);
      setError("");
    } catch (err: any) {
      setError("Failed to sync command metrics from endpoints.");
    }
  };

  useEffect(() => {
    loadMetrics();
    const interval = setInterval(loadMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const logs = realtimeLogs || [];

  const openCases = metrics?.kpis?.open_investigations ?? 3;
  const healthScore = metrics?.platform_health_diagnostics?.score ?? 98;
  const activeDecoys = logs.filter(l => l.honeypot && l.honeypot !== "none").length || 4;
  const anomalyCount = logs.filter(l => l.is_anomaly).length || 8;
  const avgResponseTime = metrics?.response_effectiveness?.avg_response_time_seconds ?? 24;
  const intelFeedsOnline = metrics?.threat_intel?.feeds_online ?? 7;

  // MITRE Map data
  const mitreTechniques = [
    { code: "T1110", name: "Brute Force", count: 18, severity: "critical" },
    { code: "T1046", name: "Network Service Scanning", count: 12, severity: "high" },
    { code: "T1190", name: "Exploit Public-Facing App", count: 9, severity: "high" },
    { code: "T1566", name: "Phishing Ingress", count: 4, severity: "medium" },
    { code: "T1021", name: "Remote Services", count: 7, severity: "medium" },
    { code: "T1059", name: "Command Scripting Interpreter", count: 15, severity: "critical" },
    { code: "T1003", name: "OS Credential Dumping", count: 2, severity: "low" },
    { code: "T1071", name: "Application Layer Protocol", count: 6, severity: "medium" },
  ];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center pb-3 page-header-glass">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono text-cyan-400 uppercase tracking-widest mb-1">
            <span className="w-2 h-2 rounded-full bg-[#00ff66] animate-pulse shadow-[0_0_8px_#00ff66]"></span>
            CONSOLE.STATUS // ACTIVE_MONITORING
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white font-mono uppercase">SOC Command Center</h1>
          <p className="text-xs text-gray-400">Real-time attack deflection & active defense console</p>
        </div>
        <button
          onClick={loadMetrics}
          className="flex items-center gap-2 px-3 py-1.5 text-xs font-semibold bg-[#111827]/70 border border-gray-800 rounded-md hover:border-amber-500/50 hover:text-amber-500 transition-all font-mono"
        >
          <RefreshCw className="w-3 h-3" /> RE-SYNC
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-950/30 border border-red-500/50 rounded-md text-red-400 text-xs font-mono">
          [ALERT] {error}
        </div>
      )}

      {/* Hex KPI section */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4 justify-items-center py-1">
        <GlassPanel borderColor="cyan" showBrackets={true} className="p-3 w-full flex justify-center items-center">
          <div className="tile-3d-elevation">
            <Hexagon size={116} glowColor="red" pulse={anomalyCount > 5}>
              <Shield className="w-5 h-5 text-red-500 mb-1" />
              <span className="text-xl font-extrabold text-white">{anomalyCount}</span>
              <span className="text-[9px] text-gray-400 uppercase tracking-widest mt-1 h-8 flex items-center justify-center text-center leading-tight">Active Threats</span>
            </Hexagon>
          </div>
        </GlassPanel>

        <GlassPanel borderColor="cyan" showBrackets={true} className="p-3 w-full flex justify-center items-center">
          <div className="tile-3d-elevation">
            <Hexagon size={116} glowColor="amber" pulse={activeDecoys > 0}>
              <Bug className="w-5 h-5 text-amber-500 mb-1" />
              <span className="text-xl font-extrabold text-white">{activeDecoys}</span>
              <span className="text-[9px] text-gray-400 uppercase tracking-widest mt-1 h-8 flex items-center justify-center text-center leading-tight">Honeypots Engaged</span>
            </Hexagon>
          </div>
        </GlassPanel>

        <GlassPanel borderColor="cyan" showBrackets={true} className="p-3 w-full flex justify-center items-center">
          <div className="tile-3d-elevation">
            <Hexagon size={116} glowColor="cyan">
              <ClipboardList className="w-5 h-5 text-cyan-400 mb-1" />
              <span className="text-xl font-extrabold text-white">{openCases}</span>
              <span className="text-[9px] text-gray-400 uppercase tracking-widest mt-1 h-8 flex items-center justify-center text-center leading-tight">Open Cases</span>
            </Hexagon>
          </div>
        </GlassPanel>

        <GlassPanel borderColor="cyan" showBrackets={true} className="p-3 w-full flex justify-center items-center">
          <div className="tile-3d-elevation">
            <Hexagon size={116} glowColor="green">
              <Activity className="w-5 h-5 text-green-500 mb-1" />
              <span className="text-xl font-extrabold text-white">{healthScore}%</span>
              <span className="text-[9px] text-gray-400 uppercase tracking-widest mt-1 h-8 flex items-center justify-center text-center leading-tight">Health Index</span>
            </Hexagon>
          </div>
        </GlassPanel>

        <GlassPanel borderColor="cyan" showBrackets={true} className="p-3 w-full flex justify-center items-center">
          <div className="tile-3d-elevation">
            <Hexagon size={116} glowColor="amber">
              <Clock3 className="w-5 h-5 text-amber-500 mb-1" />
              <span className="text-xl font-extrabold text-white">{avgResponseTime}s</span>
              <span className="text-[9px] text-gray-400 uppercase tracking-widest mt-1 h-8 flex items-center justify-center text-center leading-tight">Avg Response</span>
            </Hexagon>
          </div>
        </GlassPanel>

        <GlassPanel borderColor="cyan" showBrackets={true} className="p-3 w-full flex justify-center items-center">
          <div className="tile-3d-elevation">
            <Hexagon size={116} glowColor="cyan">
              <RadioTower className="w-5 h-5 text-cyan-400 mb-1" />
              <span className="text-xl font-extrabold text-white">{intelFeedsOnline}</span>
              <span className="text-[9px] text-gray-400 uppercase tracking-widest mt-1 h-8 flex items-center justify-center text-center leading-tight">Intel Feeds</span>
            </Hexagon>
          </div>
        </GlassPanel>
      </div>

      {/* Main Grid: Scrolling Telemetry Feed & MITRE Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Telemetry scrolling feed (2/3 width) */}
        <div className="lg:col-span-2 faceted-panel p-5 flex flex-col h-[300px]">
          <div className="flex justify-between items-center mb-3">
            <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-amber-500 uppercase">
              <span className="w-2 h-2 rounded-full bg-[#00ff66] animate-pulse shadow-[0_0_8px_#00ff66]"></span>
              SYS.FEED // LIVE TELEMETRY
            </div>
            {telemetryStatus === "connected" && (
              <span className="flex items-center gap-1.5 text-[10px] bg-green-950/30 border border-green-500/30 px-2 py-0.5 rounded text-green-400 font-bold uppercase tracking-wider font-mono shadow-[0_0_10px_rgba(0,255,102,0.06)]">
                <span className="w-2 h-2 rounded-full bg-[#00ff66] animate-pulse shadow-[0_0_8px_#00ff66]"></span> Live Ingesting
              </span>
            )}
            {(telemetryStatus === "connecting" || telemetryStatus === "reconnecting") && (
              <span className="flex items-center gap-1.5 text-[10px] bg-amber-950/30 border border-amber-500/30 px-2 py-0.5 rounded text-amber-400 font-bold uppercase tracking-wider animate-pulse font-mono shadow-[0_0_10px_rgba(245,166,35,0.06)]">
                <span className="w-2 h-2 rounded-full bg-[#ffb300] animate-pulse shadow-[0_0_8px_#ffb300]"></span> {telemetryStatus === "connecting" ? "WS Connecting" : "WS Reconnecting"}
              </span>
            )}
            {telemetryStatus === "polling" && (
              <span className="flex items-center gap-1.5 text-[10px] bg-cyan-950/30 border border-cyan-500/30 px-2 py-0.5 rounded text-cyan-400 font-bold uppercase tracking-wider font-mono shadow-[0_0_10px_rgba(0,229,255,0.06)]">
                <span className="w-2 h-2 rounded-full bg-[#00e5ff] animate-pulse shadow-[0_0_8px_#00e5ff]"></span> HTTP Polling
              </span>
            )}
            {telemetryStatus === "disconnected" && (
              <span className="flex items-center gap-1.5 text-[10px] bg-red-950/30 border border-red-500/30 px-2 py-0.5 rounded text-red-400 font-bold uppercase tracking-wider font-mono shadow-[0_0_10px_rgba(239,68,68,0.06)]">
                <span className="w-2 h-2 rounded-full bg-[#ff3333] animate-pulse shadow-[0_0_8px_#ff3333]"></span> Disconnected
              </span>
            )}
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 font-mono text-xs pr-2 scrollbar-thin flex flex-col justify-center">
            {logs.length === 0 ? (
              <div className="relative h-full min-h-[190px] p-4 flex items-center justify-center">
                <div className="relative z-10">
                  <GlassPanel borderColor="amber" className="max-w-sm px-6 py-4 text-center bg-black/35 backdrop-blur-xl">
                    <div className="text-[10px] font-bold uppercase tracking-widest text-amber-500 font-mono flex items-center justify-center gap-1.5">
                      <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,166,35,0.6)]"></span>
                      TELEMETRY IDLE
                    </div>
                    <div className="mt-1 text-[11px] text-gray-300 font-sans">Simulator feed is quiet. Decoy listeners and rule sync remain armed.</div>
                  </GlassPanel>
                </div>
              </div>
            ) : (
              logs.map((log, index) => {
                const isAnomaly = log.is_anomaly;
                const date = log.timestamp ? log.timestamp.split("T")[1]?.slice(0, 8) : "00:00:00";
                return (
                  <div
                    key={index}
                    className={`flex justify-between p-2 rounded border transition-all ${
                      isAnomaly
                        ? "bg-red-950/20 border-red-500/20 hover:border-red-500/40 text-red-200"
                        : "bg-[#111827]/40 border-gray-800 hover:border-gray-700 text-gray-300"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-gray-500">[{date}]</span>
                      <span className={isAnomaly ? "text-red-400 font-bold" : "text-cyan-400"}>{log.ip || "127.0.0.1"}</span>
                      {log.location && (
                        <span className={`text-[9px] px-1 rounded font-bold uppercase ${
                          log.location.geo_source === "mock"
                            ? "bg-amber-500/10 border border-amber-500/20 text-amber-500"
                            : "bg-cyan-500/10 border border-cyan-500/20 text-cyan-400"
                        }`}>
                          {log.location.country || "Unknown"}
                          {log.location.geo_source === "mock" && " [sim]"}
                        </span>
                      )}
                      <span>{log.event_type || log.event || "Ingress event matched"}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {log.honeypot && log.honeypot !== "none" && (
                        <span className="px-1.5 py-0.5 bg-amber-500/10 border border-amber-500/30 text-amber-500 rounded text-[9px] uppercase font-bold">
                          Decoy: {log.honeypot.split("_")[0]}
                        </span>
                      )}
                      <span className={`text-[10px] font-bold ${isAnomaly ? "text-red-400" : "text-gray-500"}`}>
                        Risk: {intToScore(log.risk_score)}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* MITRE Matrix Heatmap (1/3 width) */}
        <div className="faceted-panel p-5 h-[300px] flex flex-col relative overflow-hidden">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase mb-3">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
            MITRE.MATRIX // ATTACK COVERAGE
          </div>
          <div className="relative flex-1 min-h-0">
            <div 
              className="grid grid-cols-2 gap-3 h-full overflow-y-auto pr-1 pb-8 scrollbar-thin"
              style={{
                maskImage: "linear-gradient(to bottom, black calc(100% - 32px), transparent 100%)",
                WebkitMaskImage: "linear-gradient(to bottom, black calc(100% - 32px), transparent 100%)"
              }}
            >
              {mitreTechniques.map((tech) => (
                <div
                  key={tech.code}
                  className={`p-3 rounded border bg-[#111827]/50 hover:bg-[#1f2937]/50 transition-all ${
                    tech.severity === "critical"
                      ? "border-red-500/30 hover:border-red-500/60"
                      : tech.severity === "high"
                      ? "border-amber-500/30 hover:border-amber-500/60"
                      : "border-gray-800 hover:border-gray-600"
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <span className="text-[10px] font-mono font-bold text-gray-400">{tech.code}</span>
                    <span
                      className={`w-2 h-2 rounded-full ${
                        tech.severity === "critical"
                          ? "bg-red-500"
                          : tech.severity === "high"
                          ? "bg-amber-500"
                          : "bg-cyan-400"
                      }`}
                    ></span>
                  </div>
                  <div className="mt-1 text-xs font-semibold text-white truncate">{tech.name}</div>
                  <div className="mt-2 text-[10px] text-gray-400 font-mono">Count: {tech.count} events</div>
                </div>
              ))}
            </div>
            {/* Fade-to-transparent overlay matching panel backing, extending through padding bounds */}
            <div className="absolute left-0 right-0 h-10 bg-gradient-to-t from-[#090e1a] via-[#090e1a]/85 to-transparent pointer-events-none z-20" style={{ bottom: "-20px", margin: "0 -20px" }} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="faceted-panel p-5 lg:col-span-1 h-[170px]">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-amber-500 uppercase mb-3">
            <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,166,35,0.6)]"></span>
            CASE.LEDGER // RECENT CASES
          </div>
          <div className="space-y-2 text-xs">
            {[
              ["CASE-2026-001", "Credential spray triage", "Open"],
              ["CASE-2026-014", "Web decoy probe review", "Queued"],
              ["CASE-2026-027", "Lateral movement watch", "Monitoring"],
            ].map(([id, title, status]) => (
              <div key={id} className="flex items-center justify-between rounded border border-gray-800 bg-[#111827]/50 px-3 py-2">
                <div>
                  <span className="font-mono text-[10px] text-cyan-400">{id}</span>
                  <div className="text-gray-300">{title}</div>
                </div>
                <span className="text-[9px] font-bold uppercase text-amber-500">{status}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="faceted-panel p-5 lg:col-span-2 h-[170px] overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase">
              <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
              PATH.PREVIEW // COMPROMISE GRAPH
            </div>
            <Network className="w-4 h-4 text-cyan-400" />
          </div>

          <div className="relative flex items-center justify-between text-center mt-4 h-20 px-2">
            {/* Ribbon Background Line Connector */}
            <div className="absolute inset-0 z-0 flex items-center pointer-events-none">
              <svg className="w-full h-12" viewBox="0 0 600 50" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="comp-edge-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#00e5ff" stopOpacity="0.85" />
                    <stop offset="50%" stopColor="#d500f9" stopOpacity="0.85" />
                    <stop offset="100%" stopColor="#f5a623" stopOpacity="0.85" />
                  </linearGradient>
                  <filter id="comp-glow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3.5" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>
                
                {/* Winding organic-looking path (amber-cyan ribbon theme) */}
                <path 
                  d="M 20,25 C 90,5 150,45 220,25 C 290,5 350,45 420,25 C 490,5 550,45 580,25" 
                  fill="none" 
                  stroke="url(#comp-edge-grad)" 
                  strokeWidth="3.5"
                  filter="url(#comp-glow)"
                  className="animate-pulse"
                />

                {/* Waypoint hex-dot markers at 5 logical nodes */}
                {[30, 165, 300, 435, 570].map((cx, idx) => (
                  <g key={idx} transform={`translate(${cx}, 25)`} className="animate-pulse">
                    <polygon 
                      points="0,-5 4.3,-2.5 4.3,2.5 0,5 -4.3,2.5 -4.3,-2.5" 
                      fill="#030305" 
                      stroke={idx % 2 === 0 ? "#00e5ff" : "#f5a623"} 
                      strokeWidth="1.5" 
                    />
                  </g>
                ))}
              </svg>
            </div>

            {/* Stages Content Cards */}
            {["Ingress", "Decoy", "Rule", "Case", "Containment"].map((stage, idx) => (
              <div key={stage} className="relative z-10 w-[95px] rounded border border-cyan-500/25 bg-[#050b14]/85 px-1 py-1.5 backdrop-blur-md">
                <div className="text-[9px] font-bold uppercase tracking-widest text-cyan-400">{stage}</div>
                <div className="mt-0.5 text-[9.5px] font-mono text-white truncate px-1">
                  {["198.51.100.42", "SSH-01", "T1110", "CASE-001", "Auto-Isolate"][idx]}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const intToScore = (score: any) => {
  if (typeof score === "number") {
    return score.toFixed(2);
  }
  return score || "0.00";
};
