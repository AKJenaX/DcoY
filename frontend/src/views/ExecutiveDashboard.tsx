import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { SvgBarChart } from "../components/charts/SvgBarChart";
import { SvgLineChart } from "../components/charts/SvgLineChart";
import { SvgDonutChart } from "../components/charts/SvgDonutChart";
import { Download, Activity } from "lucide-react";
import { GlassPanel } from "../components/GlassPanel";

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
    <div className="space-y-8 py-4 px-2 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center pb-3 page-header-glass">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono text-amber-500 uppercase tracking-widest mb-1">
            <span className="w-2 h-2 rounded-full bg-[#ffb300] animate-pulse shadow-[0_0_8px_#ffb300]"></span>
            CONSOLE.STATUS // EXECUTIVE_OVERWATCH_READY
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white font-mono uppercase">Executive Intelligence Command</h1>
          <p className="text-xs text-gray-400">Operational posture, response efficiency KPIs, and defensive coverage maps</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={downloadPdf}
            disabled={downloading}
            className="px-3.5 py-1.5 bg-amber-500 hover:bg-amber-600 disabled:bg-gray-800 text-black font-bold text-xs uppercase rounded flex items-center gap-1.5 transition-all shadow-[0_0_10px_rgba(245,158,11,0.15)] font-mono"
          >
            <Download className="w-3.5 h-3.5" />
            {downloading ? "Exporting PDF..." : "EXPORT REPORT PDF"}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-950/20 border border-red-500/50 rounded-md text-red-400 text-xs font-mono">
          [ALERT] {error}
        </div>
      )}

      {/* KPI Row (Six columns) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
        {[
          ["Open Cases", kpis.open_investigations, "Active incidents"],
          ["Critical Alerts (24h)", kpis.critical_alerts_24h, "Incoming threats"],
          ["Detection Coverage", `${kpis.detection_coverage}%`, "MITRE Techniques"],
          ["MTTI (Investigate)", `${kpis.mtti_hours}h`, "Avg triage latency"],
          ["MTTR (Resolution)", `${kpis.mttr_hours}h`, "Mean mitigation time"],
          ["AI Confidence Avg", `${kpis.ai_confidence_average}%`, "Evidence verification"]
        ].map(([label, val, sub]) => (
          <GlassPanel key={label} borderColor="amber" className="p-6 text-center font-mono hover:border-amber-400/40 transition-all hover:scale-[1.02] shadow-[0_0_15px_rgba(245,158,11,0.03)] bg-[#0a0f18]/60">
            <span className="text-[10px] uppercase tracking-widest text-gray-500 block mb-2">{label}</span>
            <span className="text-4xl font-black block text-amber-400 tracking-tight">{val}</span>
            <span className="text-[8.5px] text-gray-500 mt-2 block uppercase font-sans leading-relaxed">{sub}</span>
          </GlassPanel>
        ))}
      </div>

      {/* Posture & Executive Trend Summary */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        
      {/* Posture & Executive Trend Summary */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        
        {/* SVG Circular Posture Gauge Card */}
        <GlassPanel borderColor="cyan" className="p-5 flex flex-col items-center justify-between text-center relative overflow-hidden">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 uppercase w-full text-left">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
            POSTURE.OVERALL // RISK SUMMARY
          </div>
          <div className="relative w-36 h-36 flex items-center justify-center mt-3">
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
        </GlassPanel>

        {/* Weekly Trend Line Chart */}
        <GlassPanel borderColor="cyan" className="xl:col-span-2 p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-cyan-500/15 pb-2 text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
              TREND.LOG // HISTORICAL DATA
            </div>
            <span className="text-[9px] text-gray-500 font-mono font-normal normal-case">Average over time</span>
          </div>
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
        </GlassPanel>

        {/* Daily Alerts Bar Chart */}
        <GlassPanel borderColor="cyan" className="p-5 space-y-4">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 uppercase">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
            LATENCY.METRICS // RESPONSE KPI
          </div>
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
        </GlassPanel>

      </div>

      {/* MITRE ATT&CK Matrix Grid & Drilldown */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* Tactics Grid Matrix (2/3 width) */}
        <GlassPanel borderColor="cyan" className="xl:col-span-2 p-5 space-y-4">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 uppercase">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
            MITRE.COVERAGE // TACTICS MAPPING
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-h-[350px] overflow-y-auto pr-1 scrollbar-thin">
            {metrics?.mitre_coverage?.map((item, idx) => {
              const rulesCount = item.rules?.length || 0;
              const isSelected = selectedMitreIdx === idx;
              
              let statusText = "text-gray-500";
              if (item.status === "Covered") {
                statusText = "text-green-400";
              } else if (item.status === "Partially Covered") {
                statusText = "text-amber-500";
              }

              return (
                <GlassPanel 
                  key={idx}
                  onClick={() => setSelectedMitreIdx(idx)}
                  borderColor={isSelected ? "cyan" : (item.status === "Covered" ? "cyan" : (item.status === "Partially Covered" ? "amber" : "cyan"))}
                  className={`p-3 cursor-pointer hover:scale-[1.02] flex flex-col justify-between h-28 transition-all bg-[#050b14]/50`}
                >
                  <div>
                    <span className="text-[7.5px] uppercase font-bold text-gray-500 block truncate font-mono">{item.tactic}</span>
                    <span className="text-[11px] font-black text-white mt-1 block leading-tight font-sans">{item.technique}</span>
                  </div>
                  <div className="flex justify-between items-center mt-2 pt-2 border-t border-gray-900 font-mono">
                    <span className={`text-[8.5px] uppercase font-bold ${statusText}`}>{item.status}</span>
                    <span className="text-[9px] text-gray-500">{rulesCount} rules</span>
                  </div>
                </GlassPanel>
              );
            }) || (
              <div className="col-span-4 text-center py-10 text-gray-500 text-xs font-mono">No MITRE logs maps.</div>
            )}
          </div>
        </GlassPanel>

        {/* Selected Technique Drilldown (1/3 width) */}
        <GlassPanel borderColor="amber" className="p-5 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-amber-500 border-b border-amber-500/15 pb-2 uppercase">
              <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,166,35,0.6)]"></span>
              DRILLDOWN.TACTIC // CONTROLS LIST
            </div>
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
        </GlassPanel>
        </div>

      </div>

      {/* Downside: Distribution Metrics & AI Posture Summaries */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        
        {/* Severity Distribution Donut */}
        <GlassPanel borderColor="cyan" className="p-5 text-center flex flex-col justify-between">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 uppercase text-left w-full">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
            STATUS.KPI // THREAT SEVERITY
          </div>
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
        </GlassPanel>

        {/* Top Target Vectors */}
        <GlassPanel borderColor="cyan" className="p-5 text-center flex flex-col justify-between">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 uppercase text-left w-full">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
            STATUS.KPI // ATTACK METHODS
          </div>
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
        </GlassPanel>

        {/* Affected Assets & Countries */}
        <GlassPanel borderColor="cyan" className="p-5 text-center flex flex-col justify-between">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 uppercase text-left w-full">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
            STATUS.KPI // TOP TARGETS
          </div>
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
        </GlassPanel>

        {/* SOC Performance metrics list */}
        <GlassPanel borderColor="cyan" className="p-5 space-y-3 font-mono text-xs">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 uppercase">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
            SOC.PERFORMANCE // RESPONSE METRICS
          </div>
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
        </GlassPanel>

      </div>

      {/* AI Posture Summaries */}
      {metrics?.ai_insights && (
        <GlassPanel borderColor="cyan" className="p-5 space-y-4">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-amber-500 border-b border-amber-500/15 pb-2 uppercase">
            <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,158,11,0.6)]"></span>
            AI.STRATEGY // EXECUTIVE SUGGESTION
          </div>
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
        </GlassPanel>
      )}

    </div>
  );
};
export default ExecutiveDashboard;
