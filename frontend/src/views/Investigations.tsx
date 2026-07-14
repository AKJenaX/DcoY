import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { Plus, Trash2, ArrowLeft, Send } from "lucide-react";
import { GlassPanel } from "../components/GlassPanel";

interface Case {
  id: string;
  title: string;
  status: string;
  priority: string;
  severity: string;
  assigned_analyst: string;
  risk_score: number;
  ai_summary?: string;
  created_at?: string;
}

interface InvestigationsProps {
  initialCaseId?: string | null;
  onClearInitialCaseId?: () => void;
}

export const Investigations: React.FC<InvestigationsProps> = ({ initialCaseId, onClearInitialCaseId }) => {
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [caseDetails, setCaseDetails] = useState<any>(null);
  const [newCaseTitle, setNewCaseTitle] = useState("");
  const [newNoteText, setNewNoteText] = useState("");
  const [copilotQuery, setCopilotQuery] = useState("recommend_actions");
  const [copilotResponse, setCopilotResponse] = useState<any>(null);
  const [copilotLoading, setCopilotLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (initialCaseId) {
      setSelectedCaseId(initialCaseId);
      if (onClearInitialCaseId) onClearInitialCaseId();
    }
  }, [initialCaseId]);

  const loadCases = async () => {
    try {
      setError("");
      const data = await api.getCases();
      setCases(data || []);
    } catch (err: any) {
      setError("Failed to fetch cases database ledger.");
    }
  };

  const loadCaseDetails = async (id: string) => {
    try {
      setError("");
      const data = await api.getCaseDetails(id);
      setCaseDetails(data);
      setCopilotResponse(null);
    } catch (err) {
      setError("Failed to sync case parameters.");
    }
  };

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCaseTitle.trim()) return;

    const caseId = `CASE-2026-${Math.floor(100 + Math.random() * 900)}`;
    const newCase = {
      id: caseId,
      title: newCaseTitle,
      status: "Open",
      priority: "Medium",
      severity: "Medium",
      assigned_analyst: "operator",
      risk_score: 0.5,
      ai_summary: "Awaiting incident analysis pipeline match...",
      notes: "Auto-generated investigation case record.",
    };

    try {
      setError("");
      await api.createCase(newCase);
      setNewCaseTitle("");
      await loadCases();
    } catch (err) {
      setError("Could not insert case record.");
    }
  };

  const handleDeleteCase = async (id: string) => {
    try {
      setError("");
      await api.deleteCase(id);
      setSelectedCaseId(null);
      setCaseDetails(null);
      await loadCases();
    } catch (err) {
      setError("Could not purge case record.");
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNoteText.trim() || !selectedCaseId) return;

    try {
      await api.addCaseNote(selectedCaseId, newNoteText);
      setNewNoteText("");
      await loadCaseDetails(selectedCaseId);
    } catch (err) {
      setError("Could not write analyst note.");
    }
  };

  const queryCopilot = async () => {
    if (!selectedCaseId) return;
    setCopilotLoading(true);
    setCopilotResponse(null);
    try {
      const data = await api.askCaseCopilot(selectedCaseId, copilotQuery);
      setCopilotResponse(data);
    } catch (err: any) {
      setError("AI assistant query failed. Ensure Ollama service or server is reachable.");
    } finally {
      setCopilotLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, []);

  useEffect(() => {
    if (selectedCaseId) {
      loadCaseDetails(selectedCaseId);
    }
  }, [selectedCaseId]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center pb-4 page-header-glass">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono text-amber-500 uppercase tracking-widest mb-1">
            <span className="w-2 h-2 rounded-full bg-[#ffb300] animate-pulse shadow-[0_0_8px_#ffb300]"></span>
            CONSOLE.STATUS // INVESTIGATIONS_ACTIVE
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white font-mono uppercase">Investigations workspace</h1>
          <p className="text-xs text-gray-400">Triage anomalous security cases and run incident playbook reviews</p>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-950/30 border border-red-500/50 rounded-md text-red-400 text-xs font-mono">
          [ALERT] {error}
        </div>
      )}

      {!selectedCaseId && (
        <GlassPanel borderColor="cyan" className="p-5 min-h-[220px] grid grid-cols-1 lg:grid-cols-[220px_minmax(0,1fr)] gap-5 overflow-hidden">
          <div className="border-r border-gray-800 pr-5">
            <div className="flex items-center gap-2 text-[10px] font-mono font-bold tracking-widest text-cyan-400 uppercase">
              <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
              CASE.CHRONO // TIMELINE
            </div>
            <div className="mt-3 text-3xl font-black font-mono text-white">{cases.length || 3}</div>
            <div className="text-[10px] uppercase tracking-widest text-gray-500 font-mono">Active ledgers</div>
            <div className="mt-5 rounded border border-amber-500/20 bg-amber-950/10 p-3 text-xs text-gray-300 font-sans">
              Timeline-first triage highlights escalation order before analyst assignment.
            </div>
          </div>
          <div className="relative pl-6">
            <div className="absolute left-1 top-1 bottom-1 w-px bg-gradient-to-b from-cyan-500/70 via-amber-500/50 to-gray-800" />
            {[
              ["12:00:15", "Ingress alert correlated to decoy SSH telemetry", "Detected"],
              ["12:02:40", "Evidence bundle attached to credential case", "Linked"],
              ["12:04:12", "Containment playbook awaiting operator review", "Queued"],
              ["12:08:33", "Analyst note requested for final severity rating", "Review"],
            ].map(([time, title, status], idx) => (
              <div key={title} className="relative mb-3 last:mb-0">
                <div className={`absolute -left-[27px] top-1 h-3 w-3 rounded-full border border-[#0d0f14] ${idx === 0 ? "bg-red-500" : idx === 2 ? "bg-amber-500" : "bg-cyan-400"}`} />
                <div className="flex items-center justify-between rounded border border-gray-800 bg-[#050b14]/70 px-3 py-2">
                  <div>
                    <div className="font-mono text-[10px] text-gray-500">{time}</div>
                    <div className="text-xs font-semibold text-gray-200">{title}</div>
                  </div>
                  <span className="text-[9px] font-bold uppercase tracking-widest text-amber-500">{status}</span>
                </div>
              </div>
            ))}
          </div>
        </GlassPanel>
      )}

      {/* Main Workspace splits */}
      {!selectedCaseId ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left / Center list of cases */}
          <GlassPanel borderColor="amber" className="lg:col-span-2 p-5 space-y-4">
            <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-amber-500 uppercase">
              <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,166,35,0.6)]"></span>
              CASE.LEDGER // ACTIVE INVESTIGATIONS
            </div>
            
            <div className="space-y-2">
              {cases.length === 0 ? (
                <div className="text-gray-500 text-center py-10">Zero open investigations matching active filters.</div>
              ) : (
                cases.map((c) => (
                  <div
                    key={c.id}
                    onClick={() => setSelectedCaseId(c.id)}
                    className="p-4 bg-[#111827]/40 border border-gray-800 hover:border-amber-500/40 rounded-lg flex justify-between items-center cursor-pointer transition-all hover:translate-x-1"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono font-bold text-cyan-400 bg-cyan-950/30 px-2 py-0.5 rounded border border-cyan-500/20">
                          {c.id}
                        </span>
                        <h3 className="text-sm font-bold text-white">{c.title}</h3>
                      </div>
                      <p className="text-[11px] text-gray-400 line-clamp-1">{c.ai_summary}</p>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-0.5 text-[9px] uppercase font-bold rounded ${
                        c.status === "Open" ? "bg-red-500/10 text-red-400 border border-red-500/20" : "bg-green-500/10 text-green-400 border border-green-500/20"
                      }`}>
                        {c.status}
                      </span>
                      <span className="text-xs font-mono font-bold text-gray-400">
                        Risk: {c.risk_score.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </GlassPanel>

          {/* Right column: Create a new case */}
          <GlassPanel borderColor="cyan" className="p-5 space-y-4 h-fit">
            <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase">
              <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
              CASE.ESCALATE // DISPATCH PANEL
            </div>
            <form onSubmit={handleCreateCase} className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs text-gray-400">Investigation Case Title:</label>
                <input
                  type="text"
                  placeholder="e.g. Host WS-OPERATOR brute force check"
                  value={newCaseTitle}
                  onChange={(e) => setNewCaseTitle(e.target.value)}
                  className="w-full bg-[#111827] border border-gray-800 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-amber-500"
                />
              </div>
              <button
                type="submit"
                className="w-full py-2 bg-amber-500 hover:bg-amber-600 font-bold text-xs uppercase text-black rounded transition-all flex items-center justify-center gap-1 shadow-[0_0_15px_rgba(245,166,35,0.25)]"
              >
                <Plus className="w-4 h-4" /> Spin New Case
              </button>
            </form>
          </GlassPanel>
        </div>
      ) : (
        /* Case details expanded split view */
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          {/* Core Case Details, Evidence & Notes (3/4 width) */}
          <div className="xl:col-span-3 space-y-6">
            <div className="flex items-center gap-4">
              <button
                onClick={() => {
                  setSelectedCaseId(null);
                  setCaseDetails(null);
                }}
                className="p-1.5 bg-[#111827] border border-gray-800 hover:border-gray-700 rounded text-gray-400 hover:text-white"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
              <div>
                <span className="text-[10px] font-mono font-bold text-cyan-400">{caseDetails?.id}</span>
                <h2 className="text-lg font-bold text-white">{caseDetails?.title}</h2>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Evidence Log list */}
              <GlassPanel borderColor="amber" className="p-5 space-y-3 flex flex-col h-[350px]">
                <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-amber-500 uppercase">
                  <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,166,35,0.6)]"></span>
                  CASE.EVIDENCE // FORENSIC BUNDLE
                </div>
                <div className="flex-1 overflow-y-auto space-y-2 font-mono text-xs pr-1 scrollbar-thin">
                  {!caseDetails?.evidence || caseDetails.evidence.length === 0 ? (
                    <div className="text-gray-500 text-center py-10 font-sans">No evidence logs registered to case database.</div>
                  ) : (
                    caseDetails.evidence.map((ev: any, idx: number) => (
                      <div key={idx} className="p-2.5 bg-[#050b14]/90 border border-gray-800 rounded">
                        <div className="text-[10px] text-gray-400 mb-1">{ev.timestamp || "2026-07-13 12:00:00"}</div>
                        <div className="text-white font-semibold">{ev.event}</div>
                        <div className="flex justify-between items-center mt-1 text-[10px] text-gray-400 font-sans">
                          <span>MITRE: {ev.mitre || "N/A"}</span>
                          <span className="text-red-400 uppercase font-bold">{ev.severity}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </GlassPanel>

              {/* Chronological Timeline track */}
              <GlassPanel borderColor="cyan" className="p-5 space-y-3 flex flex-col h-[350px]">
                <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase">
                  <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
                  CASE.TRACK // EVENT LOGS
                </div>
                <div className="flex-1 overflow-y-auto space-y-3 relative pl-4 border-l border-gray-800 pr-1 scrollbar-thin">
                  {!caseDetails?.timeline || caseDetails.timeline.length === 0 ? (
                    <div className="text-gray-500 text-center py-10 font-sans">No chronological timeline logs registered.</div>
                  ) : (
                    caseDetails.timeline.map((tl: any, idx: number) => (
                      <div key={idx} className="relative space-y-1">
                        {/* Dot indicator */}
                        <div className="absolute -left-[21px] top-1 w-2 h-2 rounded-full bg-cyan-400 border border-[#0d0f14]"></div>
                        <div className="text-[9px] font-mono text-gray-400">{tl.timestamp}</div>
                        <div className="text-xs text-white font-semibold">{tl.event}</div>
                        <p className="text-[11px] text-gray-400 font-sans">{tl.details}</p>
                      </div>
                    ))
                  )}
                </div>
              </GlassPanel>
            </div>

            {/* Analyst notes thread */}
            <GlassPanel borderColor="amber" className="p-5 space-y-4">
              <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-amber-500 uppercase">
                <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse shadow-[0_0_6px_rgba(245,166,35,0.6)]"></span>
                CASE.NOTES // CONSOLE CHAT
              </div>
              <div className="space-y-3 max-h-[220px] overflow-y-auto pr-1 scrollbar-thin">
                {!caseDetails?.notes_list || caseDetails.notes_list.length === 0 ? (
                  <div className="text-gray-500 text-xs py-2 font-sans">No analyst notes recorded yet.</div>
                ) : (
                  caseDetails.notes_list.map((note: any, idx: number) => (
                    <div key={idx} className="p-3 bg-[#111827]/50 border border-gray-800 rounded-lg font-mono">
                      <div className="flex justify-between items-center text-[10px] text-gray-400 mb-1">
                        <span className="font-bold text-amber-500">{note.author}</span>
                        <span>{note.created_at || "Just now"}</span>
                      </div>
                      <p className="text-xs text-gray-200 font-sans">{note.content}</p>
                    </div>
                  ))
                )}
              </div>
              <form onSubmit={handleAddNote} className="flex gap-2">
                <input
                  type="text"
                  placeholder="Record an analyst note / triage summary..."
                  value={newNoteText}
                  onChange={(e) => setNewNoteText(e.target.value)}
                  className="flex-1 bg-[#111827]/70 border border-gray-800 rounded-md px-3 py-1.5 text-xs text-white outline-none focus:border-amber-500"
                />
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/40 hover:border-amber-500 rounded-md text-xs font-semibold text-amber-400 flex items-center gap-1 transition-all"
                >
                  <Send className="w-3.5 h-3.5" /> Post
                </button>
              </form>
            </GlassPanel>
          </div>

          {/* Right column: AI Copilot Strategy Panel (1/4 width) */}
          <GlassPanel borderColor="cyan" className="p-5 flex flex-col justify-between h-fit space-y-4">
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase">
                <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_6px_rgba(0,229,255,0.6)]"></span>
                AI.COPILOT // SUGGESTION ACTIVE
              </div>

              <div className="space-y-2">
                <label className="text-[10px] text-gray-400">Analysis Perspective:</label>
                <select
                  value={copilotQuery}
                  onChange={(e) => setCopilotQuery(e.target.value)}
                  className="w-full bg-[#111827] border border-gray-800 rounded px-2 py-1.5 text-xs text-white outline-none focus:border-cyan-500"
                >
                  <option value="recommend_actions">Recommend Next SOC Actions</option>
                  <option value="summarize_incident">Summarize Incident Scope</option>
                  <option value="suggest_containment">Suggest Containment Strategy</option>
                  <option value="recommend_evidence">Recommend Additional Evidence</option>
                  <option value="draft_report">Draft Incident Wiki Report</option>
                </select>
              </div>

              <button
                onClick={queryCopilot}
                disabled={copilotLoading}
                className="w-full py-2 bg-cyan-500 hover:bg-cyan-600 font-bold text-xs uppercase text-black rounded transition-all flex items-center justify-center gap-1 shadow-[0_0_15px_rgba(0,229,255,0.25)]"
              >
                🔮 Consult AI assistant
              </button>
            </div>

            {/* Standardized glow box output layout for AI suggestion */}
            {copilotLoading && (
              <div className="text-[10px] text-gray-400 text-center py-4 animate-pulse">Drafting playbook insights...</div>
            )}

            {copilotResponse && (
              <div className="border border-cyan-500/30 bg-cyan-950/20 rounded p-4 space-y-3 text-cyan-200">
                <div className="flex justify-between items-center border-b border-cyan-500/20 pb-2">
                  <span className="text-[10px] font-bold uppercase">
                    Copilot Strategy {copilotResponse.source === "fallback" ? "(Fallback)" : "(Live)"}
                  </span>
                  <span className="text-[9px] bg-cyan-500/10 px-1.5 py-0.5 rounded text-cyan-400 font-bold border border-cyan-500/20">
                    {copilotResponse.confidence}
                  </span>
                </div>
                <div className="space-y-2">
                  {copilotResponse.bullets?.map((bullet: string, idx: number) => (
                    <p key={idx} className="text-xs leading-relaxed">• {bullet}</p>
                  ))}
                </div>
                {copilotResponse.actions?.length > 0 && (
                  <div className="space-y-2 border-t border-cyan-500/20 pt-2">
                    <span className="text-[9px] text-gray-400 uppercase tracking-wider block">Suggested Actions:</span>
                    {copilotResponse.actions.map((act: string) => (
                      <button
                        key={act}
                        onClick={() => alert(`Mock Execution: '${act}'`)}
                        className="w-full py-1 text-center bg-cyan-500 hover:bg-cyan-600 font-bold text-[10px] uppercase text-black rounded transition-all mt-1"
                      >
                        Execute: {act}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            <button
              onClick={() => handleDeleteCase(selectedCaseId)}
              className="w-full py-2 bg-red-950/20 hover:bg-red-950/40 border border-red-500/20 hover:border-red-500/40 text-red-400 font-bold text-xs uppercase rounded transition-all flex items-center justify-center gap-1"
            >
              <Trash2 className="w-3.5 h-3.5" /> Purge Case Ledger
            </button>
            </GlassPanel>
        </div>
      )}
    </div>
  );
};
