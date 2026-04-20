"""
Response agent (Phase 7–8, Phase 10).

Phase 10: dynamic response strategy — combines risk_level with event_type (attack context)
so actions match the scenario, not only the risk bucket. Prior fields on each message
(risk_score, severity, honeypot, etc.) are preserved.
"""

from typing import Any, Dict, List


def decide_response(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Choose final response_action_final, response_status_final, and a human-readable
    strategy_reason from risk_level + event_type.
    """
    out = dict(message)
    level = out.get("risk_level", "low")
    event_type = out.get("event_type", "normal")

    if level == "high":
        if event_type == "ssh_bruteforce":
            out["response_action_final"] = "block_ip_and_deploy_ssh_honeypot"
            out["strategy_reason"] = (
                "High-risk SSH brute-force attack detected, blocking IP and deploying SSH honeypot"
            )
        elif event_type == "web_attack":
            out["response_action_final"] = "block_ip_and_deploy_web_honeypot"
            out["strategy_reason"] = (
                "High-risk web attack detected, blocking IP and deploying web honeypot"
            )
        elif event_type == "port_scan":
            out["response_action_final"] = "block_ip_and_deploy_generic_trap"
            out["strategy_reason"] = (
                "High-risk port scan detected, blocking IP and deploying generic trap"
            )
        else:
            out["response_action_final"] = "block_ip_and_monitor"
            out["strategy_reason"] = (
                "High-risk activity detected, blocking IP and applying strict monitoring"
            )
        out["response_status_final"] = "enforced"

    elif level == "medium":
        if event_type == "ssh_bruteforce":
            out["response_action_final"] = "rate_limit_and_deploy_ssh_honeypot"
            out["strategy_reason"] = (
                "Medium-risk SSH brute-force activity detected, rate limiting and deploying SSH honeypot"
            )
        elif event_type == "web_attack":
            out["response_action_final"] = "delay_response_and_deploy_web_honeypot"
            out["strategy_reason"] = (
                "Medium-risk web attack detected, delaying responses and deploying web honeypot"
            )
        elif event_type == "port_scan":
            out["response_action_final"] = "monitor_ports_and_deploy_trap"
            out["strategy_reason"] = (
                "Medium-risk port scan detected, monitoring ports and deploying trap"
            )
        else:
            out["response_action_final"] = "monitor_and_log"
            out["strategy_reason"] = (
                "Medium-risk activity detected, monitoring and logging for follow-up"
            )
        out["response_status_final"] = "active_monitoring"

    else:
        # Low risk — observe quietly without disruptive controls.
        out["response_action_final"] = "silent_monitoring"
        out["response_status_final"] = "passive"
        out["strategy_reason"] = "Low-risk activity, passive monitoring"

    return out


def process(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Run the dynamic strategy for each agent message."""
    return [decide_response(msg) for msg in messages]
