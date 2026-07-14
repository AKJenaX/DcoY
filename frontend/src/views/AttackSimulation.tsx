import React, { useState, useMemo } from "react";
import { api } from "../services/api";
import { useRealtimeChannel } from "../hooks/useRealtimeChannel";
import { Play, Cpu } from "lucide-react";
import { GlassPanel } from "../components/GlassPanel";

interface SimulationStep {
  timestamp: string;
  technique: string;
  host: string;
  user: string;
  severity: string;
  detection_status: "Detected" | "Missed";
  detection_latency_sec: number;
  matching_rules: Array<{ id: number; name: string; severity: string }>;
  details: Record<string, any>;
}

interface SimulationState {
  run_id: number;
  scenario_name: string;
  status: "started" | "running" | "completed" | "failed";
  step: number;
  total_steps: number;
  event?: SimulationStep;
  results?: {
    triggered_rules: Array<{ id: number; name: string; mitre_technique: string; severity: string }>;
    missed_rules: Array<{ id: number; name: string; mitre_technique: string; severity: string }>;
    timeline: SimulationStep[];
    executive_summary: {
      simulation_score: number;
      coverage_score: number;
      major_gaps: string[];
      recommended_improvements: string[];
      risk_summary: string;
    };
  };
}

export const AttackSimulation: React.FC = () => {
  const { data: rawSim, status: simStatus, error: simError } = useRealtimeChannel("simulation");
  const [selectedScenario, setSelectedScenario] = useState("SSH Brute Force");
  const [triggering, setTriggering] = useState(false);
  const [apiError, setApiError] = useState("");

  const scenarioOptions = [
    "SSH Brute Force",
    "Phishing",
    "Password Spraying",
    "Port Scan",
    "Privilege Escalation",
    "Lateral Movement",
    "Beaconing",
    "Suspicious PowerShell",
    "Data Exfiltration",
    "Ransomware"
  ];

  // Cast simulation state
  const currentSim = rawSim as SimulationState | null;

  const triggerSim = async () => {
    try {
      setTriggering(true);
      setApiError("");
      await api.triggerSimulation(selectedScenario);
    } catch (err: any) {
      setApiError(err.message || "Failed to trigger simulation.");
    } finally {
      setTriggering(false);
    }
  };

  // Determine active node and paths for the mini-network visualization based on current state
  const networkState = useMemo(() => {
    if (!currentSim || currentSim.status === "completed" || !currentSim.event) {
      return { activeNode: null, activeEdge: null };
    }
    
    const event = currentSim.event;
    const phase = (event.details?.phase || "").toLowerCase();
    const technique = (event.technique || "").toLowerCase();

    let activeNode = "internet";
    let activeEdge = null;

    if (phase.includes("initial") || technique.includes("phishing") || technique.includes("scan")) {
      activeNode = "internet";
      activeEdge = "internet-router";
    } else if (phase.includes("credential") || technique.includes("brute") || technique.includes("spray")) {
      if (event.host.toLowerCase().includes("honeypot") || event.host.toLowerCase().includes("decoy")) {
        activeNode = "decoy";
        activeEdge = "router-decoy";
      } else {
        activeNode = "workstation";
        activeEdge = "router-workstation";
      }
    } else if (phase.includes("escalation") || phase.includes("execution")) {
      activeNode = "workstation";
      activeEdge = "router-workstation";
    } else if (phase.includes("lateral") || event.host.toLowerCase().includes("dc") || event.host.toLowerCase().includes("server")) {
      activeNode = "domain_controller";
      activeEdge = "workstation-dc";
    } else if (phase.includes("exfil") || phase.includes("c2") || technique.includes("exfiltration")) {
      activeNode = "internet";
      activeEdge = "dc-internet";
    }

    return { activeNode, activeEdge };
  }, [currentSim]);

  // Coordinates of node points for the network visualization SVG (w: 500, h: 250)
  const nodes = {
    internet: { x: 50, y: 125, label: "Internet Threat Node" },
    router: { x: 180, y: 125, label: "Firewall / Router" },
    workstation: { x: 320, y: 65, label: "Operator Workstation" },
    decoy: { x: 320, y: 185, label: "Honeypot Decoy Mesh" },
    domain_controller: { x: 450, y: 125, label: "Corp AD DC" }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center pb-4 page-header-glass">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono text-cyan-400 uppercase tracking-widest mb-1">
            <span className="w-2 h-2 rounded-full bg-[#00ff66] animate-pulse shadow-[0_0_8px_#00ff66]"></span>
            CONSOLE.STATUS // ADVERSARY_SIMULATOR_STANDBY
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white font-mono uppercase">Adversary Attack Simulation</h1>
          <p className="text-xs text-gray-400">Coordinated purple-team playbook simulations and detection testing</p>
        </div>
        <div>
          {simStatus === "connected" && (
            <span className="flex items-center gap-1.5 text-[10px] bg-green-500/10 border border-green-500/30 px-2 py-0.5 rounded text-green-400 font-bold uppercase tracking-wider font-mono">
              <span className="w-1.5 h-1.5 bg-[#00ff66] rounded-full animate-pulse shadow-[0_0_6px_#00ff66]"></span> Simulation Link Connected
            </span>
          )}
          {(simStatus === "connecting" || simStatus === "reconnecting") && (
            <span className="flex items-center gap-1.5 text-[10px] bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded text-amber-400 font-bold uppercase tracking-wider animate-pulse font-mono">
              <span className="w-1.5 h-1.5 bg-[#ffb300] rounded-full animate-pulse shadow-[0_0_6px_#ffb300]"></span> WS Link Reconnecting...
            </span>
          )}
          {simStatus === "polling" && (
            <span className="flex items-center gap-1.5 text-[10px] bg-cyan-500/10 border border-cyan-500/30 px-2 py-0.5 rounded text-cyan-400 font-bold uppercase tracking-wider font-mono">
              <span className="w-1.5 h-1.5 bg-[#00e5ff] rounded-full animate-pulse shadow-[0_0_6px_#00e5ff]"></span> HTTP Polling Mode
            </span>
          )}
        </div>
      </div>

      {(simError || apiError) && (
        <div className="p-3 bg-red-950/20 border border-red-500/50 rounded-md text-red-400 text-xs font-mono">
          [ALERT] {simError || apiError}
        </div>
      )}

      {/* Main Simulation Hub Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Controller Form & Active Progress HUD */}
        <div className="space-y-4 lg:col-span-1">
          {/* Controller Card */}
          <GlassPanel borderColor="cyan" className="p-5 space-y-4">
            <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-amber-500 border-b border-amber-500/15 pb-2 uppercase">
              <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,166,35,0.6)]"></span>
              SIM.CONTROL // RUN CONFIG
            </div>
            
            <div className="space-y-1.5">
              <label className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Select Attack Scenario</label>
              <select
                value={selectedScenario}
                onChange={(e) => setSelectedScenario(e.target.value)}
                disabled={currentSim?.status === "running"}
                className="w-full bg-[#050b14] border border-gray-800 rounded px-3 py-2 text-xs text-white outline-none focus:border-amber-500"
              >
                {scenarioOptions.map(opt => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>

            <button
              onClick={triggerSim}
              disabled={triggering || currentSim?.status === "running"}
              className="w-full py-2.5 bg-amber-500 hover:bg-amber-600 disabled:bg-gray-800 disabled:text-gray-500 font-bold text-xs uppercase text-black rounded transition-all shadow-[0_0_15px_rgba(245,166,35,0.15)] flex items-center justify-center gap-2"
            >
              <Play className="w-3.5 h-3.5 fill-black" />
              {currentSim?.status === "running" ? "Simulation Running..." : "Execute Simulation"}
            </button>
          </GlassPanel>

          {/* Active Simulation Step HUD */}
          <GlassPanel borderColor="cyan" className="p-5 space-y-4 flex-1">
            <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 uppercase">
              <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
              SIM.PROGRESS // ACTIVE HUD
            </div>

            {currentSim && (currentSim.status === "running" || currentSim.status === "started") ? (
              <div className="space-y-4 font-mono text-xs">
                <div>
                  <span className="text-gray-500 block text-[9px] uppercase">Active Scenario</span>
                  <span className="text-white font-bold">{currentSim.scenario_name}</span>
                </div>
                
                {/* Segmented Progress bar */}
                <div>
                  <div className="flex justify-between text-[9px] text-gray-400 mb-1">
                    <span>STEP {currentSim.step} OF {currentSim.total_steps}</span>
                    <span>{Math.round((currentSim.step / currentSim.total_steps) * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-900 border border-gray-800 h-2 rounded overflow-hidden flex gap-0.5">
                    {Array.from({ length: currentSim.total_steps }).map((_, i) => (
                      <div 
                        key={i} 
                        className={`flex-1 h-full transition-all ${
                          i < currentSim.step ? "bg-amber-500" : "bg-gray-800"
                        }`}
                      />
                    ))}
                  </div>
                </div>

                {currentSim.event && (
                  <div className="space-y-2 bg-[#050b14] border border-gray-800 rounded p-3 text-[11px] leading-relaxed">
                    <div>
                      <span className="text-gray-500 block text-[9px] uppercase">Phase / Stage</span>
                      <span className="text-amber-500 font-bold uppercase tracking-wide">
                        {currentSim.event.details?.phase || "Execution"}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 block text-[9px] uppercase">Technique</span>
                      <span className="text-white">{currentSim.event.technique}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 block text-[9px] uppercase">Host Node</span>
                      <span className="text-cyan-400 font-bold">{currentSim.event.host}</span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-6 text-gray-500 text-xs flex flex-col items-center">
                <Cpu className="w-8 h-8 text-gray-600 mb-2 animate-pulse" />
                <span className="text-[10px] font-bold uppercase tracking-widest">Simulator Standby</span>
                <span className="text-[9px] mt-1 text-gray-600">Select a scenario above to run automated defensive validation.</span>
              </div>
            )}
          </GlassPanel>
        </div>

        {/* Right Side: Visual Graph & scrolling logs / completed stats (2/3 width) */}
        <div className="space-y-4 lg:col-span-2">
          
          {/* Mini-Network Map Panel */}
          <GlassPanel borderColor="cyan" className="p-5 flex flex-col justify-between">
            <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 mb-3 uppercase">
              <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
              SIM.TOPOLOGY // SUBNET VECTORS
            </div>

            <div className="w-full aspect-[2/1] min-h-[220px] max-h-[300px]">
              <svg viewBox="0 0 500 250" className="w-full h-full">
                {/* Router to nodes connections */}
                <line 
                  x1={nodes.internet.x} y1={nodes.internet.y} 
                  x2={nodes.router.x} y2={nodes.router.y} 
                  className={`stroke-2 ${networkState.activeEdge === "internet-router" ? "stroke-amber-500" : "stroke-cyan-500/20"}`} 
                />
                <line 
                  x1={nodes.router.x} y1={nodes.router.y} 
                  x2={nodes.workstation.x} y2={nodes.workstation.y} 
                  className={`stroke-2 ${networkState.activeEdge === "router-workstation" ? "stroke-amber-500" : "stroke-cyan-500/20"}`} 
                />
                <line 
                  x1={nodes.router.x} y1={nodes.router.y} 
                  x2={nodes.decoy.x} y2={nodes.decoy.y} 
                  className={`stroke-2 ${networkState.activeEdge === "router-decoy" ? "stroke-amber-500" : "stroke-cyan-500/20"}`} 
                />
                <line 
                  x1={nodes.workstation.x} y1={nodes.workstation.y} 
                  x2={nodes.domain_controller.x} y2={nodes.domain_controller.y} 
                  className={`stroke-2 ${networkState.activeEdge === "workstation-dc" ? "stroke-amber-500" : "stroke-cyan-500/20"}`} 
                />
                <line 
                  x1={nodes.domain_controller.x} y1={nodes.domain_controller.y} 
                  x2={nodes.internet.x} y2={nodes.internet.y} 
                  className={`stroke-2 ${networkState.activeEdge === "dc-internet" ? "stroke-amber-500" : "stroke-cyan-500/20"}`} 
                />

                {/* Nodes drawing */}
                {Object.entries(nodes).map(([key, node]) => {
                  const isActive = networkState.activeNode === key;
                  const isDecoy = key === "decoy";
                  
                  return (
                    <g key={key}>
                      <circle 
                        cx={node.x} 
                        cy={node.y} 
                        r={isActive ? 14 : 9} 
                        className={`transition-all duration-300 ${
                          isActive 
                            ? "fill-amber-500/25 stroke-amber-500 stroke-2" 
                            : isDecoy 
                            ? "fill-[#050b14] stroke-amber-500/50 stroke border-dashed"
                            : "fill-[#0c121b] stroke-cyan-500/30"
                        }`}
                      >
                        {isActive && (
                          <animate 
                            attributeName="r" 
                            values="10;18;10" 
                            dur="1.5s" 
                            repeatCount="indefinite" 
                          />
                        )}
                      </circle>
                      <text 
                        x={node.x} 
                        y={node.y + 22} 
                        textAnchor="middle" 
                        className="fill-gray-400 font-mono text-[8px] uppercase tracking-wider font-bold"
                      >
                        {node.label}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          </GlassPanel>

          {/* Results Summary or Timeline Console logs */}
          {currentSim?.status === "completed" && currentSim.results ? (
            /* Completed stats view */
            <GlassPanel borderColor="cyan" className="p-5 space-y-4 animate-fade-in">
              <div className="flex justify-between items-center border-b border-green-500/20 pb-2">
                <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-green-400 uppercase">
                  <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse shadow-[0_0_6px_#00ff66]"></span>
                  SIM.RESULTS // SCORE SUMMARY
                </div>
                <span className="text-[10px] bg-green-500/10 border border-green-500/30 px-2 py-0.5 rounded text-green-400 font-mono">
                  CONFIDENCE: {Math.round(currentSim.results.executive_summary.simulation_score)}%
                </span>
              </div>

              {/* KPIs strip */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  ["Detection Score", `${currentSim.results.executive_summary.simulation_score}%`, "text-amber-500"],
                  ["Coverage Score", `${currentSim.results.executive_summary.coverage_score}%`, "text-cyan-400"],
                  ["Rules Matched", `${currentSim.results.triggered_rules.length}`, "text-green-400"],
                  ["Gaps Detected", `${currentSim.results.executive_summary.major_gaps.length}`, "text-red-400"]
                ].map(([label, val, color]) => (
                  <div key={label} className="bg-[#050b14] border border-gray-800 rounded p-3 text-center">
                    <div className="text-[9px] uppercase tracking-wider text-gray-500 mb-1">{label}</div>
                    <div className={`text-xl font-black font-mono ${color}`}>{val}</div>
                  </div>
                ))}
              </div>

              {/* Gaps and Recommendations */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono pt-1">
                <div className="bg-red-950/10 border border-red-500/10 rounded p-3 space-y-2">
                  <span className="text-[10px] text-red-400 font-bold uppercase tracking-wider block">Security Blindspots</span>
                  {currentSim.results.executive_summary.major_gaps.length > 0 ? (
                    <ul className="list-disc pl-4 space-y-1.5 text-gray-300">
                      {currentSim.results.executive_summary.major_gaps.map((g, idx) => (
                        <li key={idx}>{g}</li>
                      ))}
                    </ul>
                  ) : (
                    <span className="text-gray-500">No major coverage gaps detected.</span>
                  )}
                </div>

                <div className="bg-green-950/10 border border-green-500/10 rounded p-3 space-y-2">
                  <span className="text-[10px] text-green-400 font-bold uppercase tracking-wider block">Recommended Improvements</span>
                  <ul className="list-disc pl-4 space-y-1.5 text-gray-300">
                    {currentSim.results.executive_summary.recommended_improvements.map((imp, idx) => (
                      <li key={idx}>{imp}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </GlassPanel>
          ) : (
            /* Log timeline Console */
            <GlassPanel borderColor="cyan" className="p-5 h-[200px] flex flex-col">
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase">
                  <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
                  SIM.LOG // LIVE EVENT TELEMETRY
                </div>
              </div>
              <div className="flex-1 bg-[#050b14] border border-gray-900 rounded p-3 font-mono text-[11px] text-gray-400 overflow-y-auto space-y-1 scrollbar-thin">
                {!currentSim ? (
                  <div className="text-gray-600 text-center py-10 font-sans">Simulation log waiting...</div>
                ) : (
                  <>
                    <div className="text-gray-500 font-mono">[{new Date().toLocaleTimeString()}] [SIM_ENGINE] Inbound scenario session: initialized</div>
                    {currentSim.event && (
                      <div className="text-amber-500 font-mono">
                        [{new Date(currentSim.event.timestamp).toLocaleTimeString()}] [STAGE_{currentSim.step}] {currentSim.event.details?.phase?.toUpperCase()}: {currentSim.event.technique} targeting {currentSim.event.host} ({currentSim.event.detection_status})
                      </div>
                    )}
                  </>
                )}
              </div>
            </GlassPanel>
          )}

        </div>

      </div>
    </div>
  );
};
export default AttackSimulation;
