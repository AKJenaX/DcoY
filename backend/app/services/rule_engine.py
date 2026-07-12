"""Rule evaluation engine service for ad-hoc and live telemetry detection matching."""

import json
import time
from typing import Any, Dict, List, Tuple
from app.models.detection_rule import DBDetectionRule


class RuleEngine:
    """Evaluates security rules against network telemetry caches with performance compiling caches."""

    def __init__(self) -> None:
        # Cache for parsed JSON rule criteria
        self._compiled_cache: Dict[int, Dict[str, Any]] = {}

    def compile_rule(self, rule: DBDetectionRule) -> Dict[str, Any]:
        """Parses and caches the JSON criteria for the specified rule."""
        if rule.id in self._compiled_cache:
            return self._compiled_cache[rule.id]
        
        try:
            criteria = json.loads(rule.detection_logic)
        except Exception:
            # Fallback to key-value or empty if invalid
            criteria = {}
            
        self._compiled_cache[rule.id] = criteria
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
        start_time = time.perf_counter()
        matched = []
        
        for event in telemetry:
            if self.evaluate_event(rule, event):
                matched.append(event)
                
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        coverage = len(matched) / max(1, len(telemetry))
        return matched, duration_ms, coverage
