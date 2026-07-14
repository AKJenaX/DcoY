import React, { useState } from "react";
import { api } from "../services/api";
import { RefreshCw, Download, CheckCircle, AlertTriangle } from "lucide-react";
import { GlassPanel } from "../components/GlassPanel";

export const PdfReport: React.FC = () => {
  const [compiling, setCompiling] = useState(false);
  const [reportBlob, setReportBlob] = useState<Blob | null>(null);
  const [error, setError] = useState("");

  const handleCompile = async () => {
    setCompiling(true);
    setReportBlob(null);
    setError("");
    try {
      const blob = await api.compileReport();
      setReportBlob(blob);
    } catch (err: any) {
      setError(err.message || "Failed to compile executive defense report. Ensure backend is running.");
    } finally {
      setCompiling(false);
    }
  };

  const handleDownload = () => {
    if (!reportBlob) return;
    const url = window.URL.createObjectURL(reportBlob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `DcoY_Executive_Security_Report_${new Date().getFullYear()}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.parentNode?.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center pb-4 page-header-glass">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono text-amber-500 uppercase tracking-widest mb-1">
            <span className="w-2 h-2 rounded-full bg-[#ffb300] animate-pulse shadow-[0_0_8px_#ffb300]"></span>
            CONSOLE.STATUS // AUDIT_COMPILER_ONLINE
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white font-mono uppercase">Executive Reporting</h1>
          <p className="text-xs text-gray-400">Generate and export official SOC and CISO performance audits</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compiler Dashboard Panel */}
        <GlassPanel borderColor="amber" className="p-5 space-y-4">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-amber-500 border-b border-amber-500/15 pb-2 uppercase">
            <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,166,35,0.6)]"></span>
            COMPILER.HUD // SECURITY AUDIT LEDGER
          </div>
          <p className="text-xs text-gray-400 leading-relaxed font-mono">
            The reporting engine aggregates ML anomalies, deception hits, honeypot deflections, and active cases to generate an official cryptographic audit ledger. Export options include PDF, Markdown, and JSON.
          </p>

          <div className="space-y-3 pt-2">
            <button
              onClick={handleCompile}
              disabled={compiling}
              className="w-full py-2.5 bg-amber-500 hover:bg-amber-600 disabled:bg-gray-800 font-bold text-xs uppercase text-black disabled:text-gray-500 rounded transition-all flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(245,166,35,0.25)] font-mono"
            >
              {compiling ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" /> COMPILING PDF LEDGER...
                </>
              ) : (
                "COMPILE PDF SECURITY REPORT"
              )}
            </button>

            {reportBlob && (
              <button
                onClick={handleDownload}
                className="w-full py-2.5 bg-green-500 hover:bg-green-600 font-bold text-xs uppercase text-black rounded transition-all flex items-center justify-center gap-2 font-mono"
              >
                <Download className="w-4 h-4" /> DOWNLOAD PDF REPORT
              </button>
            )}
          </div>

          {error && (
            <div className="p-3 bg-red-950/20 border border-red-500/20 text-red-400 text-xs rounded flex items-center gap-2 font-mono">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {reportBlob && (
            <div className="p-3 bg-green-950/20 border border-green-500/20 text-green-400 text-xs rounded flex items-center gap-2 font-mono">
              <CheckCircle className="w-4 h-4 flex-shrink-0" />
              <span>Executive Security PDF compiled successfully! Ready for download.</span>
            </div>
          )}
        </GlassPanel>

        {/* Report Preview Outline Panel */}
        <GlassPanel borderColor="cyan" className="p-5 space-y-4">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 border-b border-cyan-500/15 pb-2 uppercase">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
            CONTENTS.OUTLINE // REPORT CHAPTERS
          </div>
          <div className="space-y-3 text-xs text-gray-300">
            <div className="flex gap-2">
              <span className="text-cyan-400 font-bold font-mono">1.0</span>
              <div>
                <div className="font-semibold text-white font-mono">Executive Posture Summary</div>
                <p className="text-[10px] text-gray-400 font-sans">High-level threat ratings, ML classification indexes, and active decoys counts.</p>
              </div>
            </div>
            <div className="flex gap-2">
              <span className="text-cyan-400 font-bold font-mono">2.0</span>
              <div>
                <div className="font-semibold text-white font-mono">ML Anomaly Detection Sweep</div>
                <p className="text-[10px] text-gray-400 font-sans">Isolation Forest clusters, risk distribution curves, and threat classification.</p>
              </div>
            </div>
            <div className="flex gap-2">
              <span className="text-cyan-400 font-bold font-mono">3.0</span>
              <div>
                <div className="font-semibold text-white font-mono">Active Deception Engagements</div>
                <p className="text-[10px] text-gray-400 font-sans">Decoy honeypot absorption results and deflected adversary traffic logs.</p>
              </div>
            </div>
            <div className="flex gap-2">
              <span className="text-cyan-400 font-bold font-mono">4.0</span>
              <div>
                <div className="font-semibold text-white font-mono">SOAR Containment Metrics</div>
                <p className="text-[10px] text-gray-400 font-sans">Response latencies, automated firewall blocks, and remediation ROI metrics.</p>
              </div>
            </div>
          </div>
        </GlassPanel>
      </div>
    </div>
  );
};
