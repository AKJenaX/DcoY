"""
Deception agent (Phase 7).

Consumes detection events and attaches a honeypot plan using the same rules as Phase 5
(select_honeypot). Keeps deception policy isolated from ML and from final response policy.
"""

from typing import Any, Dict, List

from app.deception.honeypot import select_honeypot


def adaptive_honeypot_selection(event_type: str, profile: str) -> dict:
    """
    Select honeypot dynamically based on attack type and attacker profile.
    """
    # Advanced attackers → high interaction deception
    if profile == "advanced":
        if event_type == "ssh_bruteforce":
            return {
                "honeypot": "high_interaction_ssh_honeypot",
                "action": "Simulate full SSH environment with realistic responses",
                "status": "deployed"
            }
        elif event_type == "web_attack":
            return {
                "honeypot": "dynamic_web_honeypot",
                "action": "Serve adaptive fake web application with logging",
                "status": "deployed"
            }
        else:
            return {
                "honeypot": "adaptive_trap",
                "action": "Dynamically adjust system responses to mislead attacker",
                "status": "deployed"
            }

    # Automated tools → standard traps
    elif profile == "automated_tool":
        if event_type == "ssh_bruteforce":
            return {
                "honeypot": "standard_ssh_honeypot",
                "action": "Simulate SSH login prompts for automated tools",
                "status": "deployed"
            }
        elif event_type == "port_scan":
            return {
                "honeypot": "port_scan_trap",
                "action": "Expose fake open ports to track scanning tools",
                "status": "deployed"
            }
        else:
            return {
                "honeypot": "generic_honeypot",
                "action": "Monitor automated attack patterns",
                "status": "deployed"
            }

    # Beginner attackers → simple traps
    elif profile == "beginner":
        return {
            "honeypot": "basic_trap",
            "action": "Simple fake service to observe beginner behavior",
            "status": "deployed"
        }

    # Unknown → fallback
    else:
        return {
            "honeypot": "none",
            "action": "No deception applied",
            "status": "ignored"
        }


def process(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    For each message, choose a honeypot from event_type (attack class).

    Adds:
    - honeypot: which decoy tier to stand up
    - deception_action: human-readable decoy behavior
    - deception_status: deploy vs ignore (simulated)
    """
    updated: List[Dict[str, Any]] = []
    for msg in messages:
        out = dict(msg)
        profile = out.get("attacker_profile", "unknown")
        event_type = str(out.get("event_type", "normal"))
        
        honeypot_data = adaptive_honeypot_selection(event_type, profile)
        
        out["honeypot"] = honeypot_data["honeypot"]
        out["deception_action"] = honeypot_data["action"]
        out["deception_status"] = honeypot_data["status"]
        out["deception_reason"] = f"{profile} attacker detected, applying adaptive deception strategy"
        
        updated.append(out)
    return updated
