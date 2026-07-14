import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { SvgBarChart } from "../components/charts/SvgBarChart";
import { SvgLineChart } from "../components/charts/SvgLineChart";
import { SvgDonutChart } from "../components/charts/SvgDonutChart";
import { Award, TrendingUp, Compass, Activity, Download, Info } from "lucide-react";

interface MitreTechnique {
  tactic: string;
  technique: string;
  status: "Covered" | "Partially Covered" | "Not Covered";
  rules: Array<{ id: number; name: string; status: string; severity: string }>;
}

interface ExecutiveMetrics {
  generated_at: string;
  kpis: {
    open_investigations: number;
    critical_alerts_24h: number;
    detection_coverage: number;
    mtti_hours: number;
    mttr_hours: number;
    ai_confidence_average: number;
  };
  posture: {
    overall_risk_score: number;
    posture_label: string;
    threat_trend: string;
    analyst_workload: number;
    rule_health_average: number;
  };
  mitre_coverage: MitreTechnique[];
  trends: {
    daily_alerts: Array<{ date: string; alerts: number }>;
    weekly_trends: Array<{ week: string; alerts: number }>;
    top_attack_vectors: Array<{ label: string; value: number }>;
    severity_distribution: Array<{ label: string; value: number }>;
    top_affected_countries: Array<{ label: string; value: number }>;
    top_affected_assets: Array<{ label: string; value: number }>;
  };
  soc_performance: {
    average_response_time_minutes: number;
    average_investigation_duration_hours: number;
    case_backlog: number;
    detection_latency_seconds: number;
    false_positive_rate: number;
    analyst_productivity: number;
  };
  simulations_executed: number;
  average_simulation_success_rate: number;
  playbooks_executed: number;
  automation_coverage_pct: number;
  analyst_hours_saved: number;
  workflow_success_rate: number;
  correlated_incidents: number;
  intelligence_confidence_score: number;
  campaign_coverage_pct: number;
  top_adversary_technique: string;
  ai_insights?: {
    summary: string;
    major_incidents: string[];
    emerging_patterns: string[];
    coverage_gaps: string[];
    recommended_priorities: string[];
    strategic_observations: string[];
  };
}

