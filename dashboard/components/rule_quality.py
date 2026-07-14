"""Rule Quality, Health, and Coverage Dashboard component."""

import requests
import streamlit as st
from typing import Any, Dict, List


def render_rule_quality_panel(api_base: str) -> None:
    """Renders a collapsible Rule Quality & Coverage panel inside Detection Engineering."""

    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}

    with st.expander("📊 Rule Quality & Coverage Dashboard", expanded=False):
        tab_health, tab_coverage, tab_metrics = st.tabs(["🏥 Health", "🗺️ Coverage", "📈 Metrics"])

        # ─── Health Tab ──────────────────────────────────────────────────────
        with tab_health:
            sel_rid = st.session_state.get("selected_rule_id", 1)
            if sel_rid and sel_rid != -1:
                try:
                    r_health = requests.get(f"{api_base}/api/rules/{sel_rid}/health", headers=headers, timeout=10, verify=False)
                    if r_health.status_code == 200:
                        h = r_health.json()
                        h1, h2, h3, h4 = st.columns(4)
                        with h1:
                            st.metric("Trigger Count", h["trigger_count"])
                        with h2:
                            lt = h.get("last_triggered")
                            st.metric("Last Triggered", "Never" if not lt else "Recent")
                        with h3:
                            st.metric("Avg Exec Time", f"{h['avg_execution_time_ms']:.1f}ms")
                        with h4:
                            score = h["health_score"]
                            color = "🟢" if score >= 0.7 else ("🟡" if score >= 0.4 else "🔴")
                            st.metric("Health Score", f"{color} {score}")

                        st.markdown(
                            f"""
                            <div style="background-color: var(--bg-secondary); padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-color); margin-top: 0.5rem;">
                              <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:0.5rem;">
                                <span>False Positive Est: <b>{h['false_positive_estimate'] * 100:.1f}%</b></span>
                                <span>Detection Coverage: <b>{h['detection_coverage'] * 100:.1f}%</b></span>
                              </div>
                              <div style="font-size:0.72rem; color:var(--text-secondary);">Rule: <b>{h['name']}</b> | Status: <b>{h['status']}</b></div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.info("No health data available for this rule.")
                except Exception as e:
                    st.error(f"Error loading health data: {str(e)}")
            else:
                st.info("Select a rule from the Rule Explorer to view health metrics.")

        # ─── Coverage Tab ────────────────────────────────────────────────────
        with tab_coverage:
            try:
                r_cov = requests.get(f"{api_base}/api/rules/coverage", headers=headers, timeout=10, verify=False)
                if r_cov.status_code == 200:
                    cov = r_cov.json()

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Total Rules", cov["total_rules"])
                    with c2:
                        st.metric("MITRE Covered", f"{cov['mitre_covered']}/{cov['mitre_total']}")
                    with c3:
                        st.metric("Coverage %", f"{cov['mitre_coverage_pct']}%")

                    # Severity distribution
                    st.markdown("##### Rule Distribution by Severity")
                    sev = cov.get("severity_distribution", {})
                    sv1, sv2, sv3 = st.columns(3)
                    with sv1:
                        st.markdown(
                            f'<div style="text-align:center; padding:0.5rem; background:var(--bg-secondary); border-radius:6px; border:1px solid var(--border-color);">'
                            f'<div style="font-size:1.5rem; font-weight:700; color:var(--danger);">{sev.get("High", 0)}</div>'
                            f'<div style="font-size:0.7rem; color:var(--text-secondary);">High</div></div>',
                            unsafe_allow_html=True
                        )
                    with sv2:
                        st.markdown(
                            f'<div style="text-align:center; padding:0.5rem; background:var(--bg-secondary); border-radius:6px; border:1px solid var(--border-color);">'
                            f'<div style="font-size:1.5rem; font-weight:700; color:var(--warning);">{sev.get("Medium", 0)}</div>'
                            f'<div style="font-size:0.7rem; color:var(--text-secondary);">Medium</div></div>',
                            unsafe_allow_html=True
                        )
                    with sv3:
                        st.markdown(
                            f'<div style="text-align:center; padding:0.5rem; background:var(--bg-secondary); border-radius:6px; border:1px solid var(--border-color);">'
                            f'<div style="font-size:1.5rem; font-weight:700; color:var(--success);">{sev.get("Low", 0)}</div>'
                            f'<div style="font-size:0.7rem; color:var(--text-secondary);">Low</div></div>',
                            unsafe_allow_html=True
                        )

                    # Category distribution
                    st.markdown("##### Detection Categories")
                    cats = cov.get("category_distribution", {})
                    for cat_name, count in sorted(cats.items(), key=lambda x: x[1], reverse=True):
                        st.markdown(
                            f'<div style="display:flex; justify-content:space-between; padding:0.3rem 0.5rem; border-bottom: 1px solid var(--border-color); font-size:0.8rem;">'
                            f'<span>{cat_name}</span><span style="font-weight:700;">{count}</span></div>',
                            unsafe_allow_html=True
                        )

                    # Uncovered tactics
                    uncovered = cov.get("uncovered_tactics", [])
                    if uncovered:
                        st.markdown("##### ⚠️ Uncovered MITRE Tactics")
                        for tactic in uncovered:
                            st.markdown(f"- `{tactic}`")
                    else:
                        st.success("All tracked MITRE ATT&CK tactics are covered!")
                else:
                    st.error(f"Failed to fetch coverage data: {r_cov.status_code}")
            except Exception as e:
                st.error(f"Error loading coverage data: {str(e)}")

        # ─── Metrics Tab ─────────────────────────────────────────────────────
        with tab_metrics:
            try:
                r_met = requests.get(f"{api_base}/api/rules/metrics/all", headers=headers, timeout=10, verify=False)
                if r_met.status_code == 200:
                    all_metrics = r_met.json()
                    if all_metrics:
                        for m in all_metrics:
                            st.markdown(
                                f"""
                                <div style="background-color: var(--bg-secondary); padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-color); margin-bottom: 0.5rem;">
                                  <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:0.25rem;">
                                    <b>Rule ID: {m['rule_id']}</b>
                                    <span>Health: <b>{m['health_score']}</b></span>
                                  </div>
                                  <div style="display:flex; gap:1rem; font-size:0.72rem; color:var(--text-secondary);">
                                    <span>Exec: {m['executions']}</span>
                                    <span>Matches: {m['matches']}</span>
                                    <span>Trigger Rate: {m['trigger_rate'] * 100:.1f}%</span>
                                    <span>Avg Latency: {m['avg_latency_ms']:.1f}ms</span>
                                    <span>Cache Hit: {m['cache_hit_ratio'] * 100:.0f}%</span>
                                    <span>Failures: {m['failed_evaluations']}</span>
                                  </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.info("No rule execution metrics recorded yet. Run a rule test to generate data.")
                else:
                    st.error(f"Failed to fetch metrics: {r_met.status_code}")
            except Exception as e:
                st.error(f"Error loading metrics: {str(e)}")


def render_validation_errors(errors: List[Dict[str, str]]) -> None:
    """Renders inline validation errors/warnings."""
    for err in errors:
        icon = "❌" if err["severity"] == "error" else "⚠️"
        color = "var(--danger)" if err["severity"] == "error" else "var(--warning)"
        st.markdown(
            f'<div style="padding:0.4rem 0.6rem; margin-bottom:0.3rem; border-left:3px solid {color}; background:var(--bg-secondary); border-radius:4px; font-size:0.8rem;">'
            f'{icon} <b>{err["field"]}</b>: {err["message"]}</div>',
            unsafe_allow_html=True
        )


def render_ai_validation_assistant(rule_data: Dict[str, Any], errors: List[Dict[str, str]]) -> None:
    """Renders AI validation assistant suggestions based on detected errors."""
    if not errors:
        return

    suggestions: List[str] = []
    for err in errors:
        field = err["field"]
        if field == "detection_logic":
            suggestions.append(
                "**Detection Logic Fix:** Ensure the JSON criteria uses valid key-value pairs matching your telemetry schema. "
                "Example: `{\"event_type\": \"ssh_bruteforce\"}`"
            )
        elif field == "threshold":
            suggestions.append(
                "**Threshold Tuning:** Consider increasing the time window or reducing the threshold. "
                "A threshold of 5-10 with a 60-120s window typically balances sensitivity and noise."
            )
        elif field == "mitre_technique":
            suggestions.append(
                "**MITRE Mapping:** The specified technique may be outdated. Review the MITRE ATT&CK framework "
                "and consider techniques like T1110 (Brute Force) or T1046 (Network Scanning)."
            )
        elif field == "name":
            suggestions.append(
                "**Duplicate Name:** Each rule must have a unique name. Append a version suffix or category prefix "
                "to differentiate similar rules."
            )

    if not suggestions:
        suggestions.append("Review the flagged fields and correct any invalid values before enabling this rule.")

    from dashboard.components.widget_variants import AIWidget
    AIWidget(
        title="AI Validation Assistant",
        bullets=suggestions,
        subtitle="Rule Verification Suggestions",
        confidence="High (92%)",
        key=f"ai_val_{rule_data.get('name') or 'rule'}"
    ).render()
