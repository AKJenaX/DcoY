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
      <div className="min-h-screen bg-[#0a0b0d] flex items-center justify-center p-6 relative overflow-hidden">
        {/* Three.js/WebGL Hexagonal Drift Background */}
        <div className="absolute inset-0 z-0">
          <Login3DBackground />
        </div>

        {toastMessage && (
          <div className="fixed top-4 right-4 z-50 p-4 bg-amber-950/90 border border-amber-500 text-amber-300 font-mono text-xs rounded shadow-[0_0_20px_rgba(245,166,35,0.2)] animate-pulse flex items-center gap-2">
            <span className="w-2 h-2 bg-amber-500 rounded-full animate-ping"></span>
            {toastMessage}
          </div>
        )}

        <div className="z-10 grid w-full max-w-5xl grid-cols-1 gap-5 lg:grid-cols-[440px_minmax(0,1fr)] items-stretch">
          <div className="faceted-panel p-8 bg-[#111827]/88 backdrop-blur-lg space-y-6 shadow-[0_0_42px_rgba(245,166,35,0.10)]">
            <div className="text-center space-y-2">
              <div className="inline-flex p-3 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-500 mb-2">
                <Shield className="w-8 h-8 animate-pulse" />
              </div>
              <h1 className="text-xl font-bold tracking-tight text-white font-mono uppercase">Operator Security Portal</h1>
              <p className="text-xs text-gray-400">DcoY Cyber Defense Console Authentication</p>
            </div>

            {authError && (
              <div className="p-3 bg-red-950/20 border border-red-500/20 text-red-400 text-xs rounded">
                {authError}
              </div>
            )}

            {authSuccess && (
              <div className="p-3 bg-green-950/20 border border-green-500/20 text-green-400 text-xs rounded">
                {authSuccess}
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] text-gray-400 uppercase tracking-widest">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-[#0a0b0d] border border-gray-800 rounded px-3 py-2 text-sm text-white outline-none focus:border-amber-500"
                  required
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-gray-400 uppercase tracking-widest">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[#0a0b0d] border border-gray-800 rounded px-3 py-2 text-sm text-white outline-none focus:border-amber-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2">
                <button
                  type="submit"
                  className="py-2 bg-amber-500 hover:bg-amber-600 font-bold text-xs uppercase text-black rounded transition-all shadow-[0_0_15px_rgba(245,166,35,0.2)]"
                >
                  Log In
                </button>
                <button
                  type="button"
                  onClick={handleRegister}
                  className="py-2 bg-[#0a0b0d] hover:bg-gray-900 border border-gray-800 text-white font-bold text-xs uppercase rounded transition-all"
                >
                  Register
                </button>
              </div>
            </form>
          </div>

          <div className="faceted-panel hidden lg:flex p-6 bg-[#0b1118]/78 backdrop-blur-md border-cyan-500/10 flex-col justify-between overflow-hidden">
            <div className="space-y-4">
              <div>
                <span className="text-[10px] text-cyan-400 font-bold uppercase tracking-[0.24em]">Hive Defense</span>
                <h2 className="mt-2 text-3xl font-black text-white font-mono leading-tight">Adaptive decoy mesh online</h2>
                <p className="mt-2 text-xs text-gray-400 max-w-md">
                  Active defense fabric is standing by with deception telemetry, graph correlation, and response automation.
                </p>
              </div>

              <div className="grid grid-cols-3 gap-3">
                {[
                  ["18", "Edges watched", "text-cyan-400"],
                  ["06", "Decoys armed", "text-amber-500"],
                  ["24s", "Avg response", "text-green-400"],
                ].map(([value, label, color]) => (
                  <div key={label} className="bg-[#050b14]/70 border border-gray-800/80 rounded p-3">
                    <div className={`text-xl font-black font-mono ${color}`}>{value}</div>
                    <div className="mt-1 text-[9px] uppercase tracking-wider text-gray-500">{label}</div>
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
                <div key={text} className="flex items-center gap-3 border border-gray-800/70 bg-[#050b14]/60 rounded px-3 py-2 font-mono text-[10px]">
                  <Clock className="w-3.5 h-3.5 text-amber-500" />
                  <span className="text-gray-500">{time}</span>
                  <span className="text-gray-300">{text}</span>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between border-t border-gray-800 pt-4 text-[10px] font-bold uppercase tracking-widest">
              <span className="flex items-center gap-2 text-green-400">
                <Radio className="w-3.5 h-3.5" /> Mesh stable
              </span>
              <span className="text-gray-500">SOC link encrypted</span>
            </div>
          </div>
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
    <div className="min-h-screen bg-[#0a0b0d] flex text-gray-300">
      <aside className="h-screen sticky top-0 w-64 bg-[#0a0b0d] border-r border-[#202020]/40 flex flex-col justify-between p-5 z-20 sidebar-honeycomb-bg">
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
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-colors group ${
                  activePage === "overview"
                    ? "text-cyan-400 bg-cyan-950/15"
                    : "text-gray-400 hover:text-white hover:bg-gray-850/30"
                }`}
              >
                <NavHexagon active={activePage === "overview"} color="cyan" size={28}>
                  <Activity className="w-4 h-4" />
                </NavHexagon>
                <span className="font-mono tracking-wide">Command Overview</span>
              </button>

              <button
                onClick={() => setActivePage("hivemap")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-colors group ${
                  activePage === "hivemap"
                    ? "text-cyan-400 bg-cyan-950/15"
                    : "text-gray-400 hover:text-white hover:bg-gray-850/30"
                }`}
              >
                <NavHexagon active={activePage === "hivemap"} color="cyan" size={28}>
                  <Compass className="w-4 h-4" />
                </NavHexagon>
                <span className="font-mono tracking-wide">Hive Map</span>
              </button>

              <button
                onClick={() => setActivePage("deception")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-colors group ${
                  activePage === "deception"
                    ? "text-cyan-400 bg-cyan-950/15"
                    : "text-gray-400 hover:text-white hover:bg-gray-850/30"
                }`}
              >
                <NavHexagon active={activePage === "deception"} color="cyan" size={28}>
                  <Bug className="w-4 h-4" />
                </NavHexagon>
                <span className="font-mono tracking-wide">Deception Grid</span>
              </button>

              <button
                onClick={() => setActivePage("intel")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-colors group ${
                  activePage === "intel"
                    ? "text-cyan-400 bg-cyan-950/15"
                    : "text-gray-400 hover:text-white hover:bg-gray-850/30"
                }`}
              >
                <NavHexagon active={activePage === "intel"} color="cyan" size={28}>
                  <Globe className="w-4 h-4" />
                </NavHexagon>
                <span className="font-mono tracking-wide">Threat Intel</span>
              </button>

              <button
                onClick={() => setActivePage("geolocation")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-colors group ${
                  activePage === "geolocation"
                    ? "text-cyan-400 bg-cyan-950/15"
                    : "text-gray-400 hover:text-white hover:bg-gray-850/30"
                }`}
              >
                <NavHexagon active={activePage === "geolocation"} color="cyan" size={28}>
                  <MapPin className="w-4 h-4" />
                </NavHexagon>
                <span className="font-mono tracking-wide">Live Geolocation</span>
              </button>

              <button
                onClick={() => setActivePage("simulation")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-colors group ${
                  activePage === "simulation"
                    ? "text-cyan-400 bg-cyan-950/15"
                    : "text-gray-400 hover:text-white hover:bg-gray-850/30"
                }`}
              >
                <NavHexagon active={activePage === "simulation"} color="cyan" size={28}>
                  <Target className="w-4 h-4" />
                </NavHexagon>
                <span className="font-mono tracking-wide">Attack Simulation</span>
              </button>

              <button
                onClick={() => setActivePage("health")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-colors group ${
                  activePage === "health"
                    ? "text-cyan-400 bg-cyan-950/15"
                    : "text-gray-400 hover:text-white hover:bg-gray-850/30"
                }`}
              >
                <NavHexagon active={activePage === "health"} color="cyan" size={28}>
                  <Activity className="w-4 h-4" />
                </NavHexagon>
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
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-colors group ${
                  activePage === "investigations"
                    ? "text-amber-400 bg-amber-950/15"
                    : "text-gray-400 hover:text-white hover:bg-gray-850/30"
                }`}
              >
                <NavHexagon active={activePage === "investigations"} color="amber" size={28}>
                  <ClipboardList className="w-4 h-4" />
                </NavHexagon>
                <span className="font-mono tracking-wide">Investigations</span>
              </button>

              <button
                onClick={() => setActivePage("rules")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-colors group ${
                  activePage === "rules"
                    ? "text-amber-400 bg-amber-950/15"
                    : "text-gray-400 hover:text-white hover:bg-gray-850/30"
                }`}
              >
                <NavHexagon active={activePage === "rules"} color="amber" size={28}>
                  <Sliders className="w-4 h-4" />
                </NavHexagon>
                <span className="font-mono tracking-wide">Detection Rules</span>
              </button>
            </div>

            <div className="space-y-1.5">
              <span className="text-[10px] text-gray-500 font-bold tracking-widest uppercase flex items-center gap-1.5 px-2 mb-2">
                <span className="group-label-tick text-violet-400"></span>
                Executive
              </span>

              <button
                onClick={() => setActivePage("executive")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-colors group ${
                  activePage === "executive"
                    ? "text-violet-400 bg-violet-950/15"
                    : "text-gray-400 hover:text-white hover:bg-gray-850/30"
                }`}
              >
                <NavHexagon active={activePage === "executive"} color="violet" size={28}>
                  <Award className="w-4 h-4" />
                </NavHexagon>
                <span className="font-mono tracking-wide">Executive Dash</span>
              </button>

              <button
                onClick={() => setActivePage("report")}
                className={`w-full flex items-center gap-3 px-2 py-1 text-xs font-semibold rounded-md transition-colors group ${
                  activePage === "report"
                    ? "text-violet-400 bg-violet-950/15"
                    : "text-gray-400 hover:text-white hover:bg-gray-850/30"
                }`}
              >
                <NavHexagon active={activePage === "report"} color="violet" size={28}>
                  <FileText className="w-4 h-4" />
                </NavHexagon>
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
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Sticky Top Header Navigation */}
        <header className="sticky top-0 bg-[#0a0b0d]/85 backdrop-filter backdrop-blur-md border-b border-[#202020]/40 px-8 py-3 flex justify-between items-center z-10">
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

          <div className="flex items-center gap-4 text-xs font-semibold">
            <span className="text-gray-500 font-mono">UTC TIME: {utcTime || "00:00:00"}</span>
            {telemetryStatus === "connected" && (
              <span className="flex items-center gap-1 text-green-400 bg-green-950/20 border border-green-500/20 px-2 py-0.5 rounded text-[10px] tracking-wider uppercase font-bold">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-ping"></span> SYSTEM OK
              </span>
            )}
            {(telemetryStatus === "connecting" || telemetryStatus === "reconnecting") && (
              <span className="flex items-center gap-1 text-amber-400 bg-amber-950/20 border border-amber-500/20 px-2 py-0.5 rounded text-[10px] tracking-wider uppercase font-bold animate-pulse">
                <span className="w-1.5 h-1.5 bg-amber-500 rounded-full"></span> SYNCING...
              </span>
            )}
            {telemetryStatus === "polling" && (
              <span className="flex items-center gap-1 text-cyan-400 bg-cyan-950/20 border border-cyan-500/20 px-2 py-0.5 rounded text-[10px] tracking-wider uppercase font-bold">
                <span className="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-bounce"></span> HTTP FALLBACK
              </span>
            )}
            {telemetryStatus === "disconnected" && (
              <span className="flex items-center gap-1 text-red-400 bg-red-950/20 border border-red-500/20 px-2 py-0.5 rounded text-[10px] tracking-wider uppercase font-bold">
                <span className="w-1.5 h-1.5 bg-red-500 rounded-full"></span> OFFLINE
              </span>
            )}
          </div>
        </header>

        {/* Viewport container */}
        <main className="flex-1 p-8 overflow-y-auto">
          {renderContent()}
        </main>
      </div>
    </div>
  );
};

export default App;
