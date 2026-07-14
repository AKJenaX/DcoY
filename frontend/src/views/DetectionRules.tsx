import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { CheckCircle, AlertTriangle } from "lucide-react";
import { GlassPanel } from "../components/GlassPanel";

interface Rule {
  id: number;
  name: string;
  description: string;
  severity: "High" | "Medium" | "Low" | string;
  mitre_technique: string;
  detection_logic: string;
  status: "Enabled" | "Disabled" | string;
}

export const DetectionRules: React.FC = () => {
  const [rules, setRules] = useState<Rule[]>([]);
  const [newRuleName, setNewRuleName] = useState("");
  const [newRuleLogic, setNewRuleLogic] = useState(`{"event_type": "port_scan", "threshold": 5}`);
  const [newRuleSeverity, setNewRuleSeverity] = useState("High");
  const [newRuleMitre, setNewRuleMitre] = useState("T1046");
  const [validationResult, setValidationResult] = useState<any>(null);
  const [validationError, setValidationError] = useState("");
  const [error, setError] = useState("");

  const loadRules = async () => {
    try {
      setError("");
      const data = await api.getDetectionRules();
      setRules(data || []);
    } catch (err: any) {
      setError("Failed to fetch detection rules database.");
    }
  };

  const handleValidate = async () => {
    setValidationResult(null);
    setValidationError("");
    try {
      // Parse logic string
      const parsed = JSON.parse(newRuleLogic);
      const res = await api.validateRule(parsed);
      setValidationResult(res);
    } catch (err: any) {
      setValidationError(err.message || "Invalid JSON syntax inside logic block.");
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRuleName.trim()) return;

    try {
      const parsedLogic = JSON.parse(newRuleLogic);
      const newRule = {
        name: newRuleName,
        description: "Custom rule added via Command Console.",
        severity: newRuleSeverity,
        mitre_technique: newRuleMitre,
        detection_logic: JSON.stringify(parsedLogic),
        status: "Enabled",
      };

      setError("");
      await api.createDetectionRule(newRule);
      setNewRuleName("");
      setNewRuleLogic(`{"event_type": "port_scan", "threshold": 5}`);
      setValidationResult(null);
      await loadRules();
    } catch (err: any) {
      setError(err.message || "Could not save custom detection rule.");
    }
  };

  useEffect(() => {
    loadRules();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center pb-4 page-header-glass">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono text-amber-500 uppercase tracking-widest mb-1">
            <span className="w-2 h-2 rounded-full bg-[#ffb300] animate-pulse shadow-[0_0_8px_#ffb300]"></span>
            CONSOLE.STATUS // RULES_ONLINE
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white font-mono uppercase">Detection Rules</h1>
          <p className="text-xs text-gray-400">Manage operational triggers, query logic blocks, and active signatures</p>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-950/30 border border-red-500/50 rounded-md text-red-400 text-xs font-mono">
          [ALERT] {error}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Rules Table / Ledger list (2/3 width) */}
        <GlassPanel borderColor="amber" className="xl:col-span-2 p-5 space-y-4">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-amber-500 uppercase">
            <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,166,35,0.6)]"></span>
            RULES.ACTIVE // DETECTION POLICY
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400 uppercase text-[10px] tracking-wider font-mono">
                  <th className="py-2.5 px-3">Rule Name</th>
                  <th className="py-2.5 px-3">Mitre Code</th>
                  <th className="py-2.5 px-3 text-center">Severity</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/40 font-mono">
                {rules.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="py-10 text-center text-gray-500 font-sans">
                      No active rules synced from database.
                    </td>
                  </tr>
                ) : (
                  rules.map((rule) => (
                    <tr key={rule.id} className="hover:bg-[#111827]/40 transition-colors">
                      <td className="py-3 px-3">
                        <div className="font-bold text-white font-sans">{rule.name}</div>
                        <div className="text-[10px] text-gray-400 truncate max-w-[280px] font-sans">{rule.description}</div>
                      </td>
                      <td className="py-3 px-3 font-mono font-semibold text-cyan-400">{rule.mitre_technique}</td>
                      <td className="py-3 px-3 text-center">
                        <span
                          className={`px-2 py-0.5 text-[9px] font-bold uppercase rounded border ${
                            rule.severity === "High"
                              ? "bg-red-500/10 border-red-500/20 text-red-400"
                              : rule.severity === "Medium"
                              ? "bg-amber-500/10 border-amber-500/20 text-amber-400"
                              : "bg-green-500/10 border-green-500/20 text-green-400"
                          }`}
                        >
                          {rule.severity}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <span className="flex items-center gap-1.5 font-semibold text-gray-300">
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              rule.status === "Enabled" ? "bg-[#00ff66] animate-pulse shadow-[0_0_6px_#00ff66]" : "bg-gray-650"
                            }`}
                          ></span>
                          {rule.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </GlassPanel>

        {/* Create and Validate Custom logic panel (1/3 width) */}
        <GlassPanel borderColor="cyan" className="p-5 space-y-4 h-fit">
          <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
            RULES.DEPLOY // INGESTION LOGIC
          </div>
          <form onSubmit={handleCreateRule} className="space-y-4">
            <div className="space-y-1">
              <label className="text-[10px] text-gray-400 uppercase">Rule Name:</label>
              <input
                type="text"
                placeholder="SSH Brute Force Detection"
                value={newRuleName}
                onChange={(e) => setNewRuleName(e.target.value)}
                className="w-full bg-[#111827] border border-gray-800 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-amber-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-[10px] text-gray-400 uppercase">Severity:</label>
                <select
                  value={newRuleSeverity}
                  onChange={(e) => setNewRuleSeverity(e.target.value)}
                  className="w-full bg-[#111827] border border-gray-800 rounded px-2 py-1.5 text-xs text-white outline-none focus:border-amber-500"
                >
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-gray-400 uppercase">Mitre ID:</label>
                <input
                  type="text"
                  placeholder="T1046"
                  value={newRuleMitre}
                  onChange={(e) => setNewRuleMitre(e.target.value)}
                  className="w-full bg-[#111827] border border-gray-800 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-amber-500"
                />
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between items-center">
                <label className="text-[10px] text-gray-400 uppercase">Query logic block (JSON):</label>
                <button
                  type="button"
                  onClick={handleValidate}
                  className="text-[10px] text-cyan-400 hover:text-cyan-300 font-bold uppercase"
                >
                  Check Syntax
                </button>
              </div>
              <textarea
                rows={3}
                value={newRuleLogic}
                onChange={(e) => setNewRuleLogic(e.target.value)}
                className="w-full bg-[#050b14] border border-gray-800 rounded p-2.5 font-mono text-xs text-green-400 outline-none focus:border-cyan-500 scrollbar-thin"
              />
            </div>

            {/* Validation output overlay */}
            {validationError && (
              <div className="p-2 bg-red-950/20 border border-red-500/20 text-red-400 rounded text-[10px] flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-red-500 flex-shrink-0" />
                <span>{validationError}</span>
              </div>
            )}

            {validationResult && (
              <div
                className={`p-2.5 rounded text-[10px] flex items-start gap-1.5 border ${
                  validationResult.valid
                    ? "bg-green-950/20 border-green-500/20 text-green-400"
                    : "bg-red-950/20 border-red-500/20 text-red-400"
                }`}
              >
                {validationResult.valid ? (
                  <>
                    <CheckCircle className="w-3.5 h-3.5 text-green-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-bold">Logic validated successfully!</div>
                      <div className="text-[9px] text-gray-400 mt-0.5">Parameters match telemetry metrics schemas.</div>
                    </div>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="w-3.5 h-3.5 text-red-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-bold">Validation check failed.</div>
                      <div className="text-[9px] text-gray-400 mt-0.5">
                        Errors: {validationResult.errors?.map((e: any) => `${e.field}: ${e.message}`).join(", ")}
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}

            <button
              type="submit"
              className="w-full py-2 bg-amber-500 hover:bg-amber-600 font-bold text-xs uppercase text-black rounded transition-all shadow-[0_0_15px_rgba(245,166,35,0.25)]"
            >
              Deploy Custom Rule
            </button>
          </form>
        </GlassPanel>
      </div>
    </div>
  );
};
