import React, { useEffect, useState, useRef } from "react";
import { api } from "../services/api";
import { ShieldAlert, Server, User, AlertOctagon, HelpCircle, Activity, Sparkles, RefreshCw } from "lucide-react";
import { EnergyRibbon } from "../components/EnergyRibbon";

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

      // Position nodes in a honeycomb/grid layout or circle initially
      const positionedNodes = rawNodes.map((node: any, idx: number) => {
        const angle = (idx / rawNodes.length) * 2 * Math.PI;
        const radius = 150 + Math.random() * 50;
        return {
          id: node.id,
          name: node.name || node.label || node.id.split(":")[1] || node.id,
          type: node.type || node.id.split(":")[0] || "Asset",
          risk: node.risk_score || node.risk || 0.5,
          criticality: node.criticality || "Medium",
          x: 300 + radius * Math.cos(angle),
          y: 250 + radius * Math.sin(angle),
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

  // Run a basic force simulation step inside a hook
  useEffect(() => {
    if (nodes.length === 0) return;

    let animId: number;
    const forceStep = () => {
      setNodes((prevNodes) => {
        const nextNodes = prevNodes.map((n) => ({ ...n }));
        const k = 0.08; // Spring constant
        const rep = 800; // Repulsion constant

        // Repulsion forces between all node pairs
        for (let i = 0; i < nextNodes.length; i++) {
          for (let j = i + 1; j < nextNodes.length; j++) {
            const dx = nextNodes[j].x! - nextNodes[i].x!;
            const dy = nextNodes[j].y! - nextNodes[i].y!;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            if (dist < 150) {
              const force = rep / (dist * dist);
              const fx = force * (dx / dist);
              const fy = force * (dy / dist);
              nextNodes[i].x! -= fx;
              nextNodes[i].y! -= fy;
              nextNodes[j].x! += fx;
              nextNodes[j].y! += fy;
            }
          }
        }

        // Attraction force along edges
        edges.forEach((edge) => {
          const sNode = nextNodes.find((n) => n.id === edge.source);
          const tNode = nextNodes.find((n) => n.id === edge.target);
          if (sNode && tNode) {
            const dx = tNode.x! - sNode.x!;
            const dy = tNode.y! - sNode.y!;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            const force = k * (dist - 100);
            const fx = force * (dx / dist);
            const fy = force * (dy / dist);
            sNode.x! += fx;
            sNode.y! += fy;
            tNode.x! -= fx;
            tNode.y! -= fy;
          }
        });

        // Boundary safety box
        nextNodes.forEach((n) => {
          n.x = Math.max(40, Math.min(680, n.x!));
          n.y = Math.max(40, Math.min(480, n.y!));
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-[#220 20% 15%] pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Hive Attack Path Map</h1>
          <p className="text-sm text-gray-400">Shortest path tracer and network propagation analysis</p>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-950/30 border border-red-500/50 rounded-md text-red-400 text-xs">
          {error}
        </div>
      )}

      {/* Main split dashboard panel */}
      <div className="grid grid-cols-1 xl:grid-cols-[220px_minmax(0,1fr)_240px] gap-5">
        {/* Left column: Path tracing control controls (1/4 width) */}
        <div className="faceted-panel p-4 space-y-4 h-[570px] flex flex-col justify-between">
          <div className="space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400">🧭 Path Tracer controls</h2>
            
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
        </div>

        {/* Center column: Network Graph map panel (2/4 width) */}
        <div className="faceted-panel p-2 h-[570px] relative overflow-hidden bg-[#0d0f14]">
          <div className="absolute top-4 left-4 z-10 flex items-center gap-3">
            <span className="text-xs font-bold uppercase tracking-widest text-amber-500">Live Hive Topology Map</span>
            <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/30 border border-cyan-500/20 px-2 py-0.5 rounded">
              {nodes.length} nodes / {edges.length} links
            </span>
          </div>

          <svg
            ref={canvasRef}
            className="w-full h-full"
            viewBox="0 0 720 520"
          >
            <defs>
              <pattern id="hex-grid" width="24" height="24" patternUnits="userSpaceOnUse">
                <circle cx="12" cy="12" r="1" fill="rgba(245,166,35,0.08)" />
              </pattern>
            </defs>

            {/* Grid overlay background */}
            <rect width="720" height="520" fill="url(#hex-grid)" />

            {/* Render edges */}
            {edges.map((edge, idx) => {
              const sNode = nodes.find((n) => n.id === edge.source);
              const tNode = nodes.find((n) => n.id === edge.target);
              if (!sNode || !tNode) return null;

              return (
                <line
                  key={idx}
                  x1={sNode.x}
                  y1={sNode.y}
                  x2={tNode.x}
                  y2={tNode.y}
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth={1.5}
                />
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
                    width={720}
                    height={520}
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

              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x! - 22}, ${node.y! - 22})`}
                  className="cursor-pointer group"
                  onClick={() => setSelectedNode(node)}
                >
                  {/* Hexagon polygon path */}
                  <polygon
                    points="22,1 43,12.5 43,35.5 22,47 1,35.5 1,12.5"
                    fill={isSelected ? "#1f2937" : "#111827"}
                    stroke={
                      pathIdx !== -1
                        ? "#f5a623"
                        : glow === "red"
                        ? "#ef4444"
                        : glow === "amber"
                        ? "#f5a623"
                        : "#00e5ff"
                    }
                    strokeWidth={isSelected ? 3 : 1.8}
                    style={{
                      filter: `drop-shadow(0 0 4px ${
                        glow === "red" ? "rgba(239,68,68,0.4)" : "rgba(0,229,255,0.4)"
                      })`,
                    }}
                  />
                  {/* Node Icon inside hexagon */}
                  <g transform="translate(14, 14)">
                    {getNodeIcon(node.type)}
                  </g>
                  {/* Text label */}
                  <text
                    x="22"
                    y="58"
                    textAnchor="middle"
                    fill="#F9FAFB"
                    className="text-[9px] font-bold font-mono tracking-wider opacity-80 group-hover:opacity-100"
                  >
                    {node.name}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Right column: Details drawer & AI assistant checks (1/4 width) */}
        <div className="faceted-panel p-4 space-y-4 h-[570px] flex flex-col overflow-y-auto">
          {selectedNode ? (
            <div className="space-y-4 flex-1">
              <div className="flex items-center gap-2 border-b border-gray-800 pb-2">
                {getNodeIcon(selectedNode.type)}
                <h3 className="text-sm font-bold text-white uppercase">{selectedNode.name}</h3>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-400">Type:</span>
                  <span className="font-semibold">{selectedNode.type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Criticality:</span>
                  <span className="font-semibold text-cyan-400">{selectedNode.criticality}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Risk Assessment:</span>
                  <span
                    className={`font-mono font-bold ${
                      selectedNode.risk > 0.8
                        ? "text-red-500"
                        : selectedNode.risk > 0.6
                        ? "text-amber-500"
                        : "text-green-500"
                    }`}
                  >
                    {selectedNode.risk.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center text-gray-500">
              <Activity className="w-8 h-8 text-gray-600 mb-2" />
              <span className="text-xs">Click a node to inspect parameters</span>
            </div>
          )}

          {/* AI assistant Q&A */}
          <div className="border-t border-gray-800 pt-4 space-y-3">
            <span className="text-xs font-bold uppercase tracking-widest text-cyan-400 block">AI Graph Copilot</span>
            <select
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              className="w-full bg-[#111827] border border-gray-800 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-cyan-500"
            >
              <option value="Explain attack paths & lateral vectors">Explain attack paths & lateral vectors</option>
              <option value="Summarize active campaigns">Summarize active campaigns</option>
              <option value="Identify critical high-risk nodes">Identify critical high-risk nodes</option>
              <option value="Recommend detections & rules adjustments">Recommend detections & rules adjustments</option>
            </select>
            <button
              onClick={runAiCopilot}
              disabled={aiLoading}
              className="w-full py-1.5 bg-cyan-500 hover:bg-cyan-600 font-bold text-xs uppercase text-black rounded transition-all flex items-center justify-center gap-1"
            >
              <Sparkles className="w-3.5 h-3.5" /> Explain Graph
            </button>
            {aiLoading && <div className="text-[10px] text-gray-400 text-center animate-pulse">Running model query...</div>}
            {aiAnswer && (
              <div className="p-2.5 bg-cyan-950/20 border border-cyan-500/20 text-cyan-200 rounded text-[11px] max-h-[140px] overflow-y-auto leading-relaxed scrollbar-thin">
                {aiAnswer}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
