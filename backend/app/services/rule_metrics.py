"""Rule metrics and health tracking service for detection quality observability."""

import time
from typing import Any, Dict, List, Optional


class RuleMetrics:
    """Tracks per-rule execution metrics for health scoring and analytics."""

    def __init__(self) -> None:
        self._metrics: Dict[int, Dict[str, Any]] = {}

    def _ensure_entry(self, rule_id: int) -> Dict[str, Any]:
        if rule_id not in self._metrics:
            self._metrics[rule_id] = {
                "executions": 0,
                "matches": 0,
                "total_latency_ms": 0.0,
                "failed_evaluations": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "last_triggered": None,
                "trigger_count": 0,
            }
        return self._metrics[rule_id]

    def record_execution(
        self,
        rule_id: int,
        matched_count: int,
        duration_ms: float,
        cache_hit: bool = False,
        failed: bool = False,
    ) -> None:
        """Record a single rule execution attempt."""
        entry = self._ensure_entry(rule_id)
        entry["executions"] += 1
        entry["matches"] += matched_count
        entry["total_latency_ms"] += duration_ms

        if cache_hit:
            entry["cache_hits"] += 1
        else:
            entry["cache_misses"] += 1

        if failed:
            entry["failed_evaluations"] += 1

        if matched_count > 0:
            entry["trigger_count"] += 1
            entry["last_triggered"] = time.time()

    def get_metrics(self, rule_id: int) -> Dict[str, Any]:
        """Return computed metrics for a single rule."""
        entry = self._ensure_entry(rule_id)
        executions = entry["executions"]
        matches = entry["matches"]
        total_cache = entry["cache_hits"] + entry["cache_misses"]

        avg_latency = entry["total_latency_ms"] / max(1, executions)
        trigger_rate = matches / max(1, executions)
        cache_hit_ratio = entry["cache_hits"] / max(1, total_cache)

        # Health score: weighted composite (0.0 - 1.0)
        latency_score = max(0.0, 1.0 - (avg_latency / 100.0))
        failure_penalty = entry["failed_evaluations"] / max(1, executions)
        health_score = round(max(0.0, min(1.0, (latency_score * 0.4 + (1.0 - failure_penalty) * 0.3 + trigger_rate * 0.3))), 2)

        return {
            "rule_id": rule_id,
            "executions": executions,
            "matches": matches,
            "trigger_rate": round(trigger_rate, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "failed_evaluations": entry["failed_evaluations"],
            "cache_hits": entry["cache_hits"],
            "cache_misses": entry["cache_misses"],
            "cache_hit_ratio": round(cache_hit_ratio, 4),
            "trigger_count": entry["trigger_count"],
            "last_triggered": entry["last_triggered"],
            "health_score": health_score,
        }

    def get_all_metrics(self) -> List[Dict[str, Any]]:
        """Return computed metrics for all tracked rules."""
        return [self.get_metrics(rid) for rid in self._metrics]

    def get_coverage_stats(self, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute detection coverage analytics from a list of rule dicts."""
        mitre_set: set[str] = set()
        category_counts: Dict[str, int] = {}
        severity_counts: Dict[str, int] = {"High": 0, "Medium": 0, "Low": 0}

        for r in rules:
            mitre = r.get("mitre_technique")
            if mitre:
                mitre_set.add(mitre)

            cat = r.get("category", "Custom Rules")
            category_counts[cat] = category_counts.get(cat, 0) + 1

            sev = r.get("severity", "Medium")
            if sev in severity_counts:
                severity_counts[sev] += 1

        # All known tactics for coverage gap analysis
        all_tactics = {
            "T1110 - Brute Force", "T1046 - Network Scanning",
            "T1190 - Exploit Public-Facing Application",
            "T1210 - Exploitation of Remote Services",
            "T1059 - Command and Scripting Interpreter",
            "T1078 - Valid Accounts", "T1021 - Remote Services",
            "T1053 - Scheduled Task/Job",
            "T1071 - Application Layer Protocol",
            "T1486 - Data Encrypted for Impact",
            "T1566 - Phishing", "T1003 - OS Credential Dumping",
        }
        uncovered = sorted(all_tactics - mitre_set)

        return {
            "total_rules": len(rules),
            "mitre_covered": len(mitre_set),
            "mitre_total": len(all_tactics),
            "mitre_coverage_pct": round(len(mitre_set) / max(1, len(all_tactics)) * 100, 1),
            "uncovered_tactics": uncovered,
            "category_distribution": category_counts,
            "severity_distribution": severity_counts,
        }
