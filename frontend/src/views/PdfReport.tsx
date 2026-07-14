import React, { useState } from "react";
import { api } from "../services/api";
import { FileText, RefreshCw, Download, CheckCircle, AlertTriangle } from "lucide-react";

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
      <div className="flex justify-between items-center border-b border-[#220 20% 15%] pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Executive Reporting</h1>
          <p className="text-sm text-gray-400">Generate and export official SOC and CISO performance audits</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compiler Dashboard Panel */}
        <div className="faceted-panel p-5 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-widest text-amber-500 flex items-center gap-1.5">
            <FileText className="w-4 h-4" /> Report compiler dashboard
          </h2>
          <p className="text-xs text-gray-400 leading-relaxed">
            The reporting engine aggregates ML anomalies, deception hits, honeypot deflections, and active cases to generate an official cryptographic audit ledger. Export options include PDF, Markdown, and JSON.
          </p>

          <div className="space-y-3 pt-2">
            <button
              onClick={handleCompile}
              disabled={compiling}
              className="w-full py-2.5 bg-amber-500 hover:bg-amber-600 disabled:bg-gray-800 font-bold text-xs uppercase text-black disabled:text-gray-500 rounded transition-all flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(245,166,35,0.25)]"
            >
              {compiling ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" /> Compiling PDF Ledger...
                </>
              ) : (
                "Compile PDF Security Report"
              )}
            </button>

            {reportBlob && (
              <button
                onClick={handleDownload}
                className="w-full py-2.5 bg-green-500 hover:bg-green-600 font-bold text-xs uppercase text-black rounded transition-all flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" /> Download PDF Report
              </button>
            )}
          </div>

          {error && (
            <div className="p-3 bg-red-950/20 border border-red-500/20 text-red-400 text-xs rounded flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {reportBlob && (
            <div className="p-3 bg-green-950/20 border border-green-500/20 text-green-400 text-xs rounded flex items-center gap-2">
              <CheckCircle className="w-4 h-4 flex-shrink-0" />
              <span>Executive Security PDF compiled successfully! Ready for download.</span>
            </div>
          )}
        </div>

        {/* Report Preview Outline Panel */}
        <div className="faceted-panel p-5 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400">Report Contents Outline</h2>
          <div className="space-y-3 text-xs text-gray-300">
            <div className="flex gap-2">
              <span className="text-cyan-400 font-bold font-mono">1.0</span>
              <div>
                <div className="font-semibold text-white">Executive Posture Summary</div>
                <p className="text-[10px] text-gray-400">High-level threat ratings, ML classification indexes, and active decoys counts.</p>
              </div>
            </div>
            <div className="flex gap-2">
              <span className="text-cyan-400 font-bold font-mono">2.0</span>
              <div>
                <div className="font-semibold text-white">ML Anomaly Detection Sweep</div>
                <p className="text-[10px] text-gray-400">Isolation Forest clusters, risk distribution curves, and threat classification.</p>
              </div>
            </div>
            <div className="flex gap-2">
              <span className="text-cyan-400 font-bold font-mono">3.0</span>
              <div>
                <div className="font-semibold text-white">Active Deception Engagements</div>
                <p className="text-[10px] text-gray-400">Decoy honeypot absorption results and deflected adversary traffic logs.</p>
              </div>
            </div>
            <div className="flex gap-2">
              <span className="text-cyan-400 font-bold font-mono">4.0</span>
              <div>
                <div className="font-semibold text-white">SOAR Containment Metrics</div>
                <p className="text-[10px] text-gray-400">Response latencies, automated firewall blocks, and remediation ROI metrics.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
