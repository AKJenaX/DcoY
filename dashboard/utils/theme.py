"""Custom CSS styling and theme configuration injection for the dashboard."""

import streamlit as st

THEME_CSS = """
<style>
/* Color & Spacing Configuration */
:root {
    --bg-primary: #0B1220;
    --bg-secondary: #0E1728;
    --card-bg: #111827;
    --card-bg-sec: #1F2937;
    --border-color: rgba(255, 255, 255, 0.08);
    --primary: #3B82F6;
    --secondary: #22D3EE;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
    --purple: #8B5CF6;
    --text-primary: #F9FAFB;
    --text-secondary: #9CA3AF;
    --muted: #6B7280;
}

/* Streamlit Container Overrides */
.stApp {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.block-container {
    padding-top: 1rem!important;
    padding-bottom: 2rem!important;
    max-width: 100%!important;
}
.st-emotion-cache-1y4p8pa {
    padding-left: 1.2rem!important;
    padding-right: 1.2rem!important;
}

/* Hide Default Streamlit Elements */
header[data-testid="stHeader"] {
    background-color: transparent!important;
}
div[data-testid="stStatusWidget"] {
    display: none!important;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: var(--bg-secondary)!important;
    border-right: 1px solid var(--border-color)!important;
    min-width: 250px!important;
    max-width: 250px!important;
}

/* Sticky Top Navigation Bar with Backdrop Blur */
.top-navbar {
    position: sticky;
    top: 0;
    z-index: 999;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: rgba(11, 18, 32, 0.85);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border-color);
    padding: 0.75rem 2rem;
    margin-top: -1.5rem;
    margin-left: -3rem;
    margin-right: -3rem;
    margin-bottom: 1.5rem;
}
.navbar-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.navbar-logo-text {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.5px;
}
.navbar-subtitle {
    font-size: 0.75rem;
    color: var(--text-secondary);
    border-left: 1px solid var(--border-color);
    padding-left: 0.75rem;
    margin-left: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.navbar-center {
    flex-grow: 1;
    max-width: 480px;
    margin: 0 2rem;
}
.navbar-search-box {
    width: 100%;
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0.45rem 1rem;
    color: var(--text-primary);
    font-size: 0.85rem;
    outline: none;
    transition: border-color 0.15s ease;
}
.navbar-search-box:focus {
    border-color: var(--primary);
}
.navbar-right {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}
.navbar-icon-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.15s ease;
}
.navbar-icon-btn:hover {
    color: var(--text-primary);
}
.navbar-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: var(--primary);
    border: 2px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    color: white;
}

/* Premium Card Components (Targeting Streamlit Container Borders) */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: var(--card-bg)!important;
    border: 1px solid var(--border-color)!important;
    border-radius: 18px!important;
    padding: 1.15rem!important;
    margin-bottom: 0.65rem!important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.14)!important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease!important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(59, 130, 246, 0.25)!important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.24)!important;
    transform: translateY(-1px)!important;
}

/* Typography Hierarchy classes */
.page-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.5px;
    margin: 0;
}
.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-top: 0.75rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    letter-spacing: -0.01em;
}
.card-title {
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: 0.25rem;
}
.muted-helper {
    font-size: 0.75rem;
    color: var(--muted);
}
.widget-shell { display:flex; flex-direction:column; gap:0.55rem; }
.widget-header { display:flex; justify-content:space-between; align-items:flex-start; gap:0.75rem; }
.widget-title { font-size:0.78rem; font-weight:700; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.12em; }
.widget-subtitle { font-size:0.8rem; color:var(--text-secondary); margin-top:0.2rem; }
.widget-metric { font-size:1.55rem; font-weight:800; color:var(--text-primary); line-height:1; }
.widget-icon { width: 36px; height: 36px; border-radius: 10px; display:flex; align-items:center; justify-content:center; background: rgba(255,255,255,0.06); border:1px solid var(--border-color); color:var(--primary); }
.widget-trend { font-size:0.72rem; color:var(--success); font-weight:700; }
.widget-body { font-size:0.9rem; color:var(--text-secondary); line-height:1.55; }
.widget-body.compact { font-size:0.85rem; }
.timeline-list { display:flex; flex-direction:column; gap:0.6rem; }
.timeline-item { display:flex; gap:0.6rem; align-items:flex-start; padding:0.6rem 0.7rem; border-radius:12px; background: rgba(255,255,255,0.03); border:1px solid var(--border-color); }
.timeline-badge { width:28px; min-width:28px; height:28px; border-radius:999px; display:flex; align-items:center; justify-content:center; background: rgba(59,130,246,0.12); color: var(--primary); font-weight:700; font-size:0.78rem; }
.timeline-label { font-size:0.82rem; font-weight:700; color:var(--text-primary); }
.timeline-detail { font-size:0.78rem; color:var(--text-secondary); margin-top:0.2rem; }
.ai-list { display:flex; flex-direction:column; gap:0.5rem; }
.ai-item { padding:0.6rem 0.75rem; border-radius:12px; background: rgba(255,255,255,0.03); border:1px solid var(--border-color); color:var(--text-secondary); font-size:0.82rem; }
.empty-state { display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; min-height: 180px; color:var(--text-secondary); }
.empty-icon { font-size:1.7rem; margin-bottom:0.6rem; color:var(--primary); }
.existing-widget { border-left:3px solid var(--primary); }

/* Enterprise widget SDK styles */
.chart-toolbar { display:flex; align-items:center; gap:0.45rem; flex-wrap:wrap; }
.chart-toolbar-chip { padding:0.25rem 0.5rem; border-radius:999px; background:rgba(255,255,255,0.05); color:var(--text-secondary); font-size:0.7rem; text-transform:uppercase; letter-spacing:0.08em; }
.chart-toolbar-btn { border:1px solid var(--border-color); background:rgba(255,255,255,0.03); color:var(--text-primary); border-radius:8px; padding:0.25rem 0.55rem; cursor:pointer; font-size:0.72rem; }
.chart-legend { font-size:0.75rem; color:var(--text-secondary); margin-top:0.35rem; }
.chart-footer { margin-top:0.7rem; color:var(--text-secondary); font-size:0.8rem; }
.confidence-badge { padding:0.25rem 0.55rem; border-radius:999px; background:rgba(16,185,129,0.12); color:var(--success); font-size:0.7rem; font-weight:700; text-transform:uppercase; }
.severity-badge { padding:0.25rem 0.55rem; border-radius:999px; font-size:0.7rem; font-weight:700; text-transform:uppercase; }
.severity-badge.high { background:rgba(239,68,68,0.12); color:var(--danger); }
.severity-badge.medium { background:rgba(245,158,11,0.12); color:var(--warning); }
.severity-badge.low { background:rgba(16,185,129,0.12); color:var(--success); }
.status-pill { padding:0.25rem 0.55rem; border-radius:999px; font-size:0.7rem; font-weight:700; text-transform:uppercase; }
.status-pill.healthy { background:rgba(16,185,129,0.12); color:var(--success); }
.status-pill.degraded { background:rgba(245,158,11,0.12); color:var(--warning); }
.status-pill.critical { background:rgba(239,68,68,0.12); color:var(--danger); }
.chip { display:inline-block; padding:0.2rem 0.45rem; margin:0.2rem 0.2rem 0 0; border-radius:999px; background:rgba(59,130,246,0.12); font-size:0.7rem; color:var(--primary); }
.ai-footer-group { display:flex; flex-wrap:wrap; gap:0.25rem; align-items:center; margin-top:0.6rem; }
.empty-state-shell { display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; min-height:165px; padding:1rem; border-radius:16px; background:rgba(255,255,255,0.02); border:1px solid var(--border-color); }
.empty-state-shell.accent-primary { border-color:rgba(59,130,246,0.18); }
.empty-state-shell.accent-success { border-color:rgba(16,185,129,0.18); }
.empty-state-shell.accent-warning { border-color:rgba(245,158,11,0.18); }
.empty-state-shell.accent-danger { border-color:rgba(239,68,68,0.18); }
.empty-state-icon { font-size:1.5rem; margin-bottom:0.45rem; }
.empty-state-title { font-size:0.9rem; font-weight:700; color:var(--text-primary); margin-bottom:0.15rem; }
.empty-state-message { font-size:0.8rem; color:var(--text-secondary); }
.empty-state-detail { font-size:0.74rem; color:var(--muted); margin-top:0.25rem; }
.table-toolbar { display:flex; align-items:center; gap:0.35rem; }
.stDataFrame { border-radius:12px; overflow:hidden; }
.stDataFrame [data-testid="stHorizontalBlock"] { gap:0.25rem; }

/* Accessibility and reduced motion support */
:focus-visible {
    outline: 2px solid rgba(59, 130, 246, 0.9);
    outline-offset: 2px;
}
button:focus-visible, input:focus-visible, [role="button"]:focus-visible {
    outline: 2px solid rgba(59, 130, 246, 0.9);
    outline-offset: 2px;
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}

/* Sidebar Custom List Items selection overrides */
.sidebar-menu-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.65rem 1rem;
    border-radius: 8px;
    color: var(--text-secondary);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.15s ease, color 0.15s ease;
    margin-bottom: 0.25rem;
    border-left: 3px solid transparent;
}
.sidebar-menu-item:hover {
    background-color: rgba(255, 255, 255, 0.02);
    color: var(--text-primary);
}
.sidebar-menu-item.active {
    background-color: rgba(59, 130, 246, 0.08);
    color: var(--primary);
    border-left-color: var(--primary);
}

/* High Fidelity KPI metrics cards styling */
.soc-kpi-card {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}
.soc-kpi-icon {
    width: 38px;
    height: 38px;
    border-radius: 8px;
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
}
.soc-kpi-icon.blue { color: var(--primary); background-color: rgba(59, 130, 246, 0.06); }
.soc-kpi-icon.danger { color: var(--danger); background-color: rgba(239, 68, 68, 0.06); }
.soc-kpi-icon.warning { color: var(--warning); background-color: rgba(245, 158, 11, 0.06); }
.soc-kpi-icon.success { color: var(--success); background-color: rgba(16, 185, 129, 0.06); }
.soc-kpi-icon.purple { color: var(--purple); background-color: rgba(139, 92, 246, 0.06); }
.soc-kpi-icon.cyan { color: var(--secondary); background-color: rgba(34, 211, 238, 0.06); }

.trend-badge {
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
}
.trend-badge.up { background-color: rgba(16, 185, 129, 0.08); color: var(--success); }
.trend-badge.down { background-color: rgba(239, 68, 68, 0.08); color: var(--danger); }
.trend-badge.stable { background-color: rgba(255, 255, 255, 0.04); color: var(--text-secondary); }

/* Dark Terminal Logs Feed Box */
.terminal-window {
    background-color: #050b14;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    font-family: "Courier New", Courier, monospace;
    font-size: 0.8rem;
    padding: 1rem;
    height: 350px;
    overflow-y: auto;
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.8);
}
.terminal-window::-webkit-scrollbar, .st-emotion-cache-1y4p8pa::-webkit-scrollbar { width: 8px; }
.terminal-window::-webkit-scrollbar-thumb, .st-emotion-cache-1y4p8pa::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 999px; }
.terminal-line {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 0.35rem;
    line-height: 1.4;
    border-bottom: 1px solid rgba(255, 255, 255, 0.01);
    padding-bottom: 0.25rem;
}
.terminal-num {
    color: var(--muted);
    text-align: right;
    width: 25px;
    user-select: none;
}
.terminal-time {
    color: #10b981; /* success green timestamp */
}
.terminal-ip {
    color: #3b82f6; /* primary blue IP */
    font-weight: bold;
}
.terminal-level {
    font-weight: bold;
}
.terminal-level.high { color: var(--danger); }
.terminal-level.medium { color: var(--warning); }
.terminal-level.low { color: var(--success); }

.terminal-text {
    color: #e2e8f0;
    flex-grow: 1;
}

/* Custom Table badge pills formatting */
.badge {
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.7rem;
    text-transform: uppercase;
    display: inline-block;
}
.badge.danger { background-color: rgba(239, 68, 68, 0.08); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.15); }
.badge.warning { background-color: rgba(245, 158, 11, 0.08); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.15); }
.badge.success { background-color: rgba(16, 185, 129, 0.08); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.15); }
.badge.info { background-color: rgba(59, 130, 246, 0.08); color: var(--primary); border: 1px solid rgba(59, 130, 246, 0.15); }
.badge.cyan { background-color: rgba(34, 211, 238, 0.08); color: var(--secondary); border: 1px solid rgba(34, 211, 238, 0.15); }
.badge.purple { background-color: rgba(139, 92, 246, 0.08); color: var(--purple); border: 1px solid rgba(139, 92, 246, 0.15); }

/* SVG Icons Styles overrides */
.soc-icon {
    width: 16px;
    height: 16px;
    fill: none;
    stroke: currentColor;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
    display: inline-block;
    vertical-align: middle;
}

/* Custom Table and Avatar Overrides */
.soc-table-container {
    overflow-x: auto;
    width: 100%;
}
.soc-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
}
.soc-table th {
    padding: 0.72rem 0.9rem;
    border-bottom: 1px solid var(--border-color);
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.12em;
}
.soc-table td {
    padding: 0.72rem 0.9rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.84rem;
    color: var(--text-primary);
    vertical-align: middle;
}
.soc-table tr:hover {
    background-color: rgba(255, 255, 255, 0.03);
}
.avatar {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background-color: rgba(59, 130, 246, 0.1);
    color: var(--primary);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 700;
    margin-right: 0.5rem;
    vertical-align: middle;
}

/* Threat Intel Right Panel Gauge */
.gauge-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
    background-color: var(--card-bg-sec);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    text-align: center;
    margin-bottom: 1.25rem;
}
.gauge-value {
    font-size: 2.25rem;
    font-weight: 800;
    color: var(--danger);
    text-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
}

/* Loading Shimmer Skeletons */
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
.shimmer-skeleton {
    background: linear-gradient(90deg, #1f2937 25%, #374151 50%, #1f2937 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 8px;
    height: 16px;
    margin-bottom: 0.75rem;
}
.shimmer-skeleton.title { height: 28px; width: 60%; margin-bottom: 1.25rem; }
.shimmer-skeleton.card { height: 120px; border-radius: 16px; margin-bottom: 1.25rem; }
</style>
"""

def inject_custom_theme():
    """Injects custom CSS styles into the Streamlit DOM header."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)
