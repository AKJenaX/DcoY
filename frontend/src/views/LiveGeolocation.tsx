import React, { useState, useMemo } from "react";
import { useRealtimeChannel } from "../hooks/useRealtimeChannel";
import { MapPin, Info } from "lucide-react";
import { GlassPanel } from "../components/GlassPanel";

interface LocationData {
  ip: string;
  lat: number;
  lon: number;
  country: string;
  city: string;
  region: string;
  geo_source: "live" | "mock";
  severity?: "low" | "medium" | "high" | "critical";
}

export const LiveGeolocation: React.FC = () => {
  const { data: rawGeos, status: geoStatus, error: geoError } = useRealtimeChannel("geolocation");
  const [selectedIp, setSelectedIp] = useState<string | null>(null);
  const [filterSource, setFilterSource] = useState<"all" | "live" | "mock">("all");

  // Cast and clean coordinates list
  const geolocations = useMemo((): LocationData[] => {
    if (!Array.isArray(rawGeos)) return [];
    
    // De-duplicate by IP and filter out invalid lat/lon
    const map = new Map<string, LocationData>();
    rawGeos.forEach((item: any) => {
      if (item && item.ip && typeof item.lat === "number" && typeof item.lon === "number") {
        map.set(item.ip, {
          ip: item.ip,
          lat: item.lat,
          lon: item.lon,
          country: item.country || "Unknown",
          city: item.city || "Unknown",
          region: item.region || "Unknown",
          geo_source: item.geo_source || "live",
          severity: item.severity || (item.geo_source === "mock" ? "medium" : "high")
        });
      }
    });
    return Array.from(map.values());
  }, [rawGeos]);

  // Filter coordinates based on control options
  const filteredGeos = useMemo(() => {
    return geolocations.filter(loc => {
      if (filterSource === "all") return true;
      return loc.geo_source === filterSource;
    });
  }, [geolocations, filterSource]);

  // Find the selected location details
  const selectedLocation = useMemo(() => {
    return geolocations.find(loc => loc.ip === selectedIp) || null;
  }, [geolocations, selectedIp]);

  // Simple equirectangular projection mapping (lon: -180 to 180 -> x: 0 to 800, lat: -90 to 90 -> y: 400 to 0)
  const getXY = (lat: number, lon: number) => {
    const x = ((lon + 180) / 360) * 800;
    const y = ((90 - lat) / 180) * 400;
    return { x, y };
  };

  // Low-poly coordinates for simplified world continents map (fits the high-tech theme)
  const continents = [
    // North America
    "M 60,60 L 100,50 L 180,60 L 220,100 L 260,110 L 230,160 L 210,210 L 170,220 L 185,170 L 155,140 Z",
    // South America
    "M 185,230 L 240,240 L 220,320 L 190,370 L 180,370 L 175,280 Z",
    // Eurasia
    "M 360,60 L 460,50 L 600,45 L 720,50 L 760,100 L 700,160 L 680,210 L 600,210 L 580,240 L 520,230 L 480,180 L 460,200 L 420,180 L 400,100 Z",
    // Africa
    "M 360,195 L 420,185 L 460,215 L 480,260 L 450,330 L 415,350 L 380,270 L 350,230 Z",
    // Australia
    "M 650,290 L 720,300 L 710,340 L 660,335 Z",
    // Greenland
    "M 220,40 L 280,35 L 260,70 L 215,65 Z"
  ];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center pb-3 page-header-glass">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono text-cyan-400 uppercase tracking-widest mb-1">
            <span className="w-2 h-2 rounded-full bg-[#00ff66] animate-pulse shadow-[0_0_8px_#00ff66]"></span>
            CONSOLE.STATUS // TACTICAL_RESOLVER_ACTIVE
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white font-mono uppercase">Live Threat Geolocation</h1>
          <p className="text-xs text-gray-400">Real-time geographical resolution of active adversary scan origins</p>
        </div>
        <div>
          {geoStatus === "connected" && (
            <span className="flex items-center gap-1.5 text-[10px] bg-green-500/10 border border-green-500/30 px-2 py-0.5 rounded text-green-400 font-bold uppercase tracking-wider font-mono">
              <span className="w-1.5 h-1.5 bg-[#00ff66] rounded-full animate-pulse shadow-[0_0_6px_#00ff66]"></span> Live Link Armed
            </span>
          )}
          {(geoStatus === "connecting" || geoStatus === "reconnecting") && (
            <span className="flex items-center gap-1.5 text-[10px] bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded text-amber-400 font-bold uppercase tracking-wider animate-pulse font-mono">
              <span className="w-1.5 h-1.5 bg-[#ffb300] rounded-full animate-pulse shadow-[0_0_6px_#ffb300]"></span> Georesolver Syncing...
            </span>
          )}
          {geoStatus === "polling" && (
            <span className="flex items-center gap-1.5 text-[10px] bg-cyan-500/10 border border-cyan-500/30 px-2 py-0.5 rounded text-cyan-400 font-bold uppercase tracking-wider font-mono">
              <span className="w-1.5 h-1.5 bg-[#00e5ff] rounded-full animate-pulse shadow-[0_0_6px_#00e5ff]"></span> HTTP Resolver Fallback
            </span>
          )}
        </div>
      </div>

      {geoError && (
        <div className="p-3 bg-red-950/20 border border-red-500/50 rounded-md text-red-400 text-xs font-mono">
          [ERROR] {geoError}
        </div>
      )}

      {/* Main Map Content Block */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        
        {/* SVG Tactical Map container (3/4 width) */}
        <GlassPanel borderColor="cyan" className="xl:col-span-3 p-5 relative overflow-hidden flex flex-col items-center">
          {/* Tactical Background Grid */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(18,53,60,0.07)_1px,transparent_1px),linear-gradient(90deg,rgba(18,53,60,0.07)_1px,transparent_1px)] bg-[size:25px_25px] pointer-events-none"></div>
          
          <div className="relative w-full aspect-[2/1] min-h-[350px] max-h-[500px]">
            <svg 
              viewBox="0 0 800 400" 
              className="w-full h-full select-none"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* Latitude/Longitude grid lines */}
              <line x1="0" y1="200" x2="800" y2="200" className="stroke-cyan-500/20" strokeDasharray="5,5" />
              <line x1="400" y1="0" x2="400" y2="400" className="stroke-cyan-500/20" strokeDasharray="5,5" />
              <text x="405" y="15" className="fill-cyan-500/40 font-mono text-[9px]">Prime Meridian</text>
              <text x="5" y="195" className="fill-cyan-500/40 font-mono text-[9px]">Equator</text>
              
              {/* Continent Outlines */}
              {continents.map((d, index) => (
                <path 
                  key={index} 
                  d={d} 
                  className="fill-[#111c2a]/30 stroke-cyan-500/10 hover:stroke-cyan-500/20 transition-colors"
                  strokeWidth="1.5"
                />
              ))}

              {/* Plotted Threat Markers */}
              {filteredGeos.map((loc) => {
                const { x, y } = getXY(loc.lat, loc.lon);
                const isMock = loc.geo_source === "mock";
                const isSelected = selectedIp === loc.ip;
                const isCritical = loc.severity === "critical" || loc.severity === "high";
                
                return (
                  <g 
                    key={loc.ip} 
                    className="cursor-pointer group"
                    onClick={() => setSelectedIp(isSelected ? null : loc.ip)}
                  >
                    {isMock ? (
                      // Mock sandboxed coordinates (represented with dashed circles and a crosshair)
                      <>
                        <circle
                          cx={x}
                          cy={y}
                          r={isSelected ? 14 : 9}
                          className="stroke-amber-500/60 fill-none group-hover:stroke-amber-400 transition-all"
                          strokeDasharray="2,2"
                          strokeWidth={isSelected ? 2 : 1}
                        />
                        <line x1={x - 5} y1={y} x2={x + 5} y2={y} className="stroke-amber-500" strokeWidth="1" />
                        <line x1={x} y1={y - 5} x2={x} y2={y + 5} className="stroke-amber-500" strokeWidth="1" />
                        <circle cx={x} cy={y} r="2" className="fill-amber-500" />
                      </>
                    ) : (
                      // Live geo-resolved coordinates (glowing colored dot with animated ping radar ring)
                      <>
                        <circle
                          cx={x}
                          cy={y}
                          r={isSelected ? 16 : 10}
                          className={`fill-none transition-all ${
                            isCritical ? "stroke-red-500/30" : "stroke-cyan-500/30"
                          }`}
                          strokeWidth={2}
                        >
                          <animate
                            attributeName="r"
                            values="4;18;4"
                            dur="2.5s"
                            repeatCount="indefinite"
                          />
                          <animate
                            attributeName="opacity"
                            values="0.8;0;0.8"
                            dur="2.5s"
                            repeatCount="indefinite"
                          />
                        </circle>
                        <circle
                          cx={x}
                          cy={y}
                          r={isSelected ? 6 : 4}
                          className={`${
                            isCritical 
                              ? "fill-red-500 group-hover:fill-red-400" 
                              : "fill-cyan-400 group-hover:fill-cyan-300"
                          } transition-all`}
                        />
                      </>
                    )}
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Quick HUD status footer */}
          <div className="w-full flex justify-between items-center mt-3 pt-3 border-t border-cyan-500/10 text-[10px] font-mono text-gray-500">
            <span>GRID SYSTEM: MERCATOR 2D</span>
            <span>IP RESOLUTIONS RESOLVED: {geolocations.length}</span>
            <span>MAPPED THREAT CONTEXT: ACTIVE</span>
          </div>
        </GlassPanel>

        {/* Tactical controls & detailed side metrics (1/4 width) */}
        <div className="space-y-4">
          {/* Hex-shaped Map Legend / Controls */}
          <GlassPanel borderColor="cyan" className="p-5 space-y-4">
            <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 uppercase">
              <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
              TACTICAL.FILTERS // LEGEND
            </div>
            
            <div className="space-y-2">
              <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block">Source Node Group</span>
              <div className="grid grid-cols-3 gap-2">
                {[
                  ["all", "All"],
                  ["live", "Live"],
                  ["mock", "Sim"]
                ].map(([key, label]) => (
                  <button
                    key={key}
                    onClick={() => setFilterSource(key as any)}
                    className={`py-1 text-[10px] font-bold uppercase border rounded transition-all ${
                      filterSource === key
                        ? "bg-cyan-500/15 border-cyan-400 text-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.2)]"
                        : "bg-[#050a10] border-gray-800 text-gray-500 hover:border-gray-700 hover:text-gray-300"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-2 space-y-2.5">
              <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block">Threat Signature Legend</span>
              <div className="space-y-2 text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full fill-none border border-cyan-400 flex items-center justify-center">
                    <span className="w-1 h-1 bg-cyan-400 rounded-full"></span>
                  </span>
                  <span className="text-gray-300">Live Ingress (Low/Med Severity)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full fill-none border border-red-500 flex items-center justify-center animate-pulse">
                    <span className="w-1.5 h-1.5 bg-red-500 rounded-full"></span>
                  </span>
                  <span className="text-gray-300">High Risk Active Ingress</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 border border-dashed border-amber-500 rounded-full flex items-center justify-center">
                    <span className="text-[8px] text-amber-500 font-bold">+</span>
                  </span>
                  <span className="text-gray-300">Sandbox Sandbox Mock IP</span>
                </div>
              </div>
            </div>
          </GlassPanel>

          {/* Hex-shaped Map Node Details or General Info */}
          <GlassPanel borderColor="cyan" className="p-5 min-h-[180px] flex flex-col justify-between">
            {selectedLocation ? (
              <div className="space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-1.5 text-xs font-mono font-bold tracking-widest text-amber-500 uppercase">
                    <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,166,35,0.6)]"></span>
                    GEO.TARGET // ORIGIN ASSIGN
                  </div>
                  <button 
                    onClick={() => setSelectedIp(null)}
                    className="text-[9px] uppercase tracking-wider text-gray-500 hover:text-white font-mono"
                  >
                    Clear
                  </button>
                </div>

                <div className="space-y-2 text-xs font-mono bg-[#050b14]/90 p-3 border border-gray-800 rounded">
                  <div>
                    <span className="text-gray-500 block text-[9px] uppercase">IP Address</span>
                    <span className="text-cyan-400 font-bold">{selectedLocation.ip}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <span className="text-gray-500 block text-[9px] uppercase">Country</span>
                      <span className="text-gray-200">{selectedLocation.country}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 block text-[9px] uppercase">City</span>
                      <span className="text-gray-200">{selectedLocation.city}</span>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <span className="text-gray-500 block text-[9px] uppercase">Latitude</span>
                      <span className="text-gray-400">{selectedLocation.lat.toFixed(4)}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 block text-[9px] uppercase">Longitude</span>
                      <span className="text-gray-400">{selectedLocation.lon.toFixed(4)}</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-500 block text-[9px] uppercase">Resolver Feed Source</span>
                    <span className={`text-[9px] px-1 py-0.5 rounded font-bold uppercase inline-block ${
                      selectedLocation.geo_source === "mock"
                        ? "bg-amber-500/10 border border-amber-500/30 text-amber-500"
                        : "bg-green-500/10 border border-green-500/30 text-green-400"
                    }`}>
                      {selectedLocation.geo_source === "mock" ? "Mock sandbox" : "Live Resolved IP-API"}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-2 text-gray-500">
                <MapPin className="w-8 h-8 text-gray-600 mb-2 animate-bounce" />
                <span className="text-[10px] font-bold uppercase tracking-widest">Select Threat Node</span>
                <span className="text-[9px] mt-1 text-gray-600 max-w-[150px]">Click any coordinate marker on the tactical grid to inspect threat context.</span>
              </div>
            )}
            
            <div className="border-t border-cyan-500/10 pt-3 mt-3 flex items-center gap-2 text-[10px] text-gray-500 font-mono">
              <Info className="w-3.5 h-3.5 text-cyan-500" />
              <span>Click markers to pivot into raw asset trace.</span>
            </div>
          </GlassPanel>
        </div>

      </div>
    </div>
  );
};
