"""Rule validation service for detection rule quality assessment."""

import json
from typing import Any, Dict, List, Optional, Tuple


# Known MITRE ATT&CK technique IDs
VALID_MITRE_TECHNIQUES = {
    "T1110 - Brute Force",
    "T1046 - Network Scanning",
    "T1190 - Exploit Public-Facing Application",
    "T1210 - Exploitation of Remote Services",
    "T1059 - Command and Scripting Interpreter",
    "T1078 - Valid Accounts",
    "T1021 - Remote Services",
    "T1053 - Scheduled Task/Job",
    "T1071 - Application Layer Protocol",
    "T1486 - Data Encrypted for Impact",
    "T1566 - Phishing",
    "T1003 - OS Credential Dumping",
    "T1055 - Process Injection",
    "T1027 - Obfuscated Files or Information",
    "T1083 - File and Directory Discovery",
    "T1082 - System Information Discovery",
    "T1569 - System Services",
    "T1547 - Boot or Logon Autostart Execution",
    "T1218 - System Binary Proxy Execution",
}

VALID_CATEGORIES = {
    "Brute Force", "Port Scan", "Credential Stuffing",
    "Lateral Movement", "Privilege Escalation",
    "Suspicious PowerShell", "Public Exploit",
    "Beaconing", "Impossible Travel", "Custom Rules",
}

VALID_SEVERITIES = {"High", "Medium", "Low"}
VALID_STATUSES = {"Enabled", "Disabled"}


class RuleValidationError:
    """Represents a single validation error or warning."""
    def __init__(self, field: str, message: str, severity: str = "error") -> None:
        self.field = field
        self.message = message
        self.severity = severity  # "error" or "warning"

    def to_dict(self) -> Dict[str, str]:
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity,
        }


class RuleValidator:
    """Validates detection rule configurations for correctness and quality."""

    def validate(self, rule_data: Dict[str, Any], existing_names: Optional[List[str]] = None) -> Tuple[bool, List[Dict[str, str]]]:
        """Run all validation checks against rule_data.

        Returns:
            Tuple of (is_valid, list_of_error_dicts)
        """
        errors: List[RuleValidationError] = []
        existing_names = existing_names or []

        self._check_required_fields(rule_data, errors)
        self._check_detection_logic(rule_data, errors)
        self._check_mitre_mapping(rule_data, errors)
        self._check_duplicate_name(rule_data, existing_names, errors)
        self._check_threshold_conflicts(rule_data, errors)
        self._check_category(rule_data, errors)
        self._check_severity(rule_data, errors)

        is_valid = all(e.severity != "error" for e in errors)
        return is_valid, [e.to_dict() for e in errors]

    def _check_required_fields(self, data: Dict[str, Any], errors: List[RuleValidationError]) -> None:
        required = ["name", "description", "detection_logic"]
        for field in required:
            val = data.get(field)
            if not val or (isinstance(val, str) and not val.strip()):
                errors.append(RuleValidationError(field, f"'{field}' is required and cannot be empty."))

    def _check_detection_logic(self, data: Dict[str, Any], errors: List[RuleValidationError]) -> None:
        logic = data.get("detection_logic", "")
        if not logic:
            return
        try:
            parsed = json.loads(logic)
            if not isinstance(parsed, dict):
                errors.append(RuleValidationError("detection_logic", "Detection logic must be a JSON object with key-value criteria."))
            elif len(parsed) == 0:
                errors.append(RuleValidationError("detection_logic", "Detection logic is empty — rule will never match.", severity="warning"))
        except (json.JSONDecodeError, TypeError):
            errors.append(RuleValidationError("detection_logic", "Detection logic contains invalid JSON syntax."))

    def _check_mitre_mapping(self, data: Dict[str, Any], errors: List[RuleValidationError]) -> None:
        mitre = data.get("mitre_technique")
        if mitre and mitre not in VALID_MITRE_TECHNIQUES:
            errors.append(RuleValidationError("mitre_technique", f"Unknown MITRE technique: '{mitre}'. Verify against ATT&CK framework.", severity="warning"))

    def _check_duplicate_name(self, data: Dict[str, Any], existing: List[str], errors: List[RuleValidationError]) -> None:
        name = data.get("name", "").strip().lower()
        if name and name in [n.lower() for n in existing]:
            errors.append(RuleValidationError("name", f"A rule named '{data.get('name')}' already exists. Choose a unique name."))

    def _check_threshold_conflicts(self, data: Dict[str, Any], errors: List[RuleValidationError]) -> None:
        threshold = data.get("threshold", 5)
        time_window = data.get("time_window", 60)

        if isinstance(threshold, int) and threshold < 1:
            errors.append(RuleValidationError("threshold", "Threshold must be at least 1."))
        if isinstance(time_window, int) and time_window < 5:
            errors.append(RuleValidationError("time_window", "Time window must be at least 5 seconds."))
        if isinstance(threshold, int) and isinstance(time_window, int):
            if threshold > 0 and time_window > 0 and threshold > time_window:
                errors.append(RuleValidationError("threshold", "Threshold exceeds time window — rule may never trigger.", severity="warning"))

    def _check_category(self, data: Dict[str, Any], errors: List[RuleValidationError]) -> None:
        cat = data.get("category")
        if cat and cat not in VALID_CATEGORIES:
            errors.append(RuleValidationError("category", f"Unknown category: '{cat}'.", severity="warning"))

    def _check_severity(self, data: Dict[str, Any], errors: List[RuleValidationError]) -> None:
        sev = data.get("severity")
        if sev and sev not in VALID_SEVERITIES:
            errors.append(RuleValidationError("severity", f"Invalid severity: '{sev}'. Use High, Medium, or Low."))
