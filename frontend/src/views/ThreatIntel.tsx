import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { Shield, Rss, Globe } from "lucide-react";

interface Indicator {
  id: string;
  ioc: string;
  type: string;
  source: string;
  confidence: number;
  status: string;
}

export const ThreatIntel: React.FC = () => {
  const [indicators, setIndicators] = useState<Indicator[]>([
    {
      id: "IOC-101",
      ioc: "198.51.100.42",
      type: "IPv4 Address",
      source: "Abuse.ch Feodo Tracker",
      confidence: 0.95,
      status: "Active",
    },
    {
      id: "IOC-102",
      ioc: "badmalwaredomain.com",
      type: "Domain",
      source: "AlienVault OTX",
      confidence: 0.88,
      status: "Active",
    },
    {
      id: "IOC-103",
      ioc: "45.132.22.99",
      type: "IPv4 Address",
      source: "Emerging Threats Botnet List",
      confidence: 0.92,
      status: "Active",
    },
    {
      id: "IOC-104",
      ioc: "185.220.101.5",
      type: "IPv4 Address",
      source: "Tor Exit Node Registry",
      confidence: 0.85,
      status: "Monitored",
    },
  ]);

  const intelKpis = {
    confidence_score: 0.95,
    campaign_coverage_pct: 84.5,
    top_adversary_technique: "T1110 (Brute Force)",
  };

  const syncIntelData = async () => {
    try {
      const logs = await api.getDetectLogs();
      const events = logs.events || [];

      // Extract unique IPs matching anomalies to dynamically populate indicators
      const anomalies = events.filter((e: any) => e.is_anomaly && e.ip);
      if (anomalies.length > 0) {
        const uniqueIps = Array.from(new Set(anomalies.map((a: any) => a.ip)));
        const dynamicIndicators = uniqueIps.map((ip: any, idx: number) => ({
          id: `IOC-${201 + idx}`,
          ioc: ip,
          type: "IPv4 Address",
          source: "Dynamic Ingest Stream Anomaly",
          confidence: 0.90,
          status: "Active",
        }));
        setIndicators((prev) => {
          // Merge unique IOCs
          const merged = [...prev];
          dynamicIndicators.forEach((di) => {
            if (!merged.some((m) => m.ioc === di.ioc)) {
              merged.push(di);
            }
          });
          return merged;
        });
      }
    } catch (e) {
      // Keep defaults
    }
  };

  useEffect(() => {
    syncIntelData();
    const interval = setInterval(syncIntelData, 6000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-[#220 20% 15%] pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Threat Intelligence</h1>
          <p className="text-sm text-gray-400">Track Indicators of Compromise (IOCs) and security feed logs</p>
        </div>
      </div>

      {/* KPI Strip */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="faceted-panel p-4 bg-[#111827]/40 flex justify-between items-center">
          <div>
            <div className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Adversary Confidence</div>
            <div className="text-xl font-black text-white mt-1">{(intelKpis.confidence_score * 100).toFixed(0)}%</div>
          </div>
          <Shield className="w-8 h-8 text-cyan-400 opacity-80" />
        </div>

        <div className="faceted-panel p-4 bg-[#111827]/40 flex justify-between items-center">
          <div>
            <div className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Campaign Coverage</div>
            <div className="text-xl font-black text-white mt-1">{intelKpis.campaign_coverage_pct}%</div>
          </div>
          <Rss className="w-8 h-8 text-amber-500 opacity-80" />
        </div>

        <div className="faceted-panel p-4 bg-[#111827]/40 flex justify-between items-center">
          <div>
            <div className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Top Attack Vector</div>
            <div className="text-sm font-black text-white mt-2 truncate w-48">{intelKpis.top_adversary_technique}</div>
          </div>
          <Globe className="w-8 h-8 text-purple-400 opacity-80" />
        </div>
      </div>

      {/* Indicators List */}
      <div className="faceted-panel p-5 space-y-4">
        <h2 className="text-xs font-bold uppercase tracking-widest text-amber-500">Compromise Indicators (IOCs)</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-gray-800 text-gray-400 uppercase text-[10px] tracking-wider">
                <th className="py-2.5 px-3">IOC ID</th>
                <th className="py-2.5 px-3">Indicator Address</th>
                <th className="py-2.5 px-3">IOC Type</th>
                <th className="py-2.5 px-3">Intel Feed Source</th>
                <th className="py-2.5 px-3 text-center">Confidence</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/40">
              {indicators.map((ind) => (
                <tr key={ind.id} className="hover:bg-[#111827]/40 transition-colors">
                  <td className="py-3 px-3">
                    <span className="text-[10px] font-mono font-bold text-cyan-400 bg-cyan-950/30 px-2 py-0.5 rounded border border-cyan-500/20">
                      {ind.id}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono font-bold text-white">{ind.ioc}</td>
                  <td className="py-3 px-3 text-gray-300">{ind.type}</td>
                  <td className="py-3 px-3 text-gray-400">{ind.source}</td>
                  <td className="py-3 px-3 text-center font-mono font-semibold text-amber-400">
                    {(ind.confidence * 100).toFixed(0)}%
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className={`px-2 py-0.5 text-[9px] font-bold uppercase rounded border ${
                        ind.status === "Active"
                          ? "bg-red-500/10 border-red-500/20 text-red-400"
                          : "bg-gray-800 border-gray-700 text-gray-400"
                      }`}
                    >
                      {ind.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
