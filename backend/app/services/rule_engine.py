"""Rule evaluation engine service for ad-hoc and live telemetry detection matching."""

import json
import time
from typing import Any, Dict, List, Tuple
from app.models.detection_rule import DBDetectionRule
from app.services.rule_metrics import RuleMetrics


class RuleEngine:
    """Evaluates security rules against network telemetry caches with performance compiling caches."""

    def __init__(self) -> None:
        # Cache for parsed JSON rule criteria
        self._compiled_cache: Dict[int, Dict[str, Any]] = {}
        self.metrics = RuleMetrics()

    def compile_rule(self, rule: DBDetectionRule) -> Dict[str, Any]:
        """Parses and caches the JSON criteria for the specified rule."""
        rule_any: Any = rule
        r_id = int(rule_any.id)
        if r_id in self._compiled_cache:
            return self._compiled_cache[r_id]
        
        try:
            criteria = json.loads(str(rule_any.detection_logic))
        except Exception:
            # Fallback to key-value or empty if invalid
            criteria = {}
            
        self._compiled_cache[r_id] = criteria
        return criteria

    def clear_cache(self, rule_id: int) -> None:
        """Purge cached compilation for rule modification updates."""
        if rule_id in self._compiled_cache:
            del self._compiled_cache[rule_id]

    def evaluate_event(self, rule: DBDetectionRule, event: Dict[str, Any]) -> bool:
        """Evaluates a single telemetry event against the rule logic."""
        criteria = self.compile_rule(rule)
        if not criteria:
            return False

        # Match criteria fields
        for key, expected_val in criteria.items():
            if key not in event:
                # Key missing
                return False
                
            actual_val = event[key]
            # Case-insensitive checks for string values
            if isinstance(expected_val, str) and isinstance(actual_val, str):
                if expected_val.lower() != actual_val.lower():
                    return False
            else:
                if expected_val != actual_val:
                    return False
                    
        return True

    def test_rule(
        self,
        rule: DBDetectionRule,
        telemetry: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], float, float]:
        """Runs the rule against all telemetry logs.

        Returns:
            Tuple of (Matched Events, Execution Time (ms), Coverage Rate (0.0 - 1.0))
        """
        rule_any: Any = rule
        r_id = int(rule_any.id)
        cache_hit = r_id in self._compiled_cache

        start_time = time.perf_counter()
        failed = False
        matched = []
        
        try:
            for event in telemetry:
                if self.evaluate_event(rule, event):
                    matched.append(event)
        except Exception:
            failed = True
                
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        coverage = len(matched) / max(1, len(telemetry))

        # Record metrics
        self.metrics.record_execution(
            rule_id=r_id,
            matched_count=len(matched),
            duration_ms=duration_ms,
            cache_hit=cache_hit,
            failed=failed,
        )

        return matched, duration_ms, coverage

    def benchmark_rule(
        self,
        rule: DBDetectionRule,
        telemetry: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Run a full performance benchmark on a rule against telemetry."""
        rule_any: Any = rule
        r_id = int(rule_any.id)
        total_events = len(telemetry)

        start = time.perf_counter()
        matched, duration_ms, coverage = self.test_rule(rule, telemetry)
        end = time.perf_counter()

        return {
            "rule_id": r_id,
            "total_events_scanned": total_events,
            "matching_events": len(matched),
            "execution_time_ms": round(duration_ms, 2),
            "wall_time_ms": round((end - start) * 1000, 2),
            "detection_coverage": round(coverage, 4),
            "estimated_production_impact": "Low" if len(matched) < 5 else ("Medium" if len(matched) < 20 else "High"),
            "cache_state": "hit" if r_id in self._compiled_cache else "miss",
        }
