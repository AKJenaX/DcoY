import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { Hexagon } from "../components/Hexagon";
import { Bug, Terminal, Layers } from "lucide-react";

interface Decoy {
  id: string;
  name: string;
  type: "SSH" | "HTTP" | "Database";
  ip: string;
  status: "idle" | "engaging";
  attackerIp?: string;
  payloadData?: string[];
}

export const DeceptionGrid: React.FC = () => {
  const [decoys, setDecoys] = useState<Decoy[]>([
    {
      id: "decoy-1",
      name: "HONEYPOT-SSH-01",
      type: "SSH",
      ip: "198.51.100.42",
      status: "engaging",
      attackerIp: "185.220.101.5",
      payloadData: [
        "Connection from 185.220.101.5:43210",
        "T1110 brute-force login root:admin",
        "Failed login root:password123",
        "Failed login admin:admin",
        "SSH session closed - rate limited",
      ],
    },
    {
      id: "decoy-2",
      name: "HONEYPOT-HTTP-WEB",
      type: "HTTP",
      ip: "198.51.100.43",
      status: "engaging",
      attackerIp: "45.132.22.99",
      payloadData: [
        "GET /wp-admin.php from 45.132.22.99",
        "SQLi attempted on parameter 'id' - deflected",
        "Decoy admin panel loaded - dummy DB seeding",
        "Payload: UNION SELECT username, password FROM users",
      ],
    },
    {
      id: "decoy-3",
      name: "HONEYPOT-SQL-DB",
      type: "Database",
      ip: "198.51.100.44",
      status: "idle",
    },
    {
      id: "decoy-4",
      name: "HONEYPOT-SSH-02",
      type: "SSH",
      ip: "198.51.100.45",
      status: "idle",
    },
    {
      id: "decoy-5",
      name: "HONEYPOT-HTTP-API",
      type: "HTTP",
      ip: "198.51.100.46",
      status: "idle",
    },
    {
      id: "decoy-6",
      name: "HONEYPOT-REDIS",
      type: "Database",
      ip: "198.51.100.47",
      status: "idle",
    },
    {
      id: "decoy-7",
      name: "HONEYPOT-SMB",
      type: "SSH",
      ip: "198.51.100.48",
      status: "idle",
    },
    {
      id: "decoy-8",
      name: "HONEYPOT-WEB-02",
      type: "HTTP",
      ip: "198.51.100.49",
      status: "idle",
    },
    {
      id: "decoy-9",
      name: "HONEYPOT-MONGO",
      type: "Database",
      ip: "198.51.100.50",
      status: "engaging",
      attackerIp: "203.0.113.77",
      payloadData: [
        "Probe from 203.0.113.77:51802",
        "MongoDB unauthenticated listDatabases attempted",
        "Credential lure emitted fake admin hash",
      ],
    },
    {
      id: "decoy-10",
      name: "HONEYPOT-API-EDGE",
      type: "HTTP",
      ip: "198.51.100.51",
      status: "idle",
    },
  ]);

  const [selectedDecoyId, setSelectedDecoyId] = useState("decoy-1");
  const [filterType, setFilterType] = useState<"All" | "SSH" | "HTTP" | "Database">("All");

  const syncDecoysFromTelemetry = async () => {
    try {
      const logsData = await api.getDetectLogs();
      const events = logsData.events || [];

      // Look for any live honeypot engagement in backend telemetry
      const engagements = events.filter((e: any) => e.honeypot && e.honeypot !== "none");
      if (engagements.length > 0) {
        setDecoys((prevDecoys) => {
          const nextDecoys = [...prevDecoys];
          engagements.forEach((eng: any, idx: number) => {
            const index = idx % nextDecoys.length;
            nextDecoys[index] = {
              ...nextDecoys[index],
              status: "engaging",
              attackerIp: eng.ip || "198.51.100.42",
              payloadData: [
                `Event matched: ${eng.event_type || eng.event || "Honeypot hit"}`,
                `Attacker Node: ${eng.ip || "198.51.100.42"}`,
                `Response Action final: ${eng.response_action || "Block & Divert"}`,
                `Platform status: ${eng.response_status || "Decoy absorbing telemetry"}`
              ],
            };
          });
          return nextDecoys;
        });
      }
    } catch (e) {
      // Keep defaults
    }
  };

  useEffect(() => {
    syncDecoysFromTelemetry();
    const interval = setInterval(syncDecoysFromTelemetry, 5000);
    return () => clearInterval(interval);
  }, []);

  const selectedDecoy = decoys.find((d) => d.id === selectedDecoyId);
  const filteredDecoys = decoys.filter((d) => filterType === "All" || d.type === filterType);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-[#220 20% 15%] pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Deception Grid</h1>
          <p className="text-sm text-gray-400">Manage decoy systems, trap targets, and inspect engagements</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Honeycomb Grid Layout (2/3 width) */}
        <div className="xl:col-span-2 faceted-panel p-5 h-[570px] flex flex-col relative overflow-hidden bg-[#0d0f14]">
          <div className="absolute inset-0 opacity-30 hex-grid-overlay" />
          <div className="flex justify-between items-center mb-6 z-10">
            <h2 className="text-xs font-bold uppercase tracking-widest text-amber-500">Hive Decoy Topology</h2>
            <div className="flex gap-2">
              {(["All", "SSH", "HTTP", "Database"] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded border transition-all ${
                    filterType === type
                      ? "bg-amber-500 text-black border-amber-500"
                      : "bg-[#111827] text-gray-400 border-gray-800 hover:border-gray-700"
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* Tessellated Hex Layout using grid rows/columns offsets */}
          <div className="flex-1 flex items-center justify-center relative perspective-container z-10">
            <div className="grid grid-cols-5 gap-x-1 gap-y-0 max-w-4xl">
              {filteredDecoys.map((decoy, idx) => {
                // Apply a vertical offset for the middle column to simulate hex nesting
                const offsetClass = idx % 2 === 1 ? "translate-y-12" : "";
                const isEngaging = decoy.status === "engaging";

                return (
                  <div key={decoy.id} className={`transition-all ${offsetClass} tile-3d-elevation`}>
                    <Hexagon
                      size={128}
                      glowColor={isEngaging ? "amber" : "none"}
                      pulse={isEngaging}
                      onClick={() => setSelectedDecoyId(decoy.id)}
                    >
                      <Bug className={`w-4 h-4 mb-1 ${isEngaging ? "text-amber-500" : "text-gray-500"}`} />
                      <span className="text-[9px] font-bold font-mono tracking-wider truncate w-24">{decoy.name}</span>
                      <span className="text-[8px] text-gray-500 mt-1 uppercase">{decoy.type}</span>
                    </Hexagon>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Live Attack Engagement Inspector (1/3 width) */}
        <div className="faceted-panel p-5 h-[570px] flex flex-col bg-[#111827]">
          {selectedDecoy ? (
            <div className="space-y-4 flex-grow flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start border-b border-gray-800 pb-3">
                  <div>
                    <h3 className="text-sm font-bold text-white font-mono">{selectedDecoy.name}</h3>
                    <span className="text-[10px] text-gray-400 font-mono">IP: {selectedDecoy.ip}</span>
                  </div>
                  <span
                    className={`px-2 py-0.5 text-[8px] font-bold uppercase rounded border ${
                      selectedDecoy.status === "engaging"
                        ? "bg-amber-500/10 border-amber-500/30 text-amber-500 animate-pulse"
                        : "bg-gray-800 border-gray-700 text-gray-400"
                    }`}
                  >
                    {selectedDecoy.status === "engaging" ? "🔥 ENGAGING ATTACKER" : "IDLE"}
                  </span>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
                  <div className="p-2 bg-[#0a0b0d] border border-gray-800 rounded">
                    <span className="text-[10px] text-gray-400 block mb-1">DECOY TYPE</span>
                    <span className="font-bold text-cyan-400">{selectedDecoy.type}</span>
                  </div>
                  <div className="p-2 bg-[#0a0b0d] border border-gray-800 rounded">
                    <span className="text-[10px] text-gray-400 block mb-1">ATTACK SOURCE</span>
                    <span className="font-bold font-mono text-red-400">{selectedDecoy.attackerIp || "None"}</span>
                  </div>
                </div>
              </div>

              {/* Monospace scrolling payload feed */}
              <div className="flex-grow flex flex-col mt-4 min-h-[180px]">
                <span className="text-[10px] text-gray-400 uppercase tracking-widest block mb-1.5 flex items-center gap-1">
                  <Terminal className="w-3.5 h-3.5 text-amber-500" /> Decoy Engagement Payload Log
                </span>
                <div className="flex-1 p-3 bg-[#050b14] border border-gray-800 rounded-lg font-mono text-[10px] text-green-400 overflow-y-auto space-y-1.5 scrollbar-thin">
                  {selectedDecoy.payloadData ? (
                    selectedDecoy.payloadData.map((line, idx) => <div key={idx}>$ {line}</div>)
                  ) : (
                    <div className="text-gray-600 text-center py-10">Standby. Awaiting telemetry ingress match...</div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-grow flex flex-col items-center justify-center text-center text-gray-500">
              <Layers className="w-8 h-8 text-gray-600 mb-2 animate-pulse" />
              <span className="text-xs">Select decoy node to inspect payloads</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
