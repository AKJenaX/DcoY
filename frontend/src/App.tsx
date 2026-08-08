import React, { useState, useEffect } from "react";
import { api } from "./services/api";
import { Overview } from "./views/Overview";
import { HiveMap } from "./views/HiveMap";
import { DeceptionGrid } from "./views/DeceptionGrid";
import { Investigations } from "./views/Investigations";
import { DetectionRules } from "./views/DetectionRules";
import { ThreatIntel } from "./views/ThreatIntel";
import { PdfReport } from "./views/PdfReport";
import { Login3DBackground } from "./components/Login3DBackground";
import { useRealtimeChannel } from "./hooks/useRealtimeChannel";
import { LiveGeolocation } from "./views/LiveGeolocation";
import { AttackSimulation } from "./views/AttackSimulation";
import { PlatformHealth } from "./views/PlatformHealth";
import { ExecutiveDashboard } from "./views/ExecutiveDashboard";
import { NavHexagon } from "./components/NavHexagon";
import { GlassPanel } from "./components/GlassPanel";

import {
  Shield,
  Activity,
  Radio,
  Clock,
  User,
  Compass,
  Bug,
  ClipboardList,
  Sliders,
  Globe,
  FileText,
  LogOut,
  MapPin,
  Target,
  Search,
  Award,
} from "lucide-react";

type ActivePage =
  | "overview"
  | "hivemap"
  | "deception"
  | "intel"
  | "geolocation"
  | "simulation"
  | "health"
  | "executive"
  | "investigations"
  | "rules"
  | "report";

