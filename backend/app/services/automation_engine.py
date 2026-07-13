"""SOAR Automation integration execution engine."""

import time
import random
from typing import Any, Dict


class AutomationEngine:
    """Simulates integration actions (e.g. Block IP, Isolate Host, Disable User, Slack, Teams) without making real network changes."""

    @staticmethod
    def execute_action(action_type: str, parameter: str) -> Dict[str, Any]:
        """Execute a simulated security orchestration action."""
        # Add a tiny simulation latency
        time.sleep(random.uniform(0.1, 0.3))
        
        status = "Success"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        action_type_lower = action_type.lower()
        if "block_ip" in action_type_lower or "block ip" in action_type_lower:
            detail = f"Blocked malicious source IP: '{parameter}' on ingress cloud edge firewalls (Rule: DCOY-AUTO-BLOCK-{parameter})."
        elif "disable_user" in action_type_lower or "disable user" in action_type_lower:
            detail = f"Disabled compromised Active Directory user profile: '{parameter}' and expired all active single sign-on tokens."
        elif "isolate_host" in action_type_lower or "isolate host" in action_type_lower:
            detail = f"Isolated host node: '{parameter}' from local workstation subnets via SentinelOne endpoint agent isolation."
        elif "create_ticket" in action_type_lower or "create ticket" in action_type_lower:
            detail = f"Created Jira Service Desk incident escalation ticket (Key: SOAR-IR-{random.randint(100, 999)})."
        elif "slack" in action_type_lower:
            detail = f"Dispatched incoming Slack webhook alert notification to channel '#security-ops' detailing target '{parameter}'."
        elif "teams" in action_type_lower:
            detail = f"Dispatched Microsoft Teams channel card warning message regarding incident '{parameter}'."
        elif "email" in action_type_lower or "send email" in action_type_lower:
            detail = f"Dispatched summary threat containment report via SMTP email to SOC distribution list: '{parameter}'."
        elif "open_investigation" in action_type_lower or "open investigation" in action_type_lower:
            detail = f"Initiated secondary DB investigation case for asset tracker: '{parameter}'."
        elif "execute_playbook" in action_type_lower or "execute playbook" in action_type_lower:
            detail = f"Assigned and triggered containment playbook template: '{parameter}'."
        elif "executive_report" in action_type_lower or "executive report" in action_type_lower:
            detail = f"Compiled CISO executive PDF report for case: '{parameter}'."
        else:
            detail = f"Executed generic simulated automation step '{action_type}' with parameter: '{parameter}'."

        return {
            "status": status,
            "timestamp": timestamp,
            "action": action_type,
            "detail": detail
        } if False else {  # pyright typing guard
            "status": status,
            "timestamp": timestamp,
            "detail": detail
        }
