import React, { useEffect, useState, useRef } from "react";
import { api } from "../services/api";
import { ShieldAlert, Server, User, AlertOctagon, HelpCircle, Activity, Sparkles, RefreshCw } from "lucide-react";
import { EnergyRibbon } from "../components/EnergyRibbon";
import { GlassPanel } from "../components/GlassPanel";

interface Node {
  id: string;
  name: string;
  type: "Asset" | "User" | "Indicator" | "Case" | string;
  risk: number;
  criticality?: string;
  x?: number;
  y?: number;
}

interface Edge {
  source: string;
  target: string;
  relationship: string;
  weight: number;
}

interface HiveMapProps {
  initialNodeId?: string | null;
  onClearInitialNodeId?: () => void;
}

export const HiveMap: React.FC<HiveMapProps> = ({ initialNodeId, onClearInitialNodeId }) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  useEffect(() => {
    if (initialNodeId && nodes.length > 0) {
      // Find the node where ID matches either exactly or by label (Asset:1, User:compromised_operator)
      const match = nodes.find(n => n.id === initialNodeId || n.id.split(":")[1] === initialNodeId.split(":")[1]);
      if (match) {
        setSelectedNode(match);
      }
      if (onClearInitialNodeId) onClearInitialNodeId();
    }
  }, [initialNodeId, nodes]);
  const [startNodeId, setStartNodeId] = useState("");
  const [targetNodeId, setTargetNodeId] = useState("");
  const [shortestPath, setShortestPath] = useState<string[]>([]);
  const [aiPrompt, setAiPrompt] = useState("Explain attack paths & lateral vectors");
  const [aiAnswer, setAiAnswer] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [pathLoading, setPathLoading] = useState(false);
  const [error, setError] = useState("");

  const canvasRef = useRef<SVGSVGElement | null>(null);

  const loadGraph = async () => {
    try {
      setError("");
      const graphData = await api.getKnowledgeGraph();
      
      // Parse backend node structures (e.g. Asset:1, User:compromised_operator)
      const rawNodes = graphData.nodes || [];
      const rawEdges = graphData.edges || [];

      // Position nodes spread across full canvas with good initial spacing
      const cx = 480, cy = 300;
      const positionedNodes = rawNodes.map((node: any, idx: number) => {
        const angle = (idx / rawNodes.length) * 2 * Math.PI;
        const radius = 180 + Math.random() * 100;
        const rawName = node.name || node.label || node.id.split(":")[1] || node.id;
        return {
          id: node.id,
          name: rawName.length > 16 ? rawName.slice(0, 15) + "…" : rawName,
          type: node.type || node.id.split(":")[0] || "Asset",
          risk: node.risk_score || node.risk || 0.5,
          criticality: node.criticality || "Medium",
          x: cx + radius * Math.cos(angle),
          y: cy + radius * Math.sin(angle),
        };
      });

      setNodes(positionedNodes);
      setEdges(rawEdges);

      // Default selections
      if (positionedNodes.length > 1) {
        const indicators = positionedNodes.filter((n: any) => n.type === "Indicator");
        const assets = positionedNodes.filter((n: any) => n.type === "Asset");
        setStartNodeId(indicators[0]?.id || positionedNodes[0].id);
        setTargetNodeId(assets[0]?.id || positionedNodes[1].id);
      }
    } catch (err: any) {
      setError("Failed to fetch Knowledge Graph endpoints.");
    }
  };

  // Force-directed layout with cooling schedule so simulation settles
  const frameRef = useRef(0);
  useEffect(() => {
    if (nodes.length === 0) return;
    frameRef.current = 0;

    let animId: number;
    const maxFrames = 300;
    const forceStep = () => {
      frameRef.current++;
      const frame = frameRef.current;
      // Exponential cooling: alpha decays from 1.0 towards 0
      const alpha = Math.max(0.001, 1.0 - frame / maxFrames);
      if (alpha <= 0.002) return; // simulation settled, stop

      setNodes((prevNodes) => {
        const nextNodes = prevNodes.map((n) => ({ ...n }));
        const k = 0.02 * alpha; // Weak spring attraction scaled by alpha
        const repulsionStrength = 110000 * alpha; // Higher repulsion force
        
        // Repulsion forces + label-collision push
        for (let i = 0; i < nextNodes.length; i++) {
          for (let j = i + 1; j < nextNodes.length; j++) {
            let dx = nextNodes[j].x! - nextNodes[i].x!;
            let dy = nextNodes[j].y! - nextNodes[i].y!;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            
            // Radial repulsion — always active, strength falls off with distance²
            if (dist < 360) {
              const force = repulsionStrength / (dist * dist);
              const fx = force * (dx / dist);
              const fy = force * (dy / dist);
              nextNodes[i].x! -= fx;
              nextNodes[i].y! -= fy;
              nextNodes[j].x! += fx;
              nextNodes[j].y! += fy;
            }
            
            // Label-specific rectangular repulsion (labels are wider than tall)
            const hDist = Math.abs(dx);
            const vDist = Math.abs(dy);
            const minH = 175; // min horizontal separation for readable labels
            const minV = 95;  // min vertical separation
            if (hDist < minH && vDist < minV) {
              const pushX = (minH - hDist) * 0.4 * alpha * (dx >= 0 ? 1 : -1);
              const pushY = (minV - vDist) * 0.35 * alpha * (dy >= 0 ? 1 : -1);
              nextNodes[i].x! -= pushX;
              nextNodes[i].y! -= pushY;
              nextNodes[j].x! += pushX;
              nextNodes[j].y! += pushY;
            }
          }
        }

        // Spring attraction along edges (target distance increased to 180)
        edges.forEach((edge) => {
          const sNode = nextNodes.find((n) => n.id === edge.source);
          const tNode = nextNodes.find((n) => n.id === edge.target);
          if (sNode && tNode) {
            const dx = tNode.x! - sNode.x!;
            const dy = tNode.y! - sNode.y!;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            const force = k * (dist - 180);
            const fx = force * (dx / dist);
            const fy = force * (dy / dist);
            sNode.x! += fx;
            sNode.y! += fy;
            tNode.x! -= fx;
            tNode.y! -= fy;
          }
        });

        // Center gravity — pull nodes gently towards center of canvas
        const gravCx = 480, gravCy = 300;
        nextNodes.forEach((n) => {
          n.x! += (gravCx - n.x!) * 0.005 * alpha;
          n.y! += (gravCy - n.y!) * 0.005 * alpha;
        });

        // Boundary clamp
        nextNodes.forEach((n) => {
          n.x = Math.max(80, Math.min(880, n.x!));
          n.y = Math.max(60, Math.min(540, n.y!));
        });

        return nextNodes;
      });

      animId = requestAnimationFrame(forceStep);
    };

    animId = requestAnimationFrame(forceStep);
    return () => cancelAnimationFrame(animId);
  }, [edges.length]);

  useEffect(() => {
    loadGraph();
  }, []);

  // DIJKSTRA Shortest Path computation
  // BACKEND-BASED Shortest Path computation
  const calculatePath = async () => {
    if (!startNodeId || !targetNodeId) return;
    setPathLoading(true);
    setError("");
    try {
      const data = await api.getShortestPath(startNodeId, targetNodeId);
      if (data.path_found && data.steps) {
        setShortestPath(data.steps);
      } else {
        setShortestPath([]);
        setError("No traversal path found between selected nodes.");
      }
    } catch (err) {
      setError("Failed to calculate shortest propagation path on server.");
      setShortestPath([]);
    } finally {
      setPathLoading(false);
    }
  };

  const runAiCopilot = async () => {
    setAiLoading(true);
    setAiAnswer("");
    try {
      const data = await api.askGraphCopilot(aiPrompt);
      setAiAnswer(data.content || data.answer || "");
    } catch (err) {
      setError("AI graph assistant request failed.");
    } finally {
      setAiLoading(false);
    }
  };

  // Node Icons helper
  const getNodeIcon = (type: string) => {
    switch (type) {
      case "Asset":
        return <Server className="w-4 h-4 text-cyan-400" />;
      case "User":
        return <User className="w-4 h-4 text-amber-500" />;
      case "Indicator":
        return <ShieldAlert className="w-4 h-4 text-red-500" />;
      case "Case":
        return <AlertOctagon className="w-4 h-4 text-cyan-400" />;
      default:
        return <HelpCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getHexGlowColor = (risk: number) => {
    if (risk > 0.8) return "red";
    if (risk > 0.6) return "amber";
    return "cyan";
  };

  const panelStyle = {
    backdropFilter: "blur(24px)",
    WebkitBackdropFilter: "blur(24px)",
    background: "linear-gradient(135deg, rgba(245, 166, 35, 0.05) 0%, rgba(0, 0, 0, 0) 50%, rgba(0, 229, 255, 0.05) 100%), rgba(6, 9, 15, 0.65)",
    boxShadow: "0 0 25px rgba(0, 229, 255, 0.12), 0 0 50px rgba(0, 229, 255, 0.06), inset 0 0 0 1.5px rgba(0, 229, 255, 0.2)"
  };

  const centerPanelStyle = {
    backdropFilter: "blur(24px)",
    WebkitBackdropFilter: "blur(24px)",
    background: "linear-gradient(135deg, rgba(245, 166, 35, 0.04) 0%, rgba(0, 0, 0, 0) 50%, rgba(0, 229, 255, 0.04) 100%), rgba(5, 8, 14, 0.55)",
    boxShadow: "0 0 25px rgba(0, 229, 255, 0.12), 0 0 50px rgba(0, 229, 255, 0.06), inset 0 0 0 1.5px rgba(0, 229, 255, 0.2)"
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center pb-4 page-header-glass">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono text-cyan-400 uppercase tracking-widest mb-1">
            <span className="w-2 h-2 rounded-full bg-[#00ff66] animate-pulse shadow-[0_0_8px_#00ff66]"></span>
            CONSOLE.STATUS // TOPOLOGY_ACTIVE
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white font-mono uppercase">Hive Attack Path Map</h1>
          <p className="text-xs text-gray-400">Shortest path tracer and network propagation analysis</p>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-950/30 border border-red-500/50 rounded-md text-red-400 text-xs font-mono">
          [ALERT] {error}
        </div>
      )}

      {/* Main split dashboard panel */}
      <div className="grid grid-cols-1 xl:grid-cols-[220px_minmax(0,1fr)_240px] gap-5">
        {/* Left column: Path tracing control controls (1/4 width) */}
        <GlassPanel borderColor="cyan" className="p-4 space-y-4 h-[570px] flex flex-col justify-between" style={panelStyle}>
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-[10px] font-mono font-bold tracking-widest text-cyan-400 uppercase">
              <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
              PATH.TRACER // CONTROLS
            </div>
            
            <div className="space-y-2">
              <label className="text-xs text-gray-400">Threat Ingress Node:</label>
              <select
                value={startNodeId}
                onChange={(e) => setStartNodeId(e.target.value)}
                className="w-full bg-[#111827] border border-gray-800 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-amber-500"
              >
                {nodes.map((n) => (
                  <option key={n.id} value={n.id}>
                    [{n.type}] {n.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-gray-400">Target Asset Node:</label>
              <select
                value={targetNodeId}
                onChange={(e) => setTargetNodeId(e.target.value)}
                className="w-full bg-[#111827] border border-gray-800 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-amber-500"
              >
                {nodes.map((n) => (
                  <option key={n.id} value={n.id}>
                    [{n.type}] {n.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={calculatePath}
              disabled={pathLoading}
              className="w-full py-2 bg-amber-500 hover:bg-amber-600 disabled:bg-gray-800 disabled:text-gray-500 font-bold text-xs uppercase text-black rounded transition-all shadow-[0_0_15px_rgba(245,166,35,0.25)] flex items-center justify-center gap-1.5"
            >
              {pathLoading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Tracing Path...
                </>
              ) : (
                "Trace Shortest Path"
              )}
            </button>
          </div>

          {/* Shortest path results steps list */}
          {shortestPath.length > 0 && (
            <div className="flex-1 overflow-y-auto mt-4 space-y-2 border-t border-gray-800 pt-3">
              <span className="text-[10px] text-gray-400 uppercase tracking-wider block mb-1">Traversing Route:</span>
              {shortestPath.map((stepId, idx) => {
                const node = nodes.find((n) => n.id === stepId);
                return (
                  <div key={idx} className="flex items-center gap-2 text-xs font-semibold p-1.5 bg-[#111827]/60 rounded border border-gray-800">
                    <span className="text-[10px] text-amber-500 font-bold">#{idx + 1}</span>
                    <span className="truncate">{node?.name || stepId}</span>
                  </div>
                );
              })}
            </div>
          )}
        </GlassPanel>

        {/* Center column: Network Graph map panel (2/4 width) */}
        <GlassPanel borderColor="cyan" className="p-2 h-[570px] relative overflow-hidden z-10" style={centerPanelStyle}>
          <div className="absolute top-4 left-4 z-20 flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-amber-500 uppercase">
              <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,166,35,0.6)]"></span>
              MAP.TOPOLOGY // NETWORK GRAPH
            </div>
            <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/30 border border-cyan-500/20 px-2 py-0.5 rounded">
              {nodes.length} nodes / {edges.length} links
            </span>
          </div>

          <svg
            ref={canvasRef}
            className="w-full h-full relative z-10"
            viewBox="0 0 960 600"
          >
            <defs>
              <pattern id="hex-grid" width="24" height="24" patternUnits="userSpaceOnUse">
                <circle cx="12" cy="12" r="1" fill="rgba(245,166,35,0.06)" />
              </pattern>
              
              <linearGradient id="edge-idle-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#00e5ff" stopOpacity="0.22" />
                <stop offset="100%" stopColor="#f5a623" stopOpacity="0.22" />
              </linearGradient>
              
              <linearGradient id="edge-active-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#00e5ff" stopOpacity="0.75" />
                <stop offset="100%" stopColor="#f5a623" stopOpacity="0.75" />
              </linearGradient>

              <radialGradient id="node-bg-grad" cx="50%" cy="30%" r="60%" fx="50%" fy="30%">
                <stop offset="0%" stopColor="#1e293b" />
                <stop offset="100%" stopColor="#050b14" />
              </radialGradient>
              
              <radialGradient id="node-bg-grad-selected" cx="50%" cy="30%" r="60%" fx="50%" fy="30%">
                <stop offset="0%" stopColor="#334155" />
                <stop offset="100%" stopColor="#0b1329" />
              </radialGradient>

              <filter id="node-glow-red" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow dx="0" dy="0" stdDeviation="9" floodColor="#ef4444" floodOpacity="0.85"/>
              </filter>
              <filter id="node-glow-amber" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow dx="0" dy="0" stdDeviation="9" floodColor="#f5a623" floodOpacity="0.85"/>
              </filter>
              <filter id="node-glow-cyan" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow dx="0" dy="0" stdDeviation="9" floodColor="#00e5ff" floodOpacity="0.85"/>
              </filter>
            </defs>

            {/* Grid overlay background */}
            <rect width="960" height="600" fill="url(#hex-grid)" />

            {/* Render edges as glowing gradient lines */}
            {edges.map((edge, idx) => {
              const sNode = nodes.find((n) => n.id === edge.source);
              const tNode = nodes.find((n) => n.id === edge.target);
              if (!sNode || !tNode) return null;

              const isPathEdge = shortestPath.length > 0 &&
                shortestPath.indexOf(edge.source) !== -1 &&
                shortestPath.indexOf(edge.target) !== -1 &&
                Math.abs(shortestPath.indexOf(edge.source) - shortestPath.indexOf(edge.target)) === 1;

              return (
                <g key={idx}>
                  {isPathEdge ? (
                    <line
                      x1={sNode.x}
                      y1={sNode.y}
                      x2={tNode.x}
                      y2={tNode.y}
                      stroke="#f5a623"
                      strokeWidth={5}
                      strokeOpacity={0.25}
                      style={{ filter: "blur(3px)" }}
                    />
                  ) : (
                    <line
                      x1={sNode.x}
                      y1={sNode.y}
                      x2={tNode.x}
                      y2={tNode.y}
                      stroke="url(#edge-idle-grad)"
                      strokeWidth={3.5}
                      strokeOpacity={0.35}
                      style={{ filter: "blur(1.5px)" }}
                    />
                  )}
                  <line
                    x1={sNode.x}
                    y1={sNode.y}
                    x2={tNode.x}
                    y2={tNode.y}
                    stroke={isPathEdge ? "url(#edge-active-grad)" : "url(#edge-idle-grad)"}
                    strokeWidth={isPathEdge ? 3 : 1.5}
                  />
                </g>
              );
            })}

            {/* Dijkstra Path Energy Ribbon Tracing */}
            {(() => {
              const pathPoints = shortestPath
                .map((nodeId) => nodes.find((n) => n.id === nodeId))
                .filter((n): n is any => n !== undefined && n.x !== undefined && n.y !== undefined)
                .map((n) => ({ x: n.x, y: n.y }));

              if (pathPoints.length > 1) {
                return (
                  <EnergyRibbon
                    raw={true}
                    animate={true}
                    mode="map"
                    customPointsA={pathPoints}
                    customPointsB={pathPoints.map((p) => ({ x: p.x + 6, y: p.y + 6 }))}
                    width={960}
                    height={600}
                  />
                );
              }
              return null;
            })()}

            {/* Render nodes as hexagons */}
            {nodes.map((node) => {
              const glow = getHexGlowColor(node.risk);
              const isSelected = selectedNode?.id === node.id;
              const pathIdx = shortestPath.indexOf(node.id);
              
              let glowFilter = "url(#node-glow-cyan)";
              if (glow === "red") glowFilter = "url(#node-glow-red)";
              else if (glow === "amber") glowFilter = "url(#node-glow-amber)";

              const strokeColor = pathIdx !== -1
                ? "#f5a623"
                : glow === "red"
                ? "#ef4444"
                : glow === "amber"
                ? "#f5a623"
                : "#00e5ff";

              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x! - 22}, ${node.y! - 22})`}
                  className="cursor-pointer group"
                  onClick={() => setSelectedNode(node)}
                >
                  {/* Waypoint highlight outer dashed ring (spinning if active) */}
                  {pathIdx !== -1 && (
                    <polygon
                      points="22,-3 48,9.5 48,38.5 22,51 -4,38.5 -4,9.5"
                      fill="none"
                      stroke="#f5a623"
                      strokeWidth={1.5}
                      strokeDasharray="4, 4"
                      className="animate-spin"
                      style={{
                        transformOrigin: "22px 24px",
                        animationDuration: "12s",
                        filter: "drop-shadow(0 0 6px rgba(245, 166, 35, 0.8))"
                      }}
                    />
                  )}

                  {/* Layer 1: Beveled shadow offset layer for 3D extrusion */}
                  <polygon
                    points="22,1 43,12.5 43,35.5 22,47 1,35.5 1,12.5"
                    fill="#020406"
                    stroke="none"
                    transform="translate(2.5, 3.5)"
                  />

                  {/* Layer 2: Main hexagon with radial gradient and drop-shadow glow filter */}
                  <polygon
                    points="22,1 43,12.5 43,35.5 22,47 1,35.5 1,12.5"
                    fill={isSelected ? "url(#node-bg-grad-selected)" : "url(#node-bg-grad)"}
                    stroke={strokeColor}
                    strokeWidth={isSelected ? 2.5 : 1.5}
                    filter={isSelected ? "url(#node-glow-cyan)" : glowFilter}
                    className="transition-all duration-300 group-hover:scale-105"
                    style={{ transformOrigin: "22px 24px" }}
                  />

                  {/* Layer 3: Bevel facet highlight (translucent overlay on top half) */}
                  <polygon
                    points="22,1.5 41.5,12.5 22,23.5 2.5,12.5"
                    fill="rgba(255, 255, 255, 0.05)"
                    stroke="none"
                    pointerEvents="none"
                  />

                  {/* Waypoint center dot (pulsing indicator) */}
                  {pathIdx !== -1 && (
                    <circle 
                      cx="22" 
                      cy="24" 
                      r="16" 
                      fill="rgba(245, 166, 35, 0.08)" 
                      className="animate-pulse" 
                    />
                  )}

                  {/* Node Icon inside hexagon */}
                  <g transform="translate(14, 14)" className="pointer-events-none">
                    {getNodeIcon(node.type)}
                  </g>
                  {/* Text label */}
                  <text
                    x="22"
                    y="58"
                    textAnchor="middle"
                    fill="#F9FAFB"
                    className="text-[9px] font-bold font-mono tracking-wider opacity-85 group-hover:opacity-100 drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)] pointer-events-none"
                  >
                    {node.name}
                  </text>
                </g>
              );
            })}
          </svg>
        </GlassPanel>

        {/* Right column: Details drawer & AI assistant checks (1/4 width) */}
        <GlassPanel borderColor="cyan" className="p-4 space-y-4.5 h-[570px] flex flex-col overflow-y-auto scrollbar-thin" style={panelStyle}>
          {/* Inner gradient wash */}
          <div className="absolute inset-0 rounded-2xl pointer-events-none bg-gradient-to-br from-amber-500/[0.04] via-transparent to-cyan-500/[0.04] z-0" />
          
          {/* Active Node Inspector Section */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-[10px] font-mono font-bold tracking-widest text-cyan-400 border-b border-cyan-500/10 pb-1.5 uppercase">
              <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
              NODE.INSPECT // TELEMETRY
            </div>
            {selectedNode ? (
              <div className="space-y-2.5">
                <div className="flex items-center gap-2">
                  {getNodeIcon(selectedNode.type)}
                  <h3 className="text-xs font-bold text-white uppercase font-mono truncate w-36">{selectedNode.name}</h3>
                </div>
                <div className="space-y-1.5 text-[10px] font-mono bg-[#02050a]/40 p-2 rounded border border-gray-900">
                  <div className="flex justify-between">
                    <span className="text-gray-500">TYPE:</span>
                    <span className="text-gray-300 font-bold">{selectedNode.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">CRITICALITY:</span>
                    <span className="text-cyan-400 font-bold">{selectedNode.criticality}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">RISK INDEX:</span>
                    <span
                      className={`font-bold ${
                        selectedNode.risk > 0.8
                          ? "text-red-500"
                          : selectedNode.risk > 0.6
                          ? "text-amber-500"
                          : "text-green-500"
                      }`}
                    >
                      {(selectedNode.risk * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-5 text-center text-gray-500 font-mono text-[10px] bg-[#02050a]/40 rounded border border-gray-900/60">
                <Activity className="w-4 h-4 text-gray-650 mx-auto mb-1 animate-pulse" />
                <span>[AWAITING NODE SELECTION]</span>
              </div>
            )}
          </div>

          {/* Dynamic Top Vector Risks Ledger */}
          <div className="space-y-2 border-t border-gray-900/80 pt-3.5">
            <div className="text-[10px] text-cyan-400 font-bold font-mono tracking-wider uppercase">
              HIVE.RISKS // HIGH RISK VECTORS
            </div>
            <div className="space-y-1.5">
              {nodes.length > 0 ? (
                nodes
                  .filter(n => n.risk > 0.4)
                  .sort((a, b) => b.risk - a.risk)
                  .slice(0, 2)
                  .map(n => (
                    <div 
                      key={n.id} 
                      onClick={() => setSelectedNode(n)}
                      className={`p-2 bg-[#02050a]/80 border rounded flex justify-between items-center text-[10px] font-mono cursor-pointer transition-all hover:bg-[#111827]/40 ${
                        selectedNode?.id === n.id ? "border-red-500" : "border-red-500/15"
                      }`}
                    >
                      <span className="text-gray-300 truncate w-32 flex items-center gap-1.5">
                        <span className="w-1 h-1 bg-red-500 rounded-full animate-ping"></span>
                        {n.name}
                      </span>
                      <span className="text-red-400 font-black">{Math.round(n.risk * 100)}%</span>
                    </div>
                  ))
              ) : (
                <div className="text-[9px] text-gray-600 font-mono">No risks parsed yet.</div>
              )}
            </div>
          </div>

          {/* AI assistant Q&A */}
          <div className="border-t border-gray-900/80 pt-3.5 space-y-2.5">
            <div className="flex items-center gap-2 text-[10px] font-mono font-bold tracking-widest text-cyan-400 uppercase">
              <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
              AI.COPILOT // COGNITIVE AGENT
            </div>
            <select
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              className="w-full bg-[#111827] border border-gray-800 rounded px-2 py-1 text-[10px] text-white outline-none focus:border-cyan-500 font-mono"
            >
              <option value="Explain attack paths & lateral vectors">Explain attack paths & lateral vectors</option>
              <option value="Summarize active campaigns">Summarize active campaigns</option>
              <option value="Identify critical high-risk nodes">Identify critical high-risk nodes</option>
              <option value="Recommend detections & rules adjustments">Recommend detections & rules adjustments</option>
            </select>
            <button
              onClick={runAiCopilot}
              disabled={aiLoading}
              className="w-full py-1 bg-cyan-500 hover:bg-cyan-600 font-bold text-[10px] uppercase text-black rounded transition-all flex items-center justify-center gap-1 font-mono"
            >
              <Sparkles className="w-3 h-3" /> Explain Graph
            </button>
            {aiLoading && <div className="text-[9px] text-gray-500 text-center animate-pulse font-mono">Running model query...</div>}
            {aiAnswer && (
              <div className="p-2 bg-cyan-950/20 border border-cyan-500/20 text-cyan-200 rounded text-[9.5px] max-h-[85px] overflow-y-auto leading-relaxed scrollbar-thin font-mono">
                {aiAnswer}
              </div>
            )}
          </div>

          {/* Query Log History List */}
          <div className="space-y-1.5 border-t border-gray-900/80 pt-3.5 text-[9px] font-mono text-gray-500">
            <span className="uppercase font-bold text-gray-400 block tracking-widest">COGNITIVE.LOG // HISTORY</span>
            <div className="space-y-1.5 bg-[#02050a]/40 p-2 rounded border border-gray-900 max-h-[80px] overflow-y-auto scrollbar-thin">
              <div className="border-b border-gray-900/60 pb-1">
                <span className="text-amber-500/80 block">$ EXPLAIN PATHS:</span>
                <span className="text-gray-400 block truncate">Resolved lateral hops from threat origin.</span>
              </div>
              <div>
                <span className="text-amber-500/80 block">$ EXPLAIN RULE COVERAGE:</span>
                <span className="text-gray-400 block truncate">Evaluated rule T1046 correlation limits.</span>
              </div>
            </div>
          </div>

          {/* Operator Action Guide */}
          <div className="space-y-1 border-t border-gray-900/80 pt-3.5 text-[8.5px] font-mono text-gray-500">
            <span className="uppercase font-bold text-gray-450 tracking-wider block">OPERATOR Traversal GUIDE</span>
            <ul className="list-disc pl-3.5 space-y-0.5 leading-relaxed">
              <li>Select threat ingress and target asset nodes</li>
              <li>Click Tracer to compute Dijkstra propagation path</li>
              <li>Query AI Copilot for lateral segment containment</li>
            </ul>
          </div>
        </GlassPanel>
      </div>
    </div>
  );
};
