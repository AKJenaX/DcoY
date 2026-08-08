import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { Hexagon } from "../components/Hexagon";
import { GlassPanel } from "../components/GlassPanel";
import { Shield, Bug, ClipboardList, Activity, RefreshCw, Clock3, RadioTower, Network } from "lucide-react";
import { useRealtimeChannel } from "../hooks/useRealtimeChannel";
import { Sparkline } from "../components/charts/Sparkline";
import { CountUp } from "../components/CountUp";

export const Overview: React.FC = () => {
  const { data: realtimeLogs, status: telemetryStatus } = useRealtimeChannel("telemetry");
  const [metrics, setMetrics] = useState<any>(null);
  const [error, setError] = useState("");
  const [history, setHistory] = useState<Record<string, number[]>>(() => {
    const seed = (base: number, variance: number) => 
      Array.from({ length: 15 }, () => base + Math.round((Math.random() - 0.5) * variance));
    return {
      anomalyCount: seed(8, 4),
      activeDecoys: seed(4, 2),
      openCases: seed(3, 1),
      healthScore: seed(98, 2),
      avgResponseTime: seed(24, 6),
      intelFeedsOnline: seed(7, 0)
    };
  });

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

  const defaultTelemetryLogs = [
    {
      timestamp: new Date().toISOString(),
      ip: "185.220.101.5",
      event_type: "SSH Brute Force",
      event: "Failed SSH login root:admin",
      honeypot: "HONEYPOT-SSH-01",
      is_anomaly: true,
      risk_score: 0.88,
      location: { country: "Germany", geo_source: "mock" }
    },
    {
      timestamp: new Date(Date.now() - 35000).toISOString(),
      ip: "198.51.100.42",
      event_type: "TCP SYN Port Sweep",
      event: "Port scan attempts on 80, 443, 8080",
      honeypot: "HONEYPOT-HTTP-01",
      is_anomaly: false,
      risk_score: 0.45,
      location: { country: "United States", geo_source: "mock" }
    },
    {
      timestamp: new Date(Date.now() - 75000).toISOString(),
      ip: "45.132.22.99",
      event_type: "Credential Stuffing",
      event: "Repetitive auth failures on gateway",
      honeypot: "auth-gateway-prod",
      is_anomaly: true,
      risk_score: 0.92,
      location: { country: "Netherlands", geo_source: "mock" }
    }
  ];

  const logs = realtimeLogs && realtimeLogs.length > 0 ? realtimeLogs : defaultTelemetryLogs;

  const openCases = metrics?.kpis?.open_investigations ?? 3;
  const healthScore = metrics?.platform_health_diagnostics?.score ?? 98;
  const activeDecoys = logs.filter(l => l.honeypot && l.honeypot !== "none").length || 4;
  const anomalyCount = logs.filter(l => l.is_anomaly).length || 8;
  const avgResponseTime = metrics?.response_effectiveness?.avg_response_time_seconds ?? 24;
  const intelFeedsOnline = metrics?.threat_intel?.feeds_online ?? 7;

  useEffect(() => {
    setHistory(prev => {
      const newHistory = { ...prev };
      const append = (key: string, val: number) => {
        const arr = [...(newHistory[key] || [])];
        if (arr.length === 0 || arr[arr.length - 1] !== val) {
          arr.push(val);
          if (arr.length > 20) arr.shift();
        }
        newHistory[key] = arr;
      };
      append("anomalyCount", anomalyCount);
      append("activeDecoys", activeDecoys);
      append("openCases", openCases);
      append("healthScore", healthScore);
      append("avgResponseTime", avgResponseTime);
      append("intelFeedsOnline", intelFeedsOnline);
      return newHistory;
    });
  }, [anomalyCount, activeDecoys, openCases, healthScore, avgResponseTime, intelFeedsOnline]);

  const getDelta = (key: string, current: number) => {
    const arr = history[key];
    if (!arr || arr.length < 2) return null;
    const prev = arr[arr.length - 2];
    const diff = current - prev;
    
    let isGood = diff > 0;
    if (key === "avgResponseTime" || key === "anomalyCount") {
      isGood = diff < 0; // lower is better
    }
    
    if (diff > 0) {
      return { text: `↑ +${diff}`, color: isGood ? "text-green-400" : "text-red-400" };
    }
    if (diff < 0) {
      return { text: `↓ ${Math.abs(diff)}`, color: isGood ? "text-green-400" : "text-red-400" };
    }
    return { text: `→ 0`, color: "text-gray-500" };
  };

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
          className="flex items-center gap-2 px-3 py-1.5 text-xs font-semibold bg-[#111827]/70 border border-gray-800 rounded-md hover:border-amber-500/50 hover:text-amber-500 hover:-translate-y-0.5 hover:shadow-[0_0_10px_rgba(245,158,11,0.15)] transition-all duration-300 font-mono"
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
        {/* Tier 1: Primary (Active Threats) */}
        <GlassPanel borderColor="red" showBrackets={true} className="p-3 w-full flex flex-col items-center justify-between min-h-[196px]">
          <div className="tile-3d-elevation flex-1 flex items-center justify-center">
            <Hexagon size={126} glowColor="red" pulse={true}>
              <Shield className="w-5 h-5 text-red-500 mb-1" />
              <span className="text-2xl font-black text-white"><CountUp value={anomalyCount} /></span>
              <span className="text-[9px] text-gray-400 uppercase tracking-widest mt-1 h-8 flex items-center justify-center text-center leading-tight">Active Threats</span>
            </Hexagon>
          </div>
          {/* Trend context */}
          {getDelta("anomalyCount", anomalyCount) && (
            <div className="flex items-center gap-1.5 text-[9px] font-mono mt-1.5 select-none">
              <span className={getDelta("anomalyCount", anomalyCount)?.color}>{getDelta("anomalyCount", anomalyCount)?.text}</span>
              <Sparkline data={history.anomalyCount} color="#ef4444" />
            </div>
          )}
        </GlassPanel>

        {/* Tier 2: Secondary (Honeypots Engaged) */}
        <GlassPanel borderColor="cyan" showBrackets={true} className="p-3 w-full flex flex-col items-center justify-between min-h-[196px]">
          <div className="tile-3d-elevation flex-1 flex items-center justify-center">
            <Hexagon size={114} glowColor="amber" pulse={activeDecoys > 0}>
              <Bug className="w-5 h-5 text-amber-500/70 mb-1" />
              <span className="text-xl font-extrabold text-white"><CountUp value={activeDecoys} /></span>
              <span className="text-[9px] text-gray-400 uppercase tracking-widest mt-1 h-8 flex items-center justify-center text-center leading-tight">Honeypots Engaged</span>
            </Hexagon>
          </div>
          {/* Trend context */}
          {getDelta("activeDecoys", activeDecoys) && (
            <div className="flex items-center gap-1.5 text-[9px] font-mono mt-1.5 select-none">
              <span className={getDelta("activeDecoys", activeDecoys)?.color}>{getDelta("activeDecoys", activeDecoys)?.text}</span>
              <Sparkline data={history.activeDecoys} color="#f5a623" />
            </div>
          )}
        </GlassPanel>

        {/* Tier 2: Secondary (Open Cases) */}
        <GlassPanel borderColor="cyan" showBrackets={true} className="p-3 w-full flex flex-col items-center justify-between min-h-[196px]">
          <div className="tile-3d-elevation flex-1 flex items-center justify-center">
            <Hexagon size={114} glowColor="cyan">
              <ClipboardList className="w-5 h-5 text-cyan-500/70 mb-1" />
              <span className="text-xl font-extrabold text-white"><CountUp value={openCases} /></span>
              <span className="text-[9px] text-gray-400 uppercase tracking-widest mt-1 h-8 flex items-center justify-center text-center leading-tight">Open Cases</span>
            </Hexagon>
          </div>
          {/* Trend context */}
          {getDelta("openCases", openCases) && (
            <div className="flex items-center gap-1.5 text-[9px] font-mono mt-1.5 select-none">
              <span className={getDelta("openCases", openCases)?.color}>{getDelta("openCases", openCases)?.text}</span>
              <Sparkline data={history.openCases} color="#00e5ff" />
            </div>
          )}
        </GlassPanel>

        {/* Tier 2: Secondary (Health Index) */}
        <GlassPanel borderColor="cyan" showBrackets={true} className="p-3 w-full flex flex-col items-center justify-between min-h-[196px]">
          <div className="tile-3d-elevation flex-1 flex items-center justify-center">
            <Hexagon size={114} glowColor="green">
              <Activity className="w-5 h-5 text-green-500/70 mb-1" />
              <span className="text-xl font-extrabold text-white"><CountUp value={healthScore} />%</span>
              <span className="text-[9px] text-gray-400 uppercase tracking-widest mt-1 h-8 flex items-center justify-center text-center leading-tight">Health Index</span>
            </Hexagon>
          </div>
          {/* Trend context */}
          {getDelta("healthScore", healthScore) && (
            <div className="flex items-center gap-1.5 text-[9px] font-mono mt-1.5 select-none">
              <span className={getDelta("healthScore", healthScore)?.color}>{getDelta("healthScore", healthScore)?.text}</span>
              <Sparkline data={history.healthScore} color="#10b981" />
            </div>
          )}
        </GlassPanel>

        {/* Tier 3: Tertiary (Avg Response) */}
        <GlassPanel borderColor="gray" showBrackets={true} className="p-3 w-full flex flex-col items-center justify-between min-h-[196px] opacity-75 hover:opacity-100 transition-opacity">
          <div className="tile-3d-elevation flex-1 flex items-center justify-center">
            <Hexagon size={114} glowColor="none">
              <Clock3 className="w-5 h-5 text-gray-500 mb-1" />
              <span className="text-lg font-bold text-gray-300"><CountUp value={avgResponseTime} />s</span>
              <span className="text-[9px] text-gray-500 uppercase tracking-widest mt-1 h-8 flex items-center justify-center text-center leading-tight">Avg Response</span>
            </Hexagon>
          </div>
          {/* Trend context */}
          {getDelta("avgResponseTime", avgResponseTime) && (
            <div className="flex items-center gap-1.5 text-[9px] font-mono mt-1.5 select-none">
              <span className={getDelta("avgResponseTime", avgResponseTime)?.color}>{getDelta("avgResponseTime", avgResponseTime)?.text}</span>
              <Sparkline data={history.avgResponseTime} color="rgba(255,255,255,0.15)" />
            </div>
          )}
        </GlassPanel>

        {/* Tier 3: Tertiary (Intel Feeds) */}
        <GlassPanel borderColor="gray" showBrackets={true} className="p-3 w-full flex flex-col items-center justify-between min-h-[196px] opacity-75 hover:opacity-100 transition-opacity">
          <div className="tile-3d-elevation flex-1 flex items-center justify-center">
            <Hexagon size={114} glowColor="none">
              <RadioTower className="w-5 h-5 text-gray-500 mb-1" />
              <span className="text-lg font-bold text-gray-300"><CountUp value={intelFeedsOnline} /></span>
              <span className="text-[9px] text-gray-500 uppercase tracking-widest mt-1 h-8 flex items-center justify-center text-center leading-tight">Intel Feeds</span>
            </Hexagon>
          </div>
          {/* Trend context */}
          {getDelta("intelFeedsOnline", intelFeedsOnline) && (
            <div className="flex items-center gap-1.5 text-[9px] font-mono mt-1.5 select-none">
              <span className={getDelta("intelFeedsOnline", intelFeedsOnline)?.color}>{getDelta("intelFeedsOnline", intelFeedsOnline)?.text}</span>
              <Sparkline data={history.intelFeedsOnline} color="rgba(255,255,255,0.15)" />
            </div>
          )}
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
              <span className="flex items-center gap-2 text-xs bg-green-950/50 border border-green-400/50 px-3 py-1 rounded text-green-400 font-extrabold uppercase tracking-widest font-mono shadow-[0_0_15px_rgba(0,255,102,0.25),inset_0_0_6px_rgba(0,255,102,0.15)]">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00ff66] opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#00ff66] shadow-[0_0_10px_#00ff66,0_0_20px_#00ff66]"></span>
                </span>
                Live Ingesting
              </span>
            )}
            {(telemetryStatus === "connecting" || telemetryStatus === "reconnecting") && (
              <span className="flex items-center gap-1.5 text-[10px] bg-amber-950/15 border border-amber-500/15 px-2 py-0.5 rounded text-amber-500/70 font-bold uppercase tracking-wider animate-pulse font-mono">
                <span className="w-2 h-2 rounded-full bg-amber-500/70 animate-pulse"></span> {telemetryStatus === "connecting" ? "WS Connecting" : "WS Reconnecting"}
              </span>
            )}
            {telemetryStatus === "polling" && (
              <span className="flex items-center gap-1.5 text-[10px] bg-cyan-950/15 border border-cyan-500/15 px-2 py-0.5 rounded text-cyan-500/70 font-bold uppercase tracking-wider font-mono">
                <span className="w-2 h-2 rounded-full bg-cyan-500/70 animate-pulse"></span> HTTP Polling
              </span>
            )}
            {telemetryStatus === "disconnected" && (
              <span className="flex items-center gap-1.5 text-[10px] bg-red-950/15 border border-red-500/15 px-2 py-0.5 rounded text-red-400/70 font-bold uppercase tracking-wider font-mono">
                <span className="w-2 h-2 rounded-full bg-red-500/70 animate-pulse"></span> Disconnected
              </span>
            )}
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 font-mono text-xs pr-2 scrollbar-thin">
            {logs.length === 0 ? (
              <div className="relative h-full min-h-[190px] w-full p-4 flex items-center justify-center overflow-hidden rounded-lg bg-[#050b14]/20">
                {/* Subtle Scan-line Sweep */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-30">
                  <div className="w-full h-[2px] bg-gradient-to-r from-transparent via-amber-500/30 to-transparent absolute left-0 animate-telemetry-scan" />
                </div>

                {/* Concentric pulsing radar rings behind */}
                <div className="absolute inset-0 pointer-events-none flex items-center justify-center opacity-10">
                  <div className="w-24 h-24 rounded-full border border-amber-500 animate-ping [animation-duration:3s]" />
                  <div className="w-48 h-48 rounded-full border border-amber-500 absolute animate-ping [animation-duration:3s] [animation-delay:1.5s]" />
                </div>

                {/* Faint horizontal scrolling baseline waveform */}
                <div className="absolute bottom-0 left-0 right-0 h-10 overflow-hidden opacity-[0.12] pointer-events-none">
                  <svg className="w-[200%] h-full animate-[waveform-scroll_4s_linear_infinite] @media (prefers-reduced-motion: reduce):animate-none" viewBox="0 0 400 40" preserveAspectRatio="none">
                    <path
                      d="M 0,20 Q 10,12 20,20 T 40,20 T 60,20 T 80,20 T 100,20 T 120,20 T 140,20 T 160,20 T 180,20 T 200,20 Q 210,12 220,20 T 240,20 T 260,20 T 280,20 T 300,20 T 320,20 T 340,20 T 360,20 T 380,20 T 400,20"
                      fill="none"
                      stroke="#f5a623"
                      strokeWidth="1.5"
                    />
                  </svg>
                </div>

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
        <div className="faceted-panel p-7 h-[300px] flex flex-col relative overflow-hidden">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase mb-3">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
            MITRE.MATRIX // ATTACK COVERAGE
          </div>
          <div className="relative flex-1 min-h-0">
            <div className="grid grid-cols-2 gap-3 max-h-[220px] overflow-y-auto pr-1.5 scrollbar-thin">
              {mitreTechniques.map((tech) => (
                <div
                  key={tech.code}
                  className={`p-3 rounded border bg-[#111827]/50 hover:bg-[#1f2937]/60 hover:-translate-y-0.5 hover:shadow-[0_0_12px_rgba(0,229,255,0.08)] cursor-pointer transition-all duration-300 ${
                    tech.severity === "critical"
                      ? "border-red-500/30 hover:border-red-500/60 hover:shadow-[0_0_12px_rgba(239,68,68,0.1)]"
                      : tech.severity === "high"
                      ? "border-amber-500/30 hover:border-amber-500/60 hover:shadow-[0_0_12px_rgba(245,166,35,0.1)]"
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
                  <div className="mt-2 text-[10px] text-gray-400 font-mono">Count: <CountUp value={tech.count} /> events</div>
                </div>
              ))}
            </div>
            {/* Fade-to-transparent overlay matching panel backing */}
            <div className="absolute bottom-0 left-0 right-0 h-[28px] bg-gradient-to-t from-[hsl(220,20%,8%)] to-transparent pointer-events-none z-10" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Case Ledger */}
        <div className="faceted-panel p-5 lg:col-span-1 h-auto min-h-[235px]">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-amber-500 uppercase mb-3">
            <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,166,35,0.6)]"></span>
            CASE.LEDGER // RECENT CASES
          </div>
          <div className="space-y-2 text-xs max-h-[240px] overflow-y-auto pr-1 scrollbar-thin">
            {[
              ["CASE-2026-001", "Credential spray triage", "Open"],
              ["CASE-2026-014", "Web decoy probe review", "Queued"],
              ["CASE-2026-027", "Lateral movement watch", "Monitoring"],
              ["CASE-2026-038", "SSH decoy port sweep", "Investigating"],
            ].map(([id, title, status]) => (
              <div key={id} className="flex items-center justify-between rounded border border-gray-800 bg-[#111827]/50 hover:bg-[#111827]/80 hover:border-cyan-500/30 hover:-translate-y-0.5 transition-all duration-300 cursor-pointer shadow-[0_0_0_rgba(0,229,255,0)] hover:shadow-[0_0_12px_rgba(0,229,255,0.06)] px-3 py-2">
                <div>
                  <span className="font-mono text-[10px] text-cyan-400">{id}</span>
                  <div className="text-gray-300 font-medium">{title}</div>
                </div>
                <span className="text-[9px] font-bold uppercase text-amber-500">{status}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Compromise Graph: Sized to h-[205px] for asymmetry */}
        <div className="faceted-panel p-5 lg:col-span-2 h-[205px] flex flex-col justify-between overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase">
              <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
              PATH.PREVIEW // COMPROMISE GRAPH
            </div>
            <Network className="w-4 h-4 text-cyan-400" />
          </div>

          <div className="relative flex items-center justify-between text-center flex-1 px-2">
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

                {/* Traveling light pulse flow */}
                <path 
                  d="M 20,25 C 90,5 150,45 220,25 C 290,5 350,45 420,25 C 490,5 550,45 580,25" 
                  fill="none" 
                  stroke="#ffffff" 
                  strokeWidth="4"
                  strokeDasharray="60 520"
                  className="animate-[compromise-pulse_4s_linear_infinite] @media (prefers-reduced-motion: reduce):hidden"
                  filter="url(#comp-glow)"
                />

                {/* Waypoint hex-dot markers at 5 logical nodes */}
                {[30, 165, 300, 435, 570].map((cx, idx) => {
                  const delay = `${(idx * 0.9).toFixed(1)}s`;
                  return (
                    <g 
                      key={idx} 
                      transform={`translate(${cx}, 25)`} 
                      className="animate-waypoint-flash"
                      style={{ animationDelay: delay }}
                    >
                      <polygon 
                        points="0,-5 4.3,-2.5 4.3,2.5 0,5 -4.3,2.5 -4.3,-2.5" 
                        fill="#030305" 
                        stroke={idx % 2 === 0 ? "#00e5ff" : "#f5a623"} 
                        strokeWidth="1.5" 
                      />
                    </g>
                  );
                })}
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
