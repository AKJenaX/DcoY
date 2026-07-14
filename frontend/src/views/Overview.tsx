import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { Hexagon } from "../components/Hexagon";
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
      <div className="flex justify-between items-center border-b border-[#220 20% 15%] pb-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">SOC Command Center</h1>
          <p className="text-sm text-gray-400">Real-time attack deflection & active defense console</p>
        </div>
        <button
          onClick={loadMetrics}
          className="flex items-center gap-2 px-3 py-1.5 text-xs font-semibold bg-[#111827] border border-[#222 20% 15%] rounded-md hover:border-amber-500/50 hover:text-amber-500 transition-all"
        >
          <RefreshCw className="w-3 h-3" /> Re-Sync
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-950/30 border border-red-500/50 rounded-md text-red-400 text-xs">
          {error}
        </div>
      )}

      {/* Hex KPI section */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4 justify-items-center py-1 perspective-container">
        <div className="tile-3d-elevation">
          <Hexagon size={116} glowColor="red" pulse={anomalyCount > 5}>
            <Shield className="w-5 h-5 text-red-500 mb-1" />
            <span className="text-xl font-extrabold text-white">{anomalyCount}</span>
            <span className="text-[10px] text-gray-400 uppercase tracking-widest mt-1">Active Threats</span>
          </Hexagon>
        </div>

        <div className="tile-3d-elevation">
          <Hexagon size={116} glowColor="amber" pulse={activeDecoys > 0}>
            <Bug className="w-5 h-5 text-amber-500 mb-1" />
            <span className="text-xl font-extrabold text-white">{activeDecoys}</span>
            <span className="text-[10px] text-gray-400 uppercase tracking-widest mt-1">Honeypots Engaged</span>
          </Hexagon>
        </div>

        <div className="tile-3d-elevation">
          <Hexagon size={116} glowColor="cyan">
            <ClipboardList className="w-5 h-5 text-cyan-400 mb-1" />
            <span className="text-xl font-extrabold text-white">{openCases}</span>
            <span className="text-[10px] text-gray-400 uppercase tracking-widest mt-1">Open Cases</span>
          </Hexagon>
        </div>

        <div className="tile-3d-elevation">
          <Hexagon size={116} glowColor="green">
            <Activity className="w-5 h-5 text-green-500 mb-1" />
            <span className="text-xl font-extrabold text-white">{healthScore}%</span>
            <span className="text-[10px] text-gray-400 uppercase tracking-widest mt-1">Health Index</span>
          </Hexagon>
        </div>

        <div className="tile-3d-elevation">
          <Hexagon size={116} glowColor="amber">
            <Clock3 className="w-5 h-5 text-amber-500 mb-1" />
            <span className="text-xl font-extrabold text-white">{avgResponseTime}s</span>
            <span className="text-[10px] text-gray-400 uppercase tracking-widest mt-1">Avg Response</span>
          </Hexagon>
        </div>

        <div className="tile-3d-elevation">
          <Hexagon size={116} glowColor="cyan">
            <RadioTower className="w-5 h-5 text-cyan-400 mb-1" />
            <span className="text-xl font-extrabold text-white">{intelFeedsOnline}</span>
            <span className="text-[10px] text-gray-400 uppercase tracking-widest mt-1">Intel Feeds</span>
          </Hexagon>
        </div>
      </div>

      {/* Main Grid: Scrolling Telemetry Feed & MITRE Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Telemetry scrolling feed (2/3 width) */}
        <div className="lg:col-span-2 faceted-panel p-5 flex flex-col h-[300px]">
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-sm font-bold tracking-widest uppercase text-amber-500/80">Live Telemetry Feed</h2>
            {telemetryStatus === "connected" && (
              <span className="flex items-center gap-1.5 text-[10px] bg-green-500/10 border border-green-500/30 px-2 py-0.5 rounded text-green-400 font-bold uppercase tracking-wider">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-ping"></span> Live Ingesting
              </span>
            )}
            {(telemetryStatus === "connecting" || telemetryStatus === "reconnecting") && (
              <span className="flex items-center gap-1.5 text-[10px] bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded text-amber-400 font-bold uppercase tracking-wider animate-pulse">
                <span className="w-1.5 h-1.5 bg-amber-500 rounded-full"></span> {telemetryStatus === "connecting" ? "WS Connecting" : "WS Reconnecting"}
              </span>
            )}
            {telemetryStatus === "polling" && (
              <span className="flex items-center gap-1.5 text-[10px] bg-cyan-500/10 border border-cyan-500/30 px-2 py-0.5 rounded text-cyan-400 font-bold uppercase tracking-wider">
                <span className="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-bounce"></span> HTTP Polling
              </span>
            )}
            {telemetryStatus === "disconnected" && (
              <span className="flex items-center gap-1.5 text-[10px] bg-red-500/10 border border-red-500/30 px-2 py-0.5 rounded text-red-400 font-bold uppercase tracking-wider">
                <span className="w-1.5 h-1.5 bg-red-500 rounded-full"></span> Disconnected
              </span>
            )}
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 font-mono text-xs pr-2 scrollbar-thin">
            {logs.length === 0 ? (
              <div className="relative h-full min-h-[190px] overflow-hidden rounded border border-gray-800 bg-[#050b14]/70 p-4">
                <div className="absolute inset-0 opacity-35">
                  {[
                    "00:00:00  waiting  honeypot_ssh_01  no ingress matched",
                    "00:00:04  standby  web_decoy_api    telemetry buffer armed",
                    "00:00:09  polling  rule_engine      signatures synchronized",
                    "00:00:13  idle     graph_builder    no new edges observed",
                    "00:00:18  waiting  deception_mesh   simulator heartbeat absent",
                  ].map((line, idx) => (
                    <div key={line} className="border-b border-gray-900 px-2 py-2 text-[10px] text-gray-600" style={{ marginLeft: idx % 2 ? 18 : 0 }}>
                      {line}
                    </div>
                  ))}
                </div>
                <div className="relative z-10 flex h-full items-center justify-center">
                  <div className="max-w-sm border border-amber-500/20 bg-amber-950/10 px-4 py-3 text-center">
                    <div className="text-[10px] font-bold uppercase tracking-widest text-amber-500">Telemetry idle</div>
                    <div className="mt-1 text-xs text-gray-300">Simulator feed is quiet. Decoy listeners and rule sync remain armed.</div>
                  </div>
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
        <div className="faceted-panel p-5 h-[300px] flex flex-col">
          <h2 className="text-sm font-bold tracking-widest uppercase text-cyan-400/80 mb-3">MITRE ATT&CK Matrix Coverage</h2>
          <div className="grid grid-cols-2 gap-3 flex-1 overflow-y-auto pr-1">
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
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="faceted-panel p-5 lg:col-span-1 h-[170px]">
          <h2 className="text-xs font-bold uppercase tracking-widest text-amber-500 mb-3">Recent Case Activity</h2>
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
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400">Attack Path Preview</h2>
            <Network className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-center gap-2 text-center">
            {["Ingress", "Decoy", "Rule", "Case", "Containment"].map((stage, idx) => (
              <React.Fragment key={stage}>
                <div className="min-w-0 flex-1 rounded border border-cyan-500/20 bg-cyan-950/10 px-2 py-3">
                  <div className="text-[10px] font-bold uppercase tracking-widest text-gray-400">{stage}</div>
                  <div className="mt-1 text-xs font-mono text-white">{["198.51.100.42", "SSH-01", "T1110", "CASE-001", "Auto-Isolate"][idx]}</div>
                </div>
                {idx < 4 && <div className="hidden h-px w-8 bg-gradient-to-r from-cyan-500/60 to-amber-500/60 xl:block" />}
              </React.Fragment>
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
