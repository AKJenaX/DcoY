"""Custom CSS styling and theme configuration injection for the dashboard."""

import streamlit as st

THEME_CSS = """
<style>
/* Color & Grid Layout Configuration */
:root {
    --bg-primary: #07111F;
    --bg-secondary: #0E1728;
    --card-bg: #111C2D;
    --border-color: rgba(255, 255, 255, 0.05);
    --primary: #3B82F6;
    --secondary: #22D3EE;
    --danger: #EF4444;
    --warning: #F59E0B;
    --success: #22C55E;
    --purple: #8B5CF6;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --muted: #64748B;
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
    background-color: rgba(14, 23, 40, 0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
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
    border-radius: 12px!important;
    padding: 1.25rem!important;
    margin-bottom: 0.5rem!important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)!important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease!important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(59, 130, 246, 0.2)!important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(59, 130, 246, 0.03)!important;
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
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-top: 0.75rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.card-title {
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: 0.25rem;
}
.muted-helper {
    font-size: 0.75rem;
    color: var(--muted);
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
.soc-kpi-icon.success { color: var(--success); background-color: rgba(34, 197, 94, 0.06); }
.soc-kpi-icon.purple { color: var(--purple); background-color: rgba(139, 92, 246, 0.06); }
.soc-kpi-icon.cyan { color: var(--secondary); background-color: rgba(34, 211, 238, 0.06); }

.trend-badge {
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
}
.trend-badge.up { background-color: rgba(34, 197, 94, 0.08); color: var(--success); }
.trend-badge.down { background-color: rgba(239, 68, 68, 0.08); color: var(--danger); }
.trend-badge.stable { background-color: rgba(255, 255, 255, 0.04); color: var(--text-secondary); }

/* Dark Terminal Logs Feed Box */
.terminal-window {
    background-color: #050b14;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-family: "Courier New", Courier, monospace;
    font-size: 0.8rem;
    padding: 1rem;
    height: 350px;
    overflow-y: auto;
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.8);
}
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
    color: #4ade80; /* green timestamp */
}
.terminal-ip {
    color: #38bdf8; /* cyan IP address */
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

/* System Status Nodes Grid layout */
.status-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
}
.status-node {
    background-color: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.status-label {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-secondary);
}
.status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    position: relative;
}
.status-indicator.green {
    background-color: var(--success);
    box-shadow: 0 0 8px var(--success);
}
.status-indicator.green::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background-color: var(--success);
    opacity: 0.4;
    animation: pulse-ring 1.5s infinite ease-in-out;
}
.status-indicator.yellow {
    background-color: var(--warning);
    box-shadow: 0 0 8px var(--warning);
}
.status-indicator.red {
    background-color: var(--danger);
    box-shadow: 0 0 8px var(--danger);
}

@keyframes pulse-ring {
    0% { transform: scale(1); opacity: 0.4; }
    100% { transform: scale(2.5); opacity: 0; }
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
.badge.success { background-color: rgba(34, 197, 94, 0.08); color: var(--success); border: 1px solid rgba(34, 197, 94, 0.15); }
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
</style>
"""

def inject_custom_theme():
    """Inject custom CSS styling into the Streamlit application."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)