export const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activePage, setActivePage] = useState<ActivePage>("overview");
  const { status: telemetryStatus } = useRealtimeChannel("telemetry");

  const [appSelectedCaseId, setAppSelectedCaseId] = useState<string | null>(null);
  const [appSelectedNodeId, setAppSelectedNodeId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults(null);
      return;
    }

    setIsSearching(true);
    const delayDebounce = setTimeout(async () => {
      try {
        const res = await api.globalSearch(searchQuery);
        setSearchResults(res);
      } catch (err) {
        console.error("Search error", err);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [searchQuery]);
  const [parallaxOffset, setParallaxOffset] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const isTouch = window.matchMedia("(pointer: coarse)").matches;
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (isTouch || prefersReducedMotion) return;

    const handleMouseMove = (e: MouseEvent) => {
      const nx = (e.clientX / window.innerWidth) - 0.5;
      const ny = (e.clientY / window.innerHeight) - 0.5;
      setParallaxOffset({
        x: -nx * 5, // -2.5px to +2.5px
        y: -ny * 5
      });
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);
  const handleSearchResultClick = (item: any) => {
    setIsSearchFocused(false);
    setSearchQuery("");
    
    const type = item.entity_type;
    const id = item.entity_id;
    
    if (type === "Case") {
      setAppSelectedCaseId(id);
      setActivePage("investigations");
    } else if (type === "Asset" || type === "User" || type === "Indicator") {
      const nodeId = id.includes(":") ? id : `${type}:${id}`;
      setAppSelectedNodeId(nodeId);
      setActivePage("hivemap");
    } else if (type === "Rule") {
      setActivePage("rules");
    } else if (type === "Simulation" || item.route === "simulation") {
      setActivePage("simulation");
    } else if (type === "Report" || item.route === "report") {
      setActivePage("report");
    } else if (item.route === "deception") {
      setActivePage("deception");
    } else if (item.route === "intel") {
      setActivePage("intel");
    }
  };
  
  // Login form state
  const [username, setUsername] = useState("operator");
  const [password, setPassword] = useState("secure_password");
  const [authError, setAuthError] = useState("");
  const [authSuccess, setAuthSuccess] = useState("");

  const [utcTime, setUtcTime] = useState("");
  const [toastMessage, setToastMessage] = useState("");

  useEffect(() => {
    setIsLoggedIn(api.isLoggedIn());
    const interval = setInterval(() => {
      setUtcTime(new Date().toUTCString().split(" ")[4]);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleExpired = () => {
      setIsLoggedIn(false);
      setAuthError("Session expired — please log in again");
    };

    const handleToast = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail.type === "clear") {
        setToastMessage("");
      } else {
        setToastMessage(detail.message);
      }
    };

    window.addEventListener("auth-session-expired", handleExpired);
    window.addEventListener("show-toast", handleToast);

    return () => {
      window.removeEventListener("auth-session-expired", handleExpired);
      window.removeEventListener("show-toast", handleToast);
    };
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError("");
    setAuthSuccess("");
    try {
      await api.login(username, password);
      window.history.pushState({}, "", "/");
      setIsLoggedIn(true);
    } catch (err: any) {
      setAuthError(err.message || "Authentication failed. Ensure the operator is registered.");
    }
  };

  const handleRegister = async () => {
    setAuthError("");
    setAuthSuccess("");
    try {
      await api.register(username, password);
      setAuthSuccess("Registration successful! You may now Log In.");
    } catch (err: any) {
      setAuthError(err.message || "Registration failed. User may already exist.");
    }
  };

  const handleLogout = () => {
    api.logout();
    setIsLoggedIn(false);
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-[#030305] flex items-center justify-center p-6 relative overflow-hidden">
        {/* Background container with HexField and EnergyRibbon */}
        <div className="absolute inset-0 z-0">
          <Login3DBackground />
        </div>

        {toastMessage && (
          <div className="fixed top-4 right-4 z-50 p-4 bg-amber-950/90 border border-amber-500/30 text-amber-300 font-mono text-xs rounded shadow-[0_0_20px_rgba(245,166,35,0.2)] animate-pulse flex items-center gap-2">
            <span className="w-2 h-2 bg-amber-500 rounded-full animate-ping"></span>
            {toastMessage}
          </div>
        )}

        <div className="z-10 grid w-full max-w-5xl grid-cols-1 gap-5 lg:grid-cols-[460px_minmax(0,1fr)] items-stretch">
          {/* Glass login form card */}
          <GlassPanel borderColor="amber" className="p-8 flex flex-col justify-between h-[520px]">
            <div>
              {/* Header block with status indicator */}
              <div className="border-b border-gray-800/60 pb-4 mb-5">
                <div className="flex items-center gap-2 text-amber-500 font-mono text-[10px] font-bold tracking-widest mb-1.5">
                  <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse shadow-[0_0_6px_#00ff66]"></span>
                  SYS.STATUS: SECURE
                </div>
                <h1 className="text-xl font-bold tracking-wider text-white font-mono uppercase">Operator Security Portal</h1>
                <p className="text-[9px] text-gray-500 font-mono tracking-wider mt-0.5">DECOY DEPLOYMENT VECTOR // AXIS-01</p>
              </div>

              {authError && (
                <div className="p-3 bg-red-950/20 border border-red-500/20 text-red-400 text-xs rounded mb-4 font-mono">
                  {authError}
                </div>
              )}

              {authSuccess && (
                <div className="p-3 bg-green-950/20 border border-green-500/20 text-green-400 text-xs rounded mb-4 font-mono">
                  {authSuccess}
                </div>
              )}

              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-1">
                  <label className="text-[10px] text-gray-400 font-mono tracking-widest uppercase">Operator Identity</label>
                  <div className="relative flex items-center">
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="w-full bg-white/[0.03] border border-white/[0.08] rounded px-3 py-2.5 pr-16 text-sm text-white outline-none focus:border-amber-500/50 focus:bg-white/[0.05] transition-all font-mono"
                      required
                    />
                    <span className="absolute right-3 text-[9px] text-amber-500/40 font-mono font-bold tracking-wider pointer-events-none">SECURE</span>
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] text-gray-400 font-mono tracking-widest uppercase">Authentication Vector</label>
                  <div className="relative flex items-center">
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full bg-white/[0.03] border border-white/[0.08] rounded px-3 py-2.5 pr-16 text-sm text-white outline-none focus:border-amber-500/50 focus:bg-white/[0.05] transition-all font-mono"
                      required
                    />
                    <span className="absolute right-3 text-[9px] text-amber-500/40 font-mono font-bold tracking-wider pointer-events-none">KEYCARD</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-2">
                  <button
                    type="submit"
                    className="py-2.5 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/50 font-bold text-xs uppercase text-amber-400 rounded transition-all font-mono shadow-[inset_0_1px_0_rgba(255,255,255,0.05)] hover:text-white"
                  >
                    Log In
                  </button>
                  <button
                    type="button"
                    onClick={handleRegister}
                    className="py-2.5 bg-white/[0.02] hover:bg-white/[0.06] border border-white/10 text-white font-bold text-xs uppercase rounded transition-all font-mono"
                  >
                    Register
                  </button>
                </div>
              </form>
            </div>

            {/* Footer metadata info */}
            <div className="border-t border-gray-800/60 pt-3 flex justify-between items-center font-mono text-[9px] text-gray-500">
              <span>SECURITY AUTH: LVL 4</span>
              <span className="text-amber-500/50 font-bold">RESTRICTED TERMINAL</span>
            </div>
          </GlassPanel>

          {/* Glass details stats card */}
          <GlassPanel borderColor="cyan" className="hidden lg:flex p-8 flex-col justify-between h-[520px]">
            <div>
              <div className="border-b border-gray-800/60 pb-4 mb-5">
                <span className="text-[10px] text-cyan-400 font-mono font-bold uppercase tracking-[0.2em]">Hive Defense</span>
                <h2 className="mt-1 text-2xl font-bold text-white font-mono leading-tight uppercase">Adaptive Decoy Mesh</h2>
                <p className="mt-1.5 text-xs text-gray-400 max-w-md font-sans">
                  Active defense fabric is standing by with deception telemetry, graph correlation, and response automation.
                </p>
              </div>

              <div className="grid grid-cols-3 gap-3">
                {[
                  ["18", "Edges watched", "text-cyan-400"],
                  ["06", "Decoys armed", "text-amber-500"],
                  ["24s", "Avg response", "text-green-400"],
                ].map(([value, label, color]) => (
                  <div key={label} className="bg-white/[0.02] border border-white/[0.06] rounded p-3">
                    <div className={`text-xl font-bold font-mono ${color}`}>{value}</div>
                    <div className="mt-1 text-[8px] uppercase tracking-wider text-gray-500 font-mono">{label}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              {[
                ["03:14:22", "SSH decoy port rotated across edge subnet"],
                ["03:14:30", "Credential spray probe diverted to honey account"],
                ["03:14:41", "Knowledge graph queued fresh attack-path trace"],
              ].map(([time, text]) => (
                <div key={text} className="flex items-center gap-3 border border-white/[0.04] bg-white/[0.01] rounded px-3 py-2 font-mono text-[9px]">
                  <Clock className="w-3.5 h-3.5 text-amber-500/70" />
                  <span className="text-gray-500">{time}</span>
                  <span className="text-gray-300">{text}</span>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between border-t border-gray-800/60 pt-3 text-[9px] font-mono font-bold uppercase tracking-widest">
              <span className="flex items-center gap-2 text-green-400">
                <Radio className="w-3.5 h-3.5 animate-pulse" /> Mesh stable
              </span>
              <span className="text-gray-500">SOC link encrypted</span>
            </div>
          </GlassPanel>
        </div>
      </div>
    );
  }

  const renderContent = () => {
    switch (activePage) {
      case "overview":
        return <Overview />;
      case "hivemap":
        return (
          <HiveMap 
            initialNodeId={appSelectedNodeId} 
            onClearInitialNodeId={() => setAppSelectedNodeId(null)} 
          />
        );
      case "deception":
        return <DeceptionGrid />;
      case "investigations":
        return (
          <Investigations 
            initialCaseId={appSelectedCaseId} 
            onClearInitialCaseId={() => setAppSelectedCaseId(null)} 
          />
        );
      case "rules":
        return <DetectionRules />;
      case "intel":
        return <ThreatIntel />;
      case "geolocation":
        return <LiveGeolocation />;
      case "simulation":
        return <AttackSimulation />;
      case "health":
        return <PlatformHealth />;
      case "executive":
        return <ExecutiveDashboard />;
      case "report":
        return <PdfReport />;
      default:
        return <Overview />;
    }
  };

  return (
    <div className="h-screen max-h-screen bg-[#030305] flex text-gray-300 relative overflow-hidden">
      {/* Hoisted Global Background */}
      <div 
        className="fixed inset-0 z-0 pointer-events-none select-none bg-[#030305] transition-transform duration-300 ease-out"
        style={{
          transform: `translate3d(${parallaxOffset.x * 0.3}px, ${parallaxOffset.y * 0.3}px, 0)`
        }}
      >
        <Login3DBackground mode="ambient" />
      </div>

      {/* Sidebar Navigation */}
      <aside 
        className="h-screen sticky top-0 w-64 border-r border-white/[0.03] flex flex-col justify-between p-5 z-20 overflow-hidden"
        style={{ backdropFilter: "blur(24px)", WebkitBackdropFilter: "blur(24px)", background: "linear-gradient(to right, rgba(5, 8, 14, 0.55) 0%, rgba(5, 8, 14, 0.40) 100%)" }}
      >

        <div className="flex-1 overflow-y-auto space-y-6 pr-1 custom-scrollbar z-10 relative">
          {/* Logo */}
          <div className="flex items-center gap-3 pb-4 border-b border-gray-800/80">
            <NavHexagon active={true} color="amber" size={32}>
              <Shield className="w-5 h-5 text-amber-500" />
            </NavHexagon>
            <div>
              <span className="font-bold text-white font-mono tracking-wider text-sm block">DcoY Console</span>
              <span className="text-[9px] text-amber-500 font-bold tracking-widest uppercase">Hive Defense</span>
            </div>
          </div>

          <nav className="space-y-4">
            <div className="space-y-1.5">
              <span className="text-[10px] text-gray-500 font-bold tracking-widest uppercase flex items-center gap-1.5 px-2 mb-2">
                <span className="group-label-tick text-cyan-400"></span>
                Monitoring
              </span>
              
              <button
                onClick={() => setActivePage("overview")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-all group ${
                  activePage === "overview"
                    ? "text-cyan-400 bg-cyan-950/15 border border-cyan-500/20 shadow-[0_0_15px_rgba(0,229,255,0.06)]"
                    : "text-gray-300 border border-transparent hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <div className={`p-1.5 rounded-md border transition-all duration-300 ${
                  activePage === "overview"
                    ? "bg-cyan-500/20 border-cyan-400/50 shadow-[0_0_8px_rgba(0,229,255,0.2)]"
                    : "bg-white/[0.02] border-white/[0.06] group-hover:bg-white/[0.06] group-hover:border-white/20"
                }`}>
                  <Activity className="w-3.5 h-3.5" />
                </div>
                <span className="font-mono tracking-wide">Command Overview</span>
              </button>

              <button
                onClick={() => setActivePage("hivemap")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-all group ${
                  activePage === "hivemap"
                    ? "text-cyan-400 bg-cyan-950/15 border border-cyan-500/20 shadow-[0_0_15px_rgba(0,229,255,0.06)]"
                    : "text-gray-300 border border-transparent hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <div className={`p-1.5 rounded-md border transition-all duration-300 ${
                  activePage === "hivemap"
                    ? "bg-cyan-500/20 border-cyan-400/50 shadow-[0_0_8px_rgba(0,229,255,0.2)]"
                    : "bg-white/[0.02] border-white/[0.06] group-hover:bg-white/[0.06] group-hover:border-white/20"
                }`}>
                  <Compass className="w-3.5 h-3.5" />
                </div>
                <span className="font-mono tracking-wide">Hive Map</span>
              </button>

              <button
                onClick={() => setActivePage("deception")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-all group ${
                  activePage === "deception"
                    ? "text-cyan-400 bg-cyan-950/15 border border-cyan-500/20 shadow-[0_0_15px_rgba(0,229,255,0.06)]"
                    : "text-gray-300 border border-transparent hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <div className={`p-1.5 rounded-md border transition-all duration-300 ${
                  activePage === "deception"
                    ? "bg-cyan-500/20 border-cyan-400/50 shadow-[0_0_8px_rgba(0,229,255,0.2)]"
                    : "bg-white/[0.02] border-white/[0.06] group-hover:bg-white/[0.06] group-hover:border-white/20"
                }`}>
                  <Bug className="w-3.5 h-3.5" />
                </div>
                <span className="font-mono tracking-wide">Deception Grid</span>
              </button>

              <button
                onClick={() => setActivePage("intel")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-all group ${
                  activePage === "intel"
                    ? "text-cyan-400 bg-cyan-950/15 border border-cyan-500/20 shadow-[0_0_15px_rgba(0,229,255,0.06)]"
                    : "text-gray-300 border border-transparent hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <div className={`p-1.5 rounded-md border transition-all duration-300 ${
                  activePage === "intel"
                    ? "bg-cyan-500/20 border-cyan-400/50 shadow-[0_0_8px_rgba(0,229,255,0.2)]"
                    : "bg-white/[0.02] border-white/[0.06] group-hover:bg-white/[0.06] group-hover:border-white/20"
                }`}>
                  <Globe className="w-3.5 h-3.5" />
                </div>
                <span className="font-mono tracking-wide">Threat Intel</span>
              </button>

              <button
                onClick={() => setActivePage("geolocation")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-all group ${
                  activePage === "geolocation"
                    ? "text-cyan-400 bg-cyan-950/15 border border-cyan-500/20 shadow-[0_0_15px_rgba(0,229,255,0.06)]"
                    : "text-gray-300 border border-transparent hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <div className={`p-1.5 rounded-md border transition-all duration-300 ${
                  activePage === "geolocation"
                    ? "bg-cyan-500/20 border-cyan-400/50 shadow-[0_0_8px_rgba(0,229,255,0.2)]"
                    : "bg-white/[0.02] border-white/[0.06] group-hover:bg-white/[0.06] group-hover:border-white/20"
                }`}>
                  <MapPin className="w-3.5 h-3.5" />
                </div>
                <span className="font-mono tracking-wide">Live Geolocation</span>
              </button>

              <button
                onClick={() => setActivePage("simulation")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-all group ${
                  activePage === "simulation"
                    ? "text-cyan-400 bg-cyan-950/15 border border-cyan-500/20 shadow-[0_0_15px_rgba(0,229,255,0.06)]"
                    : "text-gray-300 border border-transparent hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <div className={`p-1.5 rounded-md border transition-all duration-300 ${
                  activePage === "simulation"
                    ? "bg-cyan-500/20 border-cyan-400/50 shadow-[0_0_8px_rgba(0,229,255,0.2)]"
                    : "bg-white/[0.02] border-white/[0.06] group-hover:bg-white/[0.06] group-hover:border-white/20"
                }`}>
                  <Target className="w-3.5 h-3.5" />
                </div>
                <span className="font-mono tracking-wide">Attack Simulation</span>
              </button>

              <button
                onClick={() => setActivePage("health")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-all group ${
                  activePage === "health"
                    ? "text-cyan-400 bg-cyan-950/15 border border-cyan-500/20 shadow-[0_0_15px_rgba(0,229,255,0.06)]"
                    : "text-gray-300 border border-transparent hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <div className={`p-1.5 rounded-md border transition-all duration-300 ${
                  activePage === "health"
                    ? "bg-cyan-500/20 border-cyan-400/50 shadow-[0_0_8px_rgba(0,229,255,0.2)]"
                    : "bg-white/[0.02] border-white/[0.06] group-hover:bg-white/[0.06] group-hover:border-white/20"
                }`}>
                  <Activity className="w-3.5 h-3.5" />
                </div>
                <span className="font-mono tracking-wide">Platform Health</span>
              </button>
            </div>

            <div className="space-y-1.5">
              <span className="text-[10px] text-gray-500 font-bold tracking-widest uppercase flex items-center gap-1.5 px-2 mb-2">
                <span className="group-label-tick text-amber-500"></span>
                Management
              </span>

              <button
                onClick={() => setActivePage("investigations")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-all group ${
                  activePage === "investigations"
                    ? "text-amber-400 bg-amber-950/15 border border-amber-500/20 shadow-[0_0_15px_rgba(245,166,35,0.06)]"
                    : "text-gray-300 border border-transparent hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <div className={`p-1.5 rounded-md border transition-all duration-300 ${
                  activePage === "investigations"
                    ? "bg-amber-500/20 border-amber-400/50 shadow-[0_0_8px_rgba(245,166,35,0.2)]"
                    : "bg-white/[0.02] border-white/[0.06] group-hover:bg-white/[0.06] group-hover:border-white/20"
                }`}>
                  <ClipboardList className="w-3.5 h-3.5" />
                </div>
                <span className="font-mono tracking-wide">Investigations</span>
              </button>

              <button
                onClick={() => setActivePage("rules")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-all group ${
                  activePage === "rules"
                    ? "text-amber-400 bg-amber-950/15 border border-amber-500/20 shadow-[0_0_15px_rgba(245,166,35,0.06)]"
                    : "text-gray-300 border border-transparent hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <div className={`p-1.5 rounded-md border transition-all duration-300 ${
                  activePage === "rules"
                    ? "bg-amber-500/20 border-amber-400/50 shadow-[0_0_8px_rgba(245,166,35,0.2)]"
                    : "bg-white/[0.02] border-white/[0.06] group-hover:bg-white/[0.06] group-hover:border-white/20"
                }`}>
                  <Sliders className="w-3.5 h-3.5" />
                </div>
                <span className="font-mono tracking-wide">Detection Rules</span>
              </button>
            </div>

            <div className="space-y-1.5">
              <span className="text-[10px] text-gray-500 font-bold tracking-widest uppercase flex items-center gap-1.5 px-2 mb-2">
                <span className="group-label-tick text-amber-500"></span>
                Executive
              </span>

              <button
                onClick={() => setActivePage("executive")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-all group ${
                  activePage === "executive"
                    ? "text-amber-400 bg-amber-950/15 border border-amber-500/20 shadow-[0_0_15px_rgba(245,166,35,0.06)]"
                    : "text-gray-300 border border-transparent hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <div className={`p-1.5 rounded-md border transition-all duration-300 ${
                  activePage === "executive"
                    ? "bg-amber-500/20 border-amber-400/50 shadow-[0_0_8px_rgba(245,166,35,0.2)]"
                    : "bg-white/[0.02] border-white/[0.06] group-hover:bg-white/[0.06] group-hover:border-white/20"
                }`}>
                  <Award className="w-3.5 h-3.5" />
                </div>
                <span className="font-mono tracking-wide">Executive Dash</span>
              </button>

              <button
                onClick={() => setActivePage("report")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-all group ${
                  activePage === "report"
                    ? "text-amber-400 bg-amber-950/15 border border-amber-500/20 shadow-[0_0_15px_rgba(245,166,35,0.06)]"
                    : "text-gray-300 border border-transparent hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <div className={`p-1.5 rounded-md border transition-all duration-300 ${
                  activePage === "report"
                    ? "bg-amber-500/20 border-amber-400/50 shadow-[0_0_8px_rgba(245,166,35,0.2)]"
                    : "bg-white/[0.02] border-white/[0.06] group-hover:bg-white/[0.06] group-hover:border-white/20"
                }`}>
                  <FileText className="w-3.5 h-3.5" />
                </div>
                <span className="font-mono tracking-wide">PDF Reporting</span>
              </button>
            </div>
          </nav>
        </div>

        {/* System info & logout */}
        <div className="space-y-4 pt-4 border-t border-gray-800/80 z-10 relative">
          <div className="p-3 faceted-panel-status space-y-1.5 text-[10px]">
            <div className="flex justify-between">
              <span className="text-gray-500">DECOY SYSTEM:</span>
              <span className="text-green-500 font-bold">ONLINE</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">ANOMALY DETECT:</span>
              <span className="text-green-500 font-bold">STABLE</span>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs px-2">
            <span className="flex items-center gap-1.5 text-gray-400">
              <User className="w-3.5 h-3.5" /> operator
            </span>
            <button
              onClick={handleLogout}
              className="text-gray-500 hover:text-red-400 transition-colors p-1"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen max-h-screen overflow-hidden relative z-10">
        {/* Sticky Top Header Navigation */}
        <header className="sticky top-0 border-b border-white/[0.08] px-8 py-3 flex justify-between items-center z-10" style={{ backdropFilter: "blur(24px)", WebkitBackdropFilter: "blur(24px)", background: "rgba(5, 8, 14, 0.45)" }}>
          <div className="flex items-center gap-6 flex-1 max-w-2xl">
            <span className="text-xs font-mono font-bold tracking-wider text-gray-400 whitespace-nowrap">
              SECURE DOMAIN OPERATOR WORKSPACE
            </span>

            {/* Persistent Global Search Input & Dropdown Overlay */}
            <div className="relative flex-1 max-w-md hidden md:block">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Global Search (assets, users, cases, rules...)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onFocus={() => setIsSearchFocused(true)}
                  className="w-full bg-[#050b14]/80 border border-gray-800 rounded px-3 py-1.5 pl-8 text-xs text-white outline-none focus:border-cyan-500/50 transition-colors font-mono"
                />
                <Search className="w-3.5 h-3.5 text-gray-500 absolute left-2.5 top-2.5" />
                {isSearching && (
                  <div className="w-3.5 h-3.5 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin absolute right-2.5 top-2.5 animate-duration-1000" />
                )}
              </div>

              {/* Search Backdrop Overlay clicker */}
              {isSearchFocused && (
                <div 
                  className="fixed inset-0 z-40 bg-transparent" 
                  onClick={() => setIsSearchFocused(false)}
                />
              )}

              {/* Overlay dropdown container */}
              {isSearchFocused && searchQuery && (
                <div className="absolute left-0 right-0 mt-2 bg-[#080d16] border border-cyan-500/15 rounded-md shadow-2xl z-50 max-h-[380px] overflow-y-auto font-mono text-[11px] p-3 divide-y divide-gray-900/60">
                  {searchResults && Object.keys(searchResults).some(key => searchResults[key]?.length > 0) ? (
                    Object.entries(searchResults).map(([key, list]: [string, any]) => {
                      if (!list || list.length === 0) return null;
                      return (
                        <div key={key} className="py-2 first:pt-0 last:pb-0">
                          <span className="text-[8px] text-cyan-400/80 font-bold uppercase tracking-wider block mb-1">
                            {key === "cases" ? "📂 Cases & Investigations" : (key === "assets" ? "🖥️ Enterprise Assets" : (key === "users" ? "👤 User Accounts" : (key === "rules" ? "🛡️ Detection Rules" : key.toUpperCase())))}
                          </span>
                          <div className="space-y-1">
                            {list.map((item: any, idx: number) => (
                              <div
                                key={idx}
                                onClick={() => handleSearchResultClick(item)}
                                className="p-1.5 rounded hover:bg-cyan-500/10 cursor-pointer flex justify-between items-center transition-colors group"
                              >
                                <div>
                                  <span className="text-gray-300 font-bold group-hover:text-white block">{item.title}</span>
                                  <span className="text-[8.5px] text-gray-500 block truncate">{item.subtitle}</span>
                                </div>
                                <span className="text-[8.5px] px-1 py-0.5 rounded border border-gray-800 text-gray-500 group-hover:border-cyan-500/30 group-hover:text-cyan-400 font-bold uppercase tracking-wide font-mono">
                                  Inspect
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <div className="text-gray-600 text-center py-4">
                      {isSearching ? "Searching platform index..." : "No matching indicators, assets, or cases found."}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs font-semibold font-mono">
            <span className="text-gray-500 font-mono">UTC TIME: {utcTime || "00:00:00"}</span>
            {telemetryStatus === "connected" && (
              <span className="flex items-center gap-1.5 text-green-400 bg-green-950/20 border border-green-500/20 px-2 py-0.5 rounded text-[10px] tracking-wider uppercase font-bold">
                <span className="w-2 h-2 rounded-full bg-[#00ff66] animate-pulse shadow-[0_0_8px_#00ff66]"></span> SYSTEM OK
              </span>
            )}
            {(telemetryStatus === "connecting" || telemetryStatus === "reconnecting") && (
              <span className="flex items-center gap-1.5 text-amber-400 bg-amber-950/20 border border-amber-500/20 px-2 py-0.5 rounded text-[10px] tracking-wider uppercase font-bold animate-pulse">
                <span className="w-2 h-2 rounded-full bg-[#ffb300] animate-pulse shadow-[0_0_8px_#ffb300]"></span> SYNCING
              </span>
            )}
            {telemetryStatus === "polling" && (
              <span className="flex items-center gap-1.5 text-cyan-400 bg-cyan-950/20 border border-cyan-500/20 px-2 py-0.5 rounded text-[10px] tracking-wider uppercase font-bold">
                <span className="w-2 h-2 rounded-full bg-[#00e5ff] animate-pulse shadow-[0_0_8px_#00e5ff]"></span> HTTP FALLBACK
              </span>
            )}
            {telemetryStatus === "disconnected" && (
              <span className="flex items-center gap-1.5 text-red-400 bg-red-950/20 border border-red-500/20 px-2 py-0.5 rounded text-[10px] tracking-wider uppercase font-bold">
                <span className="w-2 h-2 rounded-full bg-[#ff3333] animate-pulse shadow-[0_0_8px_#ff3333]"></span> OFFLINE
              </span>
            )}
          </div>
        </header>

        {/* Viewport container */}
        <main 
          className="flex-1 min-h-0 p-8 overflow-y-auto relative bg-transparent z-10 transition-transform duration-300 ease-out"
          style={{
            transform: `translate3d(${parallaxOffset.x}px, ${parallaxOffset.y}px, 0)`
          }}
        >
          <div className="relative z-10">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
