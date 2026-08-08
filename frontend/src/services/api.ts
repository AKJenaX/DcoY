const API_BASE = "https://dcoy-9n8n.onrender.com";

const getHeaders = () => {
  const token = localStorage.getItem("auth_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};


const originalFetch = window.fetch;
window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
  const options = init || {};
  const isWrite = options.method && ["POST", "PUT", "DELETE"].includes(options.method.toUpperCase());
  let timeoutId: any = null;

  if (isWrite) {
    timeoutId = setTimeout(() => {
      window.dispatchEvent(
        new CustomEvent("show-toast", {
          detail: { message: "Action queued, retrying...", type: "warning" },
        })
      );
    }, 2000);
  }

  try {
    const response = await originalFetch(input, init);
    if (isWrite && timeoutId) {
      clearTimeout(timeoutId);
      window.dispatchEvent(
        new CustomEvent("show-toast", {
          detail: { message: "", type: "clear" },
        })
      );
    }

    if (response.status === 401) {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("username");
      window.history.pushState({}, "", "/login");
      window.dispatchEvent(
        new CustomEvent("show-toast", {
          detail: { message: "Session expired - please log in again", type: "warning" },
        })
      );
      window.dispatchEvent(new CustomEvent("auth-session-expired"));
      throw new Error("Session expired. Redirecting to login.");
    }
    return response;
  } catch (err) {
    if (isWrite && timeoutId) {
      clearTimeout(timeoutId);
      window.dispatchEvent(
        new CustomEvent("show-toast", {
          detail: { message: "", type: "clear" },
        })
      );
    }
    throw err;
  }
};

export const api = {
  // Authentication
  async login(username = "operator", password = "secure_password") {
    let res: Response;
    try {
      res = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
    } catch {
      throw new Error("Backend unreachable. Start FastAPI on port 8001, then try again.");
    }
    if (!res.ok) throw new Error("Invalid credentials");
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem("auth_token", data.access_token);
      localStorage.setItem("username", username);
    }
    return data;
  },

  async register(username = "operator", password = "secure_password") {
    let res: Response;
    try {
      res = await fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
    } catch {
      throw new Error("Backend unreachable. Start FastAPI on port 8001, then try again.");
    }
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Registration failed");
    }
    return res.json();
  },

  logout() {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("username");
  },

  isLoggedIn() {
    return !!localStorage.getItem("auth_token");
  },

  getUsername() {
    return localStorage.getItem("username") || "operator";
  },

  // Telemetry logs
  async getDetectLogs() {
    const res = await fetch(`${API_BASE}/detect`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch logs");
    return res.json();
  },

  async getExplainableAlerts() {
    const res = await fetch(`${API_BASE}/explain`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch explainable alerts");
    return res.json();
  },

  // Executive dashboard KPIs
  async getExecutiveMetrics() {
    const res = await fetch(`${API_BASE}/api/executive/metrics`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch executive metrics");
    return res.json();
  },

  // Cases (Investigations) Workspace
  async getCases(params: { status?: string; priority?: string } = {}) {
    const query = new URLSearchParams(params as any).toString();
    const res = await fetch(`${API_BASE}/api/investigations?${query}`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch cases");
    return res.json();
  },

  async createCase(caseData: any) {
    const res = await fetch(`${API_BASE}/api/investigations`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(caseData),
    });
    if (!res.ok) throw new Error("Failed to create case");
    return res.json();
  },

  async getCaseDetails(id: string) {
    const res = await fetch(`${API_BASE}/api/investigations/${id}`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch case details");
    return res.json();
  },

  async updateCase(id: string, updates: any) {
    const res = await fetch(`${API_BASE}/api/investigations/${id}`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify(updates),
    });
    if (!res.ok) throw new Error("Failed to update case");
    return res.json();
  },

  async deleteCase(id: string) {
    const res = await fetch(`${API_BASE}/api/investigations/${id}`, {
      method: "DELETE",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to delete case");
    return res.json();
  },

  async addCaseEvidence(id: string, evidenceData: any) {
    const res = await fetch(`${API_BASE}/api/investigations/${id}/evidence`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(evidenceData),
    });
    if (!res.ok) throw new Error("Failed to attach evidence");
    return res.json();
  },

  async addCaseNote(id: string, content: string) {
    const res = await fetch(`${API_BASE}/api/investigations/${id}/notes`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ content, author: this.getUsername() }),
    });
    if (!res.ok) throw new Error("Failed to add note");
    return res.json();
  },

  // AI assistant within case Q&A
  async askCaseCopilot(caseId: string, queryType: string) {
    const res = await fetch(`${API_BASE}/api/incident-response/ai-assistant`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ query_type: queryType, case_id: caseId }),
    });
    if (!res.ok) throw new Error("AI assistant request failed");
    return res.json();
  },

  // Knowledge Graph attack path analysis
  async getKnowledgeGraph() {
    const res = await fetch(`${API_BASE}/api/soar/knowledge-graph/graph`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch knowledge graph");
    return res.json();
  },

  async getGraphAnalytics() {
    const res = await fetch(`${API_BASE}/api/soar/knowledge-graph/analytics`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch graph analytics");
    return res.json();
  },

  async getShortestPath(source: string, target: string) {
    const query = new URLSearchParams({ source, target }).toString();
    const res = await fetch(`${API_BASE}/api/soar/knowledge-graph/attack-paths?${query}`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch shortest paths");
    return res.json();
  },

  async askGraphCopilot(prompt: string) {
    const res = await fetch(`${API_BASE}/api/soar/knowledge-graph/ai-assistant`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ prompt }),
    });
    if (!res.ok) throw new Error("AI graph assistant failed");
    const data = await res.json();
    return {
      ...data,
      content: data.content || data.answer || "",
      source: data.source || "fallback",
    };
  },

  // Detection Rules
  async getDetectionRules() {
    const res = await fetch(`${API_BASE}/api/rules`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch rules");
    return res.json();
  },

  async createDetectionRule(ruleData: any) {
    const res = await fetch(`${API_BASE}/api/rules`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(ruleData),
    });
    if (!res.ok) throw new Error("Failed to create rule");
    return res.json();
  },

  async validateRule(logic: any) {
    const res = await fetch(`${API_BASE}/api/rules/validate`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ detection_logic: logic }),
    });
    if (!res.ok) throw new Error("Rule validation check failed");
    return res.json();
  },

  // PDF Report Compilation
  getReportDownloadUrl() {
    return `${API_BASE}/report`;
  },

  async compileReport() {
    const res = await fetch(`${API_BASE}/report`, {
      headers: {
        ...getHeaders(),
        Accept: "application/pdf",
      },
    });
    if (!res.ok) {
      const detail = await res.text().catch(() => "");
      throw new Error(detail || `Failed to compile report PDF (${res.status})`);
    }
    const contentType = res.headers.get("content-type") || "";
    if (!contentType.includes("application/pdf")) {
      throw new Error("Invalid response format received from compiler.");
    }
    return res.blob();
  },

  // Purple Team Simulations
  async getSimulations() {
    const res = await fetch(`${API_BASE}/api/simulations`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch simulations");
    return res.json();
  },

  async triggerSimulation(scenarioName: string) {
    const res = await fetch(`${API_BASE}/api/simulations`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ scenario_name: scenarioName }),
    });
    if (!res.ok) throw new Error("Failed to trigger simulation");
    return res.json();
  },

  async getSimulationsKpis() {
    const res = await fetch(`${API_BASE}/api/simulations/kpis`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch simulation KPIs");
    return res.json();
  },

  // Platform Diagnostics & Search
  async getPlatformHealth() {
    const res = await fetch(`${API_BASE}/api/soar/platform/health`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch platform health metrics");
    return res.json();
  },

  async getPlatformDocs() {
    const res = await fetch(`${API_BASE}/api/soar/platform/docs`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch developer docs");
    return res.json();
  },

  async getApiInventory() {
    const res = await fetch(`${API_BASE}/api/soar/platform/api-inventory`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch API endpoint inventory");
    return res.json();
  },

  async triggerDemoAttack() {
    const res = await fetch(`${API_BASE}/api/soar/platform/demo/trigger`, {
      method: "POST",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to trigger demo attack scenario");
    return res.json();
  },

  async clearDemoTelemetry() {
    const res = await fetch(`${API_BASE}/api/soar/platform/demo/clear`, {
      method: "POST",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to clear demo telemetry");
    return res.json();
  },

  async globalSearch(query: string) {
    const res = await fetch(`${API_BASE}/api/soar/platform/search?query=${encodeURIComponent(query)}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Global search failed");
    return res.json();
  },
};