export const ExecutiveDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<ExecutiveMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMitreIdx, setSelectedMitreIdx] = useState<number>(0);
  const [downloading, setDownloading] = useState(false);

  const fetchMetrics = async () => {
    try {
      const data = await api.getExecutiveMetrics();
      setMetrics(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to update executive metrics.");
    }
  };

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await fetchMetrics();
      setLoading(false);
    };
    init();

    const interval = setInterval(fetchMetrics, 45000);
    return () => clearInterval(interval);
  }, []);

  const downloadPdf = async () => {
    setDownloading(true);
    try {
      const token = localStorage.getItem("auth_token");
      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const res = await fetch(api.getReportDownloadUrl(), { headers });
      if (!res.ok) throw new Error("PDF report generation failed.");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `DcoY-Executive-Report-${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err: any) {
      alert(err.message || "Failed to download PDF report.");
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-amber-500 font-mono text-xs">
        <Activity className="w-8 h-8 animate-spin mb-2" />
        COMPILING OPERATIONAL INTELLIGENCE METRICS...
      </div>
    );
  }

  const kpis = metrics?.kpis || {
    open_investigations: 0,
    critical_alerts_24h: 0,
    detection_coverage: 0,
    mtti_hours: 0,
    mttr_hours: 0,
    ai_confidence_average: 0
  };

  const posture = metrics?.posture || {
    overall_risk_score: 50,
    posture_label: "Guarded",
    threat_trend: "Stable",
    analyst_workload: 0,
    rule_health_average: 0
  };

  const selectedMitre = metrics?.mitre_coverage?.[selectedMitreIdx] || null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-[#202020]/40 pb-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Award className="w-6 h-6 text-amber-500" />
            Executive Intelligence Command
          </h1>
          <p className="text-sm text-gray-400">Operational posture, response efficiency KPIs, and defensive coverage maps</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={downloadPdf}
            disabled={downloading}
            className="px-3.5 py-1.5 bg-amber-500 hover:bg-amber-600 disabled:bg-gray-800 text-black font-bold text-xs uppercase rounded flex items-center gap-1.5 transition-all shadow-[0_0_10px_rgba(245,158,11,0.15)]"
          >
            <Download className="w-3.5 h-3.5" />
            {downloading ? "Exporting PDF..." : "Export Report PDF"}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-950/20 border border-red-500/50 rounded-md text-red-400 text-xs font-mono">
          [ALERT] {error}
        </div>
      )}

      {/* KPI Row (Six columns) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[
          ["Open Cases", kpis.open_investigations, "Active incidents", "border-amber-500/20 text-amber-500"],
          ["Critical Alerts (24h)", kpis.critical_alerts_24h, "Incoming threats", "border-red-500/20 text-red-500"],
          ["Detection Coverage", `${kpis.detection_coverage}%`, "MITRE Techniques", "border-green-500/20 text-green-400"],
          ["MTTI (Investigate)", `${kpis.mtti_hours}h`, "Avg triage latency", "border-cyan-500/20 text-cyan-400"],
          ["MTTR (Resolution)", `${kpis.mttr_hours}h`, "Mean mitigation time", "border-purple-500/20 text-purple-400"],
          ["AI Confidence Avg", `${kpis.ai_confidence_average}%`, "Evidence verification", "border-cyan-500/20 text-cyan-400"]
        ].map(([label, val, sub, borderClass]) => (
          <div key={label} className={`faceted-panel p-4 bg-[#0a0f18]/80 border text-center font-mono ${borderClass}`}>
            <span className="text-[9px] uppercase tracking-wider text-gray-500 block mb-1">{label}</span>
            <span className="text-2xl font-black block">{val}</span>
            <span className="text-[8px] text-gray-500 mt-1 block uppercase">{sub}</span>
          </div>
        ))}
      </div>

      {/* Posture & Executive Trend Summary */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        
        {/* SVG Circular Posture Gauge Card */}
        <div className="faceted-panel p-5 bg-[#0a0f18]/80 flex flex-col items-center justify-between text-center relative overflow-hidden">
          <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400/80 mb-2 w-full text-left">
            Security Posture
          </h2>
          <div className="relative w-36 h-36 flex items-center justify-center">
            {/* Draw a dynamic circular SVG gauge */}
            <svg width="120" height="120" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="40" fill="none" className="stroke-gray-900" strokeWidth="6" />
              <circle 
                cx="50" cy="50" r="40" 
                fill="none" 
                stroke={posture.overall_risk_score >= 70 ? "#ef4444" : (posture.overall_risk_score >= 40 ? "#f59e0b" : "#10b981")} 
                strokeWidth="6" 
                strokeDasharray={`${(posture.overall_risk_score / 100) * 251.2} 251.2`}
                className="transition-all duration-500 transform -rotate-90 origin-center"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center font-mono">
              <span className="text-2xl font-black text-white">{posture.overall_risk_score}%</span>
              <span className="text-[8px] text-gray-500 uppercase tracking-widest">Risk Score</span>
            </div>
          </div>
          <div className="mt-3 font-mono text-xs w-full text-left bg-[#050b14]/50 border border-gray-900 rounded p-2">
            <div className="flex justify-between py-1 text-gray-400 border-b border-gray-900">
              <span>Threat Level</span>
              <span className={`font-bold ${
                posture.posture_label === "Elevated" ? "text-red-400" : (posture.posture_label === "Guarded" ? "text-amber-400" : "text-green-400")
              }`}>{posture.posture_label}</span>
            </div>
            <div className="flex justify-between py-1 text-gray-400 border-b border-gray-900">
              <span>Alert Trend</span>
              <span className="text-white">{posture.threat_trend}</span>
            </div>
            <div className="flex justify-between py-1 text-gray-400">
              <span>Rule Health</span>
              <span className="text-white">{posture.rule_health_average}%</span>
            </div>
          </div>
        </div>

        {/* Weekly Trend Line Chart */}
        <div className="faceted-panel p-5 bg-[#0a0f18]/80 xl:col-span-2 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 flex justify-between items-center">
            <span>Weekly Threats Trend</span>
            <span className="text-[9px] text-gray-500 font-mono font-normal normal-case">Average over time</span>
          </h2>
          {metrics?.trends?.weekly_trends ? (
            <div className="h-40 flex items-center justify-center">
              <SvgLineChart 
                data={metrics.trends.weekly_trends.map(t => t.alerts)} 
                labels={metrics.trends.weekly_trends.map(t => t.week)} 
                color="#06b6d4" 
                height={140}
              />
            </div>
          ) : (
            <div className="text-center py-10 text-gray-500 text-xs font-mono">No weekly data.</div>
          )}
        </div>

        {/* Daily Alerts Bar Chart */}
        <div className="faceted-panel p-5 bg-[#0a0f18]/80 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2">
            Daily Incident Rate
          </h2>
          {metrics?.trends?.daily_alerts ? (
            <div className="h-40 flex items-center justify-center">
              <SvgBarChart 
                data={metrics.trends.daily_alerts.map(d => ({ label: d.date, value: d.alerts }))} 
                color="#f59e0b" 
                height={140}
              />
            </div>
          ) : (
            <div className="text-center py-10 text-gray-500 text-xs font-mono">No daily logs.</div>
          )}
        </div>

      </div>

      {/* MITRE ATT&CK Matrix Grid & Drilldown */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* Tactics Grid Matrix (2/3 width) */}
        <div className="faceted-panel p-5 bg-[#0a0f18]/80 xl:col-span-2 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2">
            MITRE ATT&CK Enterprise Coverage
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-h-[350px] overflow-y-auto pr-1">
            {metrics?.mitre_coverage?.map((item, idx) => {
              const rulesCount = item.rules?.length || 0;
              const isSelected = selectedMitreIdx === idx;
              
              let statusBorder = "border-gray-800";
              let statusText = "text-gray-500";
              if (item.status === "Covered") {
                statusBorder = "border-green-500/20";
                statusText = "text-green-400";
              } else if (item.status === "Partially Covered") {
                statusBorder = "border-amber-500/20";
                statusText = "text-amber-500";
              }

              return (
                <div 
                  key={idx}
                  onClick={() => setSelectedMitreIdx(idx)}
                  className={`faceted-panel p-3 bg-[#050b14]/50 border transition-all cursor-pointer hover:border-cyan-500/35 flex flex-col justify-between h-28 ${
                    isSelected ? "border-cyan-500/80 shadow-[0_0_10px_rgba(6,182,212,0.15)] bg-cyan-950/5" : statusBorder
                  }`}
                >
                  <div>
                    <span className="text-[7.5px] uppercase font-bold text-gray-500 block truncate">{item.tactic}</span>
                    <span className="text-[11px] font-black text-white mt-1 block leading-tight">{item.technique}</span>
                  </div>
                  <div className="flex justify-between items-center mt-2 pt-2 border-t border-gray-900">
                    <span className={`text-[8.5px] uppercase font-bold ${statusText}`}>{item.status}</span>
                    <span className="text-[9px] font-mono text-gray-500">{rulesCount} rules</span>
                  </div>
                </div>
              );
            }) || (
              <div className="col-span-4 text-center py-10 text-gray-500 text-xs font-mono">No MITRE logs maps.</div>
            )}
          </div>
        </div>

        {/* Selected Technique Drilldown (1/3 width) */}
        <div className="faceted-panel p-5 bg-[#0a0f18]/80 space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="text-xs font-bold uppercase tracking-widest text-amber-500 border-b border-amber-500/15 pb-2 flex items-center gap-1.5">
              <Compass className="w-4 h-4" />
              Coverage Drilldown
            </h2>
            {selectedMitre ? (
              <div className="space-y-4 pt-1 font-mono text-xs">
                <div>
                  <span className="text-gray-500 text-[8.5px] block uppercase">MITRE Tactic</span>
                  <span className="text-white font-bold">{selectedMitre.tactic}</span>
                </div>
                <div>
                  <span className="text-gray-500 text-[8.5px] block uppercase">Attack Technique</span>
                  <span className="text-white font-bold text-cyan-400">{selectedMitre.technique}</span>
                </div>
                
                <div>
                  <span className="text-gray-500 text-[8.5px] block uppercase mb-2">Detection Controls ({selectedMitre.rules?.length || 0})</span>
                  {selectedMitre.rules && selectedMitre.rules.length > 0 ? (
                    <div className="max-h-[160px] overflow-y-auto space-y-2 border border-gray-900 rounded p-2 bg-[#050b14]">
                      {selectedMitre.rules.map(rule => (
                        <div key={rule.id} className="flex justify-between items-center border-b border-gray-900 pb-1.5 last:border-b-0 text-[10px]">
                          <div>
                            <span className="text-gray-300 font-bold block">{rule.name}</span>
                            <span className="text-[8px] text-gray-500">ID: {rule.id}</span>
                          </div>
                          <span className={`text-[8.5px] px-1 py-0.5 rounded font-black uppercase inline-block border ${
                            rule.severity === "High" ? "bg-red-500/10 border-red-500/30 text-red-500" : "bg-amber-500/10 border-amber-500/30 text-amber-500"
                          }`}>
                            {rule.severity}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-6 text-gray-600 text-[10px] border border-dashed border-gray-800 rounded bg-[#050b14]">
                      No custom detection controls mapping this technique.
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-10 text-gray-500 text-xs">Select a technique to inspect detection coverage.</div>
            )}
          </div>
          
          <div className="border-t border-cyan-500/10 pt-3 flex items-center gap-1.5 text-[9px] text-gray-500 font-mono">
            <Info className="w-3.5 h-3.5 text-cyan-500 flex-shrink-0" />
            <span>Select techniques to view their detection rules.</span>
          </div>
        </div>

      </div>

      {/* Downside: Distribution Metrics & AI Posture Summaries */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        
        {/* Severity Distribution Donut */}
        <div className="faceted-panel p-5 bg-[#0a0f18]/80 text-center flex flex-col justify-between">
          <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 text-left w-full">
            Threat Severity
          </h2>
          <div className="h-32 flex items-center justify-center">
            {metrics?.trends?.severity_distribution ? (
              <SvgDonutChart 
                data={metrics.trends.severity_distribution} 
                colors={["#ef4444", "#f59e0b", "#10b981"]}
                size={110}
              />
            ) : (
              <span className="text-gray-500 font-mono text-xs">No distribution.</span>
            )}
          </div>
          <span className="text-[8.5px] uppercase font-mono text-gray-500">Breakdown of ingested alerts</span>
        </div>

        {/* Top Target Vectors */}
        <div className="faceted-panel p-5 bg-[#0a0f18]/80 text-center flex flex-col justify-between">
          <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 text-left w-full">
            Top Attack Vectors
          </h2>
          <div className="h-32 flex items-center justify-center">
            {metrics?.trends?.top_attack_vectors ? (
              <SvgDonutChart 
                data={metrics.trends.top_attack_vectors} 
                colors={["#a855f7", "#3b82f6", "#06b6d4"]}
                size={110}
              />
            ) : (
              <span className="text-gray-500 font-mono text-xs">No vectors.</span>
            )}
          </div>
          <span className="text-[8.5px] uppercase font-mono text-gray-500">Top attack methods detected</span>
        </div>

        {/* Affected Assets & Countries */}
        <div className="faceted-panel p-5 bg-[#0a0f18]/80 text-center flex flex-col justify-between">
          <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 text-left w-full">
            Top Mapped Targets
          </h2>
          <div className="h-32 flex items-center justify-center">
            {metrics?.trends?.top_affected_assets ? (
              <SvgDonutChart 
                data={metrics.trends.top_affected_assets} 
                colors={["#10b981", "#3b82f6", "#f59e0b"]}
                size={110}
              />
            ) : (
              <span className="text-gray-500 font-mono text-xs">No asset data.</span>
            )}
          </div>
          <span className="text-[8.5px] uppercase font-mono text-gray-500">Most targeted hosts</span>
        </div>

        {/* SOC Performance metrics list */}
        <div className="faceted-panel p-5 bg-[#0a0f18]/80 space-y-3 font-mono text-xs">
          <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2">
            SOC Response Metrics
          </h2>
          <div className="space-y-2">
            {[
              ["Analyst Workload", `${posture.analyst_workload} cases`, "Avg queue per analyst"],
              ["Avg Response Time", `${metrics?.soc_performance?.average_response_time_minutes ?? 0} mins`, "From ingestion to action"],
              ["Avg Investigation", `${metrics?.soc_performance?.average_investigation_duration_hours ?? 0} hrs`, "Case resolution lifetime"],
              ["Rule Health Avg", `${posture.rule_health_average}%`, "Ready signature coverage"]
            ].map(([lbl, val, desc]) => (
              <div key={lbl} className="flex justify-between items-center border-b border-gray-900 pb-1.5 last:border-b-0">
                <div>
                  <span className="text-gray-300 font-bold block">{lbl}</span>
                  <span className="text-[8px] text-gray-500 uppercase">{desc}</span>
                </div>
                <span className="text-cyan-400 font-bold text-sm">{val}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* AI Posture Summaries */}
      {metrics?.ai_insights && (
        <div className="faceted-panel p-5 bg-cyan-950/5 border border-cyan-500/15 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400 flex items-center gap-1.5 border-b border-cyan-500/15 pb-2">
            <TrendingUp className="w-4 h-4" />
            AI Gen-Copilot Posture Summary
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs leading-relaxed">
            <div className="space-y-2 md:col-span-2">
              <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block">Strategic Executive Analysis</span>
              <p className="text-gray-300 font-mono whitespace-pre-wrap">{metrics.ai_insights.summary}</p>
            </div>
            
            <div className="space-y-3 font-mono bg-[#050b14]/90 p-4 border border-gray-800 rounded">
              <div>
                <span className="text-[10px] text-amber-500 font-bold uppercase tracking-wider block mb-1">Response Plan Priorities</span>
                <ul className="list-disc pl-4 space-y-1.5 text-gray-300 text-[11px]">
                  {metrics.ai_insights.recommended_priorities?.map((p, idx) => (
                    <li key={idx}>{p}</li>
                  ))}
                </ul>
              </div>
              <div>
                <span className="text-[10px] text-red-400 font-bold uppercase tracking-wider block mb-1">Defense Gaps</span>
                <ul className="list-disc pl-4 space-y-1.5 text-gray-300 text-[11px]">
                  {metrics.ai_insights.coverage_gaps?.map((cg, idx) => (
                    <li key={idx}>{cg}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
export default ExecutiveDashboard;
