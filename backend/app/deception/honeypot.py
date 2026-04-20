"""Phase 5: smart honeypot selection (simulated responses, no real honeypot daemons)."""

from typing import Any, Dict, List

# Keys for /detect "response_summary" — must match honeypot values from select_honeypot.
RESPONSE_SUMMARY_KEYS = ("ssh_honeypot", "web_honeypot", "generic_trap", "none")


def select_honeypot(attack_type: str) -> dict:
    """
    Pick a honeypot tier from the classified attack_type.

    Rationale (demo / viva):
    - ssh_bruteforce → ssh_honeypot: attacker expects SSH; we waste their time on a fake shell.
    - web_attack → web_honeypot: high HTTP-like volume; decoy login pages distract scrapers/bots.
    - port_scan → generic_trap: reconnaissance across ports; fake listeners + logging without mimicking one app.
    - anything else (e.g. normal) → none: no deception cost on benign traffic.
    """
    if attack_type == "ssh_bruteforce":
        return {
            "honeypot": "ssh_honeypot",
            "action": "Simulate SSH login environment",
            "status": "deployed",
        }
    if attack_type == "web_attack":
        return {
            "honeypot": "web_honeypot",
            "action": "Serve fake login page",
            "status": "deployed",
        }
    if attack_type == "port_scan":
        return {
            "honeypot": "generic_trap",
            "action": "Open fake ports and monitor",
            "status": "deployed",
        }
    return {
        "honeypot": "none",
        "action": "No action required",
        "status": "ignored",
    }


def build_response_summary(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count rows by selected honeypot kind (for API aggregation)."""
    summary = {key: 0 for key in RESPONSE_SUMMARY_KEYS}
    for row in records:
        kind = row.get("honeypot")
        if kind in summary:
            summary[kind] += 1
    return summary
